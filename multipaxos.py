from network import Network
from utils import TIMEOUT
import threading
import time
from blockchain import Blog
from utils import *

class MultiPaxos:
	def __init__(self, net, pid, blog):
		self.net = net
		self.pid = pid
		self.blog = blog
		self.leader = None
		self.queue = []

		self.ballot_num = [0,0,0]		# Depth, Num, Pid
		self.accept_val = None
		self.accept_num = None
		
		self.process_lock = threading.Lock()

		self.promises = 0
		self.acceptances = 0
		self.heartbeats = set()

		threading.Thread(target=self.handleMessages).start()
		threading.Thread(target=self.handleQueue).start()
		threading.Thread(target=self.handleRecieve).start()

	def incrementBallot(self):
		self.ballot_num[1] += 1
		self.ballot_num[2] = self.pid
	def incrementDepth(self):
		self.ballot_num[0]+=1
		self.accept_num = None
		self.accept_val = None

	def addToQueue(self, val):
		self.queue.append(val)

	def checkHeartbeat(self, dest):
		if dest == self.pid:
			return True		# just to keep other logic clean, and save messages
		self.heartbeats-={dest}
		self.net.send(dest, ("PING",))
		debug(self.pid, "send PING to", dest)
		start_time = time.time()
		while time.time() < start_time() + TIMEOUT:
			if dest in self.heartbeats:
				break
		return dest in self.heartbeats

	def updateHeartbeat(self, sender):
		self.heartbeats |= {sender}

	def handleQueue(self):
		while True:
			time.sleep(.1)
			if self.leader == self.pid and self.queue:
				# with self.process_lock:
				if self.accept() == True:
					print('DECIDED')
					print("accepted!")
					self.decide()

	def handleRecieve(self):
		while True:
			if not isDebug():
				time.sleep(3)

			content,sender = self.net.pop_recv_message()
			match content[0]:
				case "PROMISE":
					self.recieve_promise(content, sender)
				case "ACCEPTED":
					self.recieve_accepted(content, sender)
				case _:
					error(self.pid,"Unknown message recieved:",content,"from",sender)


	def handleMessages(self):
		while True:
			if not isDebug():
				time.sleep(3)
			
			if self.leader == self.pid and self.queue and self.accept_val == None:
				...

			content,sender = self.net.pop_message()
			# with self.process_lock:
			match content[0]:
				case "PREPARE":
					self.promise(content, sender)
				case "PROMISE":
					self.recieve_promise(content, sender)
					error(self.pid, "should not be in this queue")
				case "ACCEPT":
					self.accepted(content, sender)
				case "ACCEPTED":
					self.recieve_accepted(content, sender)
					error(self.pid, "should not be in this queue")
				case "PING":
					self.net.send(sender, ("PONG",))
				case "PONG":
					self.updateHeartbeat(sender)
				case "ENQUEUE":
					self.addToQueue(content[1])
				case "DECIDE":
					print("CONTENT",content)
					self.blog.add(*content[1])
				case _:
					error(self.pid,"Unknown message recieved:",content,"from",sender)
			# note this is not the only place promises are handled

	def prepare(self):
		"""
		broadcast prepare messages to elect leader
		can be used like while mp.prepare() == False: print("retrying")
		"""
		# TODO: handle if leader exists
		self.incrementBallot()

		self.promises = 0
		self.net.broadcast(("PREPARE", self.ballot_num))
		debug(self.pid, "broadcast PREPARE", self.ballot_num, level = 1)
		
		start_time = time.time()
		while time.time() <= start_time + TIMEOUT:
			if self.promises >= 3:
				break
		if self.promises < 3:
			debug(self.pid,"- NOT ENOUGH PROMISES (",self.promises,")")
			return False
		else:
			debug(self.pid,"became leader")
			self.leader = self.pid
			return True

	def promise(self, content, sender):
		"send promise messages back to leader"
		if self.ballot_num <= content[1]:
			self.ballot_num = content[1]
			if sender != self.pid:
				self.leader = None
				self.acceptances = -5
				self.promises = -5
				while self.queue:
					self.net.send(sender,("ENQUEUE",self.queue.pop(0)))
			self.net.send(sender, ("PROMISE", self.accept_val, self.accept_num))
			debug(self.pid, "PROMISE to", sender, self.accept_val, self.accept_num, level = 1)
			
	def recieve_promise(self, content, sender):
		"receive promise messages from the leader election phase"
		self.promises += 1
		if self.accept_num is None or (content[2] is not None and self.accept_num < content[2]):
			self.accept_val, self.accept_num = content[1:]
		debug("received PROMISE", self.ballot_num, "of", self.promises, level = 1)

	def accept(self, add_val=None):
		"broadcast accept message with value"
		if add_val is not None:
			self.queue.append(add_val)
		if self.leader == self.pid:
			assert self.accept_val or self.queue, "calling accept but no value to propose" 
			val = self.accept_val or self.queue.pop(0)
			self.acceptances = 0
			self.net.broadcast(("ACCEPT", val, self.ballot_num))

			start_time = time.time() 
			while time.time() <= start_time + TIMEOUT:
				if self.acceptances >= 3:
					break
			if self.acceptances < 3:
				debug(self.pid,"- NOT ENOUGH ACCEPTANCES (",self.acceptances,")")
				# self.queue.insert(0, val) # message just gets lost
				return False
			else:
				debug(self.pid,"was accepted")
				return True
		else:
			error(self.pid, "IS NOT LEADER,", self.leader, "IS")
			return False
	
	def accepted(self, content, sender):
		"send accepted message back to leader"
		if self.ballot_num <= content[2]:
			self.ballot_num = content[2]

			if self.leader != sender:
				self.leader = sender
				self.acceptances = -5
				self.promises = -5

			self.accept_num = self.ballot_num
			self.accept_val = content[1]
			self.net.send(sender, ("ACCEPTED",self.ballot_num))
			debug(self.pid, "ACCEPTED", self.ballot_num, "of",sender,level = 1)
		else:
			debug(self.pid, "not ACCEPTED, I have higher ballot number", self.ballot_num, content[2], level = 1)
	
	def decide(self):
		self.net.broadcast(("DECIDE",self.accept_val, self.accept_num))
		debug(self.pid, "broadcast DECIDE with", self.accept_val, self.accept_num, level = 1)

	def push_value(self, val):
		if self.leader == None or self.checkHeartbeat(self.leader) == False:
			if self.prepare() == False:
				return False		# wasn't able to be leader, tell owner to retry
		# some leader is defined right now
		if self.leader == self.pid:
			self.addToQueue(val)
		elif self.leader != self.pid:
			# send to leader's queue
			self.net.send(self.leader, ("ENQUEUE", val))
		else:
			error("THIS SHOULD NOT HAPPEN")
		return True

	def recieve_accepted(self, content, sender):
		debug(self.pid, "maybe ACCEPTED from",str(sender)+", now at",self.acceptances, level = 1)
		if self.ballot_num == content[1]:
			self.acceptances += 1
			debug(self.pid, "recieved ACCEPTED from",str(sender)+", now at",self.acceptances, level = 1)

	def __str__(self):
		out = '[\n'
		
		out += f'\tPID: {self.pid}\n'
		out += f'\tLeader: {self.leader}\n'
		out += f'\tQueue: {self.queue}\n'
		out += f'\tBallot Num: {self.ballot_num}\n'
		out += f'\tAccept Val: {self.accept_val}\n'
		out += f'\tAccept Num: {self.accept_num}\n'
		out += f'\tNum Promises: {self.promises}\n'
		out += f'\tNum Acceptances: {self.acceptances}\n'
		out += f'\tHeartbeats: {self.heartbeats}\n'

		out += ']'
		return out


if __name__ == "__main__":
	mp = MultiPaxos(Network(0), 0, Blog())
	print(mp)
		
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
		
		self.promises = 0
		self.acceptances = 0
		self.heartbeats = set()

		threading.Thread(target=self.handleMessages).start()

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
		self.heartbeats-={dest}
		self.net.send(dest, ("PING",))
		start_time = time.time()
		while time.time() < start_time() + TIMEOUT:
			if dest in self.heartbeats:
				break
		return dest in self.heartbeats

	def updateHeartbeat(self, sender):
		self.heartbeats|={sender}

	def handleMessages(self):
		while True:
			time.sleep(.01 if isDebug() else 3)

			content,sender = self.net.pop_message()
			match content[0]:
				case "PREPARE":
					self.promise(content, sender)
				case "PROMISE":
					self.recieve_promise(content, sender)
				case "ACCEPT":
					self.accepted(content, sender)
				case "ACCEPTED":
					self.recieve_accepted(content, sender)
				case "PING":
					self.net.send(sender, ("PONG",))
				case "PONG":
					self.updateHeartbeat(sender)
				case "ENQUEUE":
					self.addToQueue(content[1])
				case _:
					error(self.pid,"Unknown message recieved:",content,"from",sender)

	def prepare(self):
		"""
		broadcast prepare messages to elect leader
		can be used like while mp.prepare() == False: print("retrying")
		"""
		# TODO: handle if leader exists
		self.incrementBallot()

		self.promises = 0
		self.net.broadcast(("PREPARE", self.ballot_num))
		
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
			self.leader = None
			while self.queue:
				self.net.send(sender,("ENQUEUE",self.queue.pop(0)))
			self.net.send(sender, ("PROMISE", self.accept_val, self.accept_num))
			
	def recieve_promise(self, content, sender):
		"receive promise messages from the leader election phase"
		self.promises += 1
		if self.accept_num is None or (content[2] is not None and self.accept_num < content[2]):
			self.accept_val, self.accept_num = content[1:]

	def accept(self, add_val=None):
		"broadcast accept message with value"
		if self.leader == self.pid:
			if add_val is not None:
				self.queue.append(add_val)
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
				# self.queue()
				return False
			else:
				debug(self.pid,"was accepted")
				self.leader = self.pid
				return True
		else:
			if self.leader is not None and self.checkHeartbeat(self.leader):
				...
			else:
				self.prepare()
				self.accept()
				return False
		
	
	def accepted(self, content, sender):
		"send accepted message back to leader"
		if self.ballot_num <= content[2]:
			self.ballot_num = content[2]
			self.accept_num = self.ballot_num
			self.accept_val = content[1]
			self.net.broadcast(("ACCEPTED",self.ballot_num))

	def recieve_accepted(self, content, sender):
		if self.ballot_num == content[1]:
			self.acceptances += 1
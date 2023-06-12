from network import Network
from utils import TIMEOUT
import threading
import time
from blockchain import Blog
from utils import *
from colorama import Fore, Back
from colorama import Style
colors = [eval(f"Fore.{x.upper()}") for x in ("cyan", "green", "yellow", "blue", "magenta", "white")]

class MultiPaxos:
	def __init__(self, net, pid, blog, debug_print = False, use_queue = True):
		self.net = net
		self.pid = pid
		self.blog = blog
		self.leader = None

		self.queue = []
		self.queueLock = threading.Lock()
		self.use_queue = use_queue

		self.isDebug = debug_print or isDebug()
		self.TIMEOUT = 0.5 if self.isDebug else 3

		self.ballot_num = [0,0,0]		# Depth, Num, Pid
		self.accept_num = None
		self.accept_val = None
		
		self.promises = 0
		self.acceptances = 0
		self.heartbeats = set()
		self.caughtup = False
		self.in_catchup = None

		threading.Thread(target=self.handleQueue).start()
		threading.Thread(target=self.handleMessages).start()
		threading.Thread(target=self.handleReceives).start()

	def debug(self, *args, **kwargs):
		if self.isDebug:
			print(f"{Fore.RED}[DEBUG - {self.pid}]:{Style.RESET_ALL}",Style.DIM+colors[self.pid],*args, **kwargs,end=f"{Style.RESET_ALL}\n")

	def addQueue(self, val):
		with self.queueLock:
			self.queue.append(val)
			self.debug("adding",val,"to queue", self.queue)
	def popQueue(self):
		with self.queueLock:
			self.debug("popping from queue", self.queue)
			return self.queue.pop(0)

	def incrementBallot(self):
		self.ballot_num[1] += 1
		self.ballot_num[2] = self.pid
	def incrementDepth(self):
		self.ballot_num[0]+=1
		self.ballot_num[1]=0
		self.ballot_num[2]=0
		self.accept_num = None
		self.accept_val = None

	def handleQueue(self):
		while self.use_queue:
			if self.queue:
				if self.leader == self.pid:
					self.accept() and self.decide()
				elif self.leader is None or self.checkHeartbeat(self.leader) == False:
					self.prepare() and self.accept() and self.decide()
				else:
					self.net.send(self.leader, ("ENQUEUE", self.ballot_num, self.popQueue()))
			time.sleep(.1)

	def handleReceives(self):
		while True:
			if not self.isDebug:
				time.sleep(3)
			content,sender = self.net.pop_recv_message()
			if content[1][0] == self.ballot_num[0] or content[0] in ("QUERY","DATA"):
				self.debug("received",content, sender)
				match content[0]:
					case "PROMISE":
						self.receive_promise(content, sender)
					case "ACCEPTED":
						self.receive_accepted(content, sender)
					case "DECIDE":
						self.receive_decide(content, sender)
					case "PING":
						self.pong(content, sender)
					case "PONG":
						self.receive_pong(content, sender)
					case "QUERY":
						self.data(content, sender)
					case "DATA":
						self.receive_data(content, sender)
					case _:
						error(self.pid,"Unknown message received:",content,"from",sender)
			elif content[1][0] < self.ballot_num[0]:
				# they are behind
				self.net.send(sender, ("OUTDATED", self.ballot_num))
			else:
				# we are behind
				self.in_catchup = (content, sender)

	def handleMessages(self):
		while True:
			if not self.isDebug:
				time.sleep(3)
			if self.in_catchup:
				self.catchup(*self.in_catchup)

			content,sender = self.net.pop_message()
			self.debug("received",content, sender)
			if content[1][0] == self.ballot_num[0] or content[0] in ("OUTDATED",):
				match content[0]:
					case "PREPARE":
						self.promise(content, sender)
					case "ACCEPT":
						self.accepted(content, sender)
					case "ENQUEUE":
						self.addQueue(content[2])
					case "OUTDATED":
						self.in_catchup = (content, sender)
					case _:
						error(self.pid,"Unknown message received:",content,"from",sender)
			elif content[1][0] < self.ballot_num[0]:
				# they are behind
				self.debug("receieved outdated message", content, sender)
				self.net.send(sender, ("OUTDATED", self.ballot_num))
			else:
				# we are behind
				self.in_catchup = (content, sender)

	def data(self, content, sender):
		assert len(self.blog.blocks)>content[2]
		self.net.send(sender, ("DATA", self.ballot_num, self.blog.blocks[content[2]].T))

	def receive_data(self, content, sender):
		self.debug("recieved data", content, sender)
		# assert self.ballot_num[0] == content[1][0], "received data for wrong ballot num"
		self.blog.add(content[2].OP, content[2].username, content[2].title, content[2].content)
		self.incrementDepth()
		self.caughtup = True

	def catchup(self, content, sender):
		self.debug("STARTING CATCHUP", content, sender)
		assert self.in_catchup is not None, "wasn't instructed to enter"
		while self.ballot_num[0] < content[1][0]:
			self.debug("catching up - ", self.ballot_num[0], " -> ", content[1][0])
			self.caughtup = False
			self.net.send(sender, ("QUERY", self.ballot_num, self.ballot_num[0]))
			start_time = time.time()
			while time.time() < start_time + 3 and self.caughtup == False:
				time.sleep(.1)
		self.in_catchup = None
		self.debug("ALL CAUGHT UP")

	def pong(self, content, sender):
		# maybe check depth / ballot num?
		if self.leader == self.pid:
			self.net.send(sender, ("PONG", self.ballot_num))

	def receive_pong(self, content, sender):
		self.heartbeats |= {sender}

	def checkHeartbeat(self, target):
		self.heartbeats -= {target}
		self.net.send(target, ("PING", self.ballot_num))
		start_time = time.time()
		while time.time() < start_time + self.TIMEOUT:
			if target in self.heartbeats: break
			time.sleep(.1)
		return target in self.heartbeats

	def prepare(self):
		self.debug("prepare")
		# assume we are leader for now
		self.incrementBallot()
		self.promises = 0
		self.net.broadcast(("PREPARE", self.ballot_num))
		start_time = time.time()
		while time.time() < start_time + self.TIMEOUT:
			if self.promises >= 3: break
			time.sleep(.1)
		if self.promises >= 3:
			self.debug("Became Leader")
			self.leader = self.pid
			return True
		else:
			self.debug("Couldn't become leader")
			self.leader = None
			return False

	def promise(self, content, sender):
		# ignore depth for now
		# self.debug(f"{content[1]=} >= {self.ballot_num=}", content[1] >= self.ballot_num)
		if content[1] >= self.ballot_num:
			self.ballot_num = content[1]
			self.net.send(sender, ("PROMISE", self.ballot_num, self.accept_num, self.accept_val))
			if sender != self.pid:
				for message in self.queue:
					self.net.send(sender, ("ENQUEUE", self.ballot_num, message))
				with self.queueLock:
					self.queue = []

	def receive_promise(self, content, sender):
		self.debug("recv promise", content, sender, self.ballot_num)
		if content[1] == self.ballot_num:
			self.promises += 1
			if content[2] is not None:
				# ignore depth for now
				if (self.accept_num is None) or (self.accept_num < content[2]):
					self.debug("override accept_val from", self.accept_val, "to", content[3])
					self.accept_num = content[2]
					self.accept_val = content[3]
		else:
			error(self.pid,"RECEIVED PROMISE FOR DIFFERENT BALLOT NUM:",self.ballot_num,"=/=", content[1])

	def accept(self):
		self.debug("accept")
		if self.accept_val is None and self.queue == []:
			error(self.pid, 'accepting with no values')
			return False
		if self.accept_val is None:
			self.accept_val = self.popQueue()
		self.acceptances = 0
		self.net.broadcast(("ACCEPT", self.ballot_num, self.accept_val))

		start_time = time.time()
		while time.time() < start_time + self.TIMEOUT:
			if self.acceptances >= 3: break
			time.sleep(0.1)
			
		if self.acceptances >= 3:
			return True
		else:
			self.debug("Accept failed, no longer leader")
			self.leader = None
			return False
	
	def accepted(self, content, sender):
		# ignore depth for now
		if content[1] >= self.ballot_num:
			self.leader = sender
			self.accept_num = content[1]
			self.accept_val = content[2]
			self.net.send(sender, ("ACCEPTED", self.ballot_num, self.accept_num, self.accept_val))
	
	def receive_accepted(self, content, sender):
		if self.leader != self.pid:
			error("Received accepted, not leader")
			return False
		if content[2] == self.ballot_num:
			self.acceptances += 1
		else:
			error("ACCEPTANCE WITH WRONG BALLOT NUM")

	def decide(self):
		# ignore depth for now
		self.net.broadcast(("DECIDE", self.ballot_num, self.accept_val))

	def receive_decide(self, content, sender):
		self.blog.add(*content[2])
		self.incrementDepth()

	def __repr__(self):
		out = '['
		out += f'PID: {self.pid}, '
		out += f'Leader: {self.leader}, '
		out += f'Ballot Num: {self.ballot_num}, '
		out += f'Accept Val: {self.accept_val}, '
		out += f'Accept Num: {self.accept_num}'

		out += ']'
		return out

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
	print(repr(mp))
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

		self.ballot_num = [0,0,0]		# Depth, Num, Pid
		self.accept_val = None
		self.accept_num = None
		
		self.promises = 0
		self.queue = []

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
			self.net.send(sender, ("PROMISE", self.accept_num, self.accept_val))
			
	def recieve_promise(self, content, sender):
		"receive promise messages from the leader election phase"
		self.promises += 1
		if self.accept_num and self.accept_num < content[2]:
			self.accept_val, self.accept_num = content[1:]

	def accept(self):
		"broadcast accept message with value"
		assert self.accept_val or self.queue, "calling accept but no value to propose" 
		val = self.accept_val or self.queue.pop(0)
		
		self.net.broadcast(("ACCEPT", val, self.ballot_num))
	
	def accepted(self, content, sender):
		"send accepted message back to leader"
		if self.ballot_num < content[2]:
			self.ballot_num = content[0]
			self.net.broadcast(("ACCEPTED",))

	
if __name__ == "__main__":
	b0 = Blog()
	mp0 = MultiPaxos(Network(0), 0, b0)
	b1 = Blog()
	mp1 = MultiPaxos(Network(1), 1, b1)
	b2 = Blog()
	mp2 = MultiPaxos(Network(2), 2, b2)
	mp0.prepare()
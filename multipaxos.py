from network import Network
from utils import TIMEOUT
import threading
import time
from blockchain import Blog
from utils import *

class MultiPaxos:
	def __init__(self, net, pid, blog, disable_queue = False):
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
		threading.Thread(target=self.handlereceive).start()
		if not disable_queue:
			threading.Thread(target=self.handleQueue).start()

	def incrementBallot(self):
		self.ballot_num[1] += 1
		self.ballot_num[2] = self.pid
	def incrementDepth(self):
		self.ballot_num[0]+=1
		self.accept_num = None
		self.accept_val = None

	def handleMessages(self):
		while True:
			if not isDebug():
				time.sleep(3)
			
			content,sender = self.net.pop_message()
			match content[0]:
				case "PREPARE":
					self.promise(content, sender)
				case _:
					error(self.pid,"Unknown message received:",content,"from",sender)

	def prepare(self):
		...

	def promise(self, content, sender):
		...	

	def receive_promise(self, content, sender):
		...

	def accept(self, add_val=None):
		...
	
	def accepted(self, content, sender):
		...
	
	def receive_accepted(self, content, sender):
		...

	def decide(self):
		...

	def receive_decide(self, content):
		...

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
		
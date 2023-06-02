from network import Network
from constants import TIMEOUT
import threading
import time
from blockchain import Blog
from enum import Enum
from utils import *
import random

class States(Enum):
	INIT = 0
	BEHIND = 1
	ELECTION = 2
	PROPOSAL = 3
	DECISION = 4

class MultiPaxos:
	def __init__(self, net, pid, blog):
		self.net = net
		self.pid = pid
		self.blog = blog

		self.state = States.INIT

		self.leader = None
		self.ballot_num = [0,0,0]
		self.accept_val = None
		self.accept_num = None
		self.responses = None
		self.val = None

		self.flag = None

		threading.Thread(target=self.handleMessages).start()
	
	def incrementBallotNum(self):
		self.ballot_num[1]+=1
		self.ballot_num[2]=self.pid

	def incrementDepth(self):
		self.ballot_num[0]+=1
		self.ballot_num[2]=self.pid

	def handleMessages(self):
		while True:
			content,sender = self.net.pop_message()
			command = content[0]
			match command:
				case "PING":
					bn = content[1]
					if bn[0] < self.ballot_num[0]:
						self.net.send(sender, ("OUTDATED", self.ballot_num))
					elif bn[0] > self.ballot_num[0]:
						self.state = States.BEHIND
						self.catchup(bn)
					else:
						self.net.send(sender, ("PONG", self.ballot_num))
				case "PONG":
					assert self.flag == False,  f"flag is not false ({self.flag})"
					self.flag = True
				case "OUTDATED":
					...
				case _:
					error(self.pid, "unknown command", content, 'from', sender)

			debug((self.pid),"handleMessages got", content,sender)
	
	def catchup(self, bn):
		while self.ballot_num[0] < bn[0]:
			# catchup here
			...

	def validate_leader(self):
		# Function should result in self.leader being a valid leader, either self or someone else
		if self.leader is not None:
			assert self.flag == None, f"flag already in use ({self.flag})"
			self.flag = False
			self.net.send(self.leader, ("PING", self.ballot_num))
			
			start_time = time.time()
			while time.time() <= start_time + TIMEOUT:
				if self.flag == True: break
				time.sleep(.1)
			if self.flag == False:
				# Existing leader did not send heartbeat
				self.leader = None
		
		if self.leader == None and self.state != States.BEHIND:
			# we try to elect ourselves
			...
			
	def __str__(self):
		return str(self.pid)
	
	
if __name__ == "__main__":
	b0 = Blog()
	mp0 = MultiPaxos(Network(0), 0, b0)
	b1 = Blog()
	mp1 = MultiPaxos(Network(1), 1, b1)
	b2 = Blog()
	mp2 = MultiPaxos(Network(2), 2, b2)
	mp0.prepare()
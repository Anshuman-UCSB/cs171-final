from network import Network
from constants import TIMEOUT
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
		self.ballot_num = [0,0,0]
		self.accept_val = None
		self.accept_num = None
		self.responses = None
		self.val = None
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
			if content[0] == "PREPARE":
				self.promise(content[1])
			elif content[0] == "PROMISE":
				self.responses+=1
			elif content[0] == "CATCHUP":
				bc = content[1].T
				self.blog.add(bc.OP, bc.username, bc.title, bc.content)
				self.responses = -3 # makes it impossible to get majority
				self.incrementDepth()
			elif content[0] == "ACCEPT":
				self.accepted(content[2], 0)
			elif content[0] == "ACCEPTED":
				...
			elif content[0] == "DECIDE":
				# add entry to blockchain
				bc = content[1].T
				self.blog.add(bc.OP, bc.username, bc.title, bc.content)
				...
			
			print((self.pid),"handleMessages got", content,sender)
	
	def catchup(self,ballot_num):
		assert self.ballot_num[0] > ballot_num[0], "calling catchup when not deeper?"
		self.net.send(ballot_num[2], ("CATCHUP", self.blog.blocks[ballot_num[0]]))

	def prepare(self):
		if self.leader is None:
			self.incrementBallotNum()
			print(self.pid,"broadcasting PREPARE",self.ballot_num)
			self.net.broadcast(("PREPARE",self.ballot_num))
			self.responses = 0
			start_time = time.time()
			while time.time() <= TIMEOUT + start_time:
				if self.responses >= 3: break
			if self.responses >= 3:
				self.leader = self.pid
				# self.accept(vals, new_val)
			else:
				print("COULDN'T GET LEADER")
				self.prepare()
		else:
			...
			# ask leader for heartbeat

	def promise(self, ballot_num):
		if ballot_num[0] < self.ballot_num[0]:
			self.catchup(ballot_num)
		elif ballot_num >= self.ballot_num:
			self.ballot_num = ballot_num
			pid = ballot_num[2]
			self.net.send(pid, ("PROMISE", ballot_num, self.accept_num, self.accept_val))
	
	def accept(self, ballot_nums, vals):
		if vals != []:
			max_ballot = max(ballot_nums)
			pid = ballot_nums.index(max_ballot)
			max_value = vals[pid]
			
			self.val = max_value
			self.ballot_num = max_ballot
		self.net.broadcast(("ACCEPT", self.ballot_num, self.val))
	
	def accepted(self, ballot_num, value):
		if ballot_num >= self.ballot_num:
			self.accept_num = ballot_num
			self.accept_val = value
			pid = ballot_num[2]
			self.net.send(pid, ("ACCEPTED", ballot_num, value))

	def decide(self):
		self.net.broadcast(("DECIDE", self.val))

	def propose_value(self):
		if self.leader == self.pid:
			...
		else:
			# send message to leader to propose value
			...
	
	
if __name__ == "__main__":
	b0 = Blog()
	mp0 = MultiPaxos(Network(0), 0, b0)
	b1 = Blog()
	mp1 = MultiPaxos(Network(1), 1, b1)
	b2 = Blog()
	mp2 = MultiPaxos(Network(2), 2, b2)
	mp0.prepare()
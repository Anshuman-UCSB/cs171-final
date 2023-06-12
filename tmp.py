import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys

mp = [MultiPaxos(Network(i), i, Blog(),debug_print=True) for i in range(5)]
mp[0].addQueue(("POST", "user", "title 1", "cont"))
mp[0].addQueue(("POST", "user", "title 2", "cont"))
mp[0].addQueue(("POST", "user", "title 3", "cont"))
while mp[0].ballot_num[0] < 3:
	time.sleep(.05)
for i in range(1,5):
	mp[i] = MultiPaxos(Network(i), i, Blog(),debug_print=True)
mp[0].addQueue(("COMMENT", "comment", "title 2", "cmnt"))
time.sleep(1)
for i in range(1,4):
	assert mp[0].blog.blocks == mp[i].blog.blocks, i
print("DONE")
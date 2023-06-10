import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys


mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
q = [("POST","user", "title", f"message content {i}") for i in range(5)]
for m in q:
	mp[0].addToQueue(m)
assert mp[0].queue == q
mp[2].prepare()
time.sleep(.1)
assert mp[2].leader == 2
assert mp[2].queue == q
assert mp[0].queue == []

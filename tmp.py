import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys


mp = [MultiPaxos(Network(i), i, Blog(),debug_print=True) for i in range(5)]
for i in range(5):
	mp[3].net.fail_link(i)
assert any(mp[3].net.canSend) == False
assert mp[0].net.canSend == [True, True, True, False, True]
time.sleep(.1)
mp[0].addQueue(("POST", "user", "titl", "cont"))
while mp[0].ballot_num[0] < 1:
	time.sleep(.1)
for i in range(5):
	mp[3].net.fix_link(i)
assert mp[0].ballot_num[0] == 1
assert mp[3].ballot_num[0] == 0

mp[3].prepare()
time.sleep(.3)
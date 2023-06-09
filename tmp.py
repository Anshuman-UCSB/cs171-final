import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys


mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
mp[0].prepare()
time.sleep(.1)
assert mp[0].leader == 0

mp[0].addToQueue(("POST","user", "title", "message content"))
print(mp[0].acceptances)
assert mp[0].acceptances >= 3
print(mp[0].acceptances)
assert mp[1].accept_num == mp[0].ballot_num
assert mp[3].accept_val == ("POST","user", "title", "message content")
print("DONE")

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

mp[0].addToQueue(("POST","user", "title", "test_accept_fresh_value"))
time.sleep(1)
assert mp[0].acceptances >= 3
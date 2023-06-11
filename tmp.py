import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys


mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True) for i in range(5)]
mp[0].prepare()
print(mp[0].ballot_num)
time.sleep(.2)
assert mp[0].leader == 0
# mp[0].queue.append("value")
# mp[0].accept()
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys

mp = [MultiPaxos(Network(i), i, Blog(),use_snapshot=True,debug_print=True) for i in range(5)]
# mp[0].addQueue(("POST", "user", "title 1", "cont"))
# mp[0].addQueue(("POST", "user", "title 2", "cont"))

# time.sleep(2)
# mp[0].save_state()
mp[0].load_state()
print(mp[0].blog.blocks)
mp[0].blog.blockchain()
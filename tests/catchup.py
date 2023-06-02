import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog

import time

mps = [MultiPaxos(Network(i), i, Blog()) for i in range(3)]
mps[0].blog.add("POST","me","title","this is content")
mps[0].blog.add("COMMENT","notme","title","this is comment")
time.sleep(.5)
mps[0].ballot_num = [2,2,0]
mps[1].prepare()

time.sleep(1)
print(mps[1].blog)
assert(len(mps[1].blog.blocks) == 2)
print(mps[1].ballot_num)
assert mps[1].ballot_num==[2,3,1]
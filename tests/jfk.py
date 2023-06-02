import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog

import time

mps = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
mps[0].net.failLink(4)
time.sleep(1)
mps[0].prepare()
for m in mps:
	m.leader = 0
for i in mps:
	print(f"{i}\'s leader:" , i.leader)
mps[4].prepare()
for i in mps:
	print(f"{i}\'s leader:" , i.leader)
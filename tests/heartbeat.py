import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog

import time

mps = [MultiPaxos(Network(i), i, Blog()) for i in range(3)]
mps[0].validate_leader()
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys

networks = [Network(i) for i in range(5)]
networks[4].fail_link(2)
networks[2].broadcast("message")
time.sleep(.1)
for i in range(4):
	assert networks[i].pop_message() == ("message",2)
assert len(networks[4].messages)==0
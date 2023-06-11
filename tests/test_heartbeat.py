import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 0

class TestHeartbeat:
		
	def test_success(self):
		mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True) for i in range(5)]
		mp[0].leader = 0
		assert mp[2].checkHeartbeat(0) == True
	def test_fail(self):
		mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True) for i in range(5)]
		mp[0].leader = None
		assert mp[2].checkHeartbeat(0) == False

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
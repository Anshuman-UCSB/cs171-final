import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 0

class TestMultiPaxos3:
	def setup_method(self):
		sys.argv.append("debug")
		sys.argv.append(str(debugLevel))
	def teardown_method(self):
		assert sys.argv.pop(-1) == str(debugLevel)
		assert sys.argv.pop(-1) == "debug"

	def test_transfer_queue(self):
		...
		
	def test_accept_somehow(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		
		...

	def test_simple_decide(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		
		assert mp[0].prepare() == True
		mp[0].addToQueue(("POST","user", "title", "test_simple_decide"))
		time.sleep(.5)
		for i in range(5):
			assert mp[i].accept_val == ("POST","user", "title", "test_simple_decide"), f"{i} failed"
		time.sleep(.5)
		assert len(mp[0].blog.blocks) == 1

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
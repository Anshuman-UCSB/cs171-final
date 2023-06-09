import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 1

class TestNetwork(unittest.TestCase):
	def setUp(self):
		sys.argv.append("debug")
		sys.argv.append(str(debugLevel))
	def tearDown(self):
		assert sys.argv.pop(-1) == str(debugLevel)
		assert sys.argv.pop(-1) == "debug"

	def test_failLink(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		assert all(mp[0].net.canSend) == True
		mp[0].net.failLink(2)
		time.sleep(.1)
		assert mp[0].net.canSend == [True, True, False, True, True]
		time.sleep(.1)
		assert mp[2].net.canSend == [False, True, True, True, True]
		mp[1].net.failLink(0)
		time.sleep(.1)
		assert mp[0].net.canSend == [True, False, False, True, True]
		mp[0].net.failLink(0)
		time.sleep(.1)
		assert mp[0].net.canSend == [False, False, False, True, True]

	def test_fixlink(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		assert all(mp[0].net.canSend) == True
		mp[0].net.failLink(2)
		time.sleep(.1)
		assert mp[0].net.canSend == [True, True, False, True, True]
		time.sleep(.1)
		assert mp[2].net.canSend == [False, True, True, True, True]
		mp[1].net.failLink(0)
		time.sleep(.1)
		assert mp[0].net.canSend == [True, False, False, True, True]
		mp[0].net.failLink(0)
		time.sleep(.1)
		assert mp[0].net.canSend == [False, False, False, True, True]

		mp[0].net.fixLink(1)
		time.sleep(.1)
		assert mp[0].net.canSend == [False, True, False, True, True]
		mp[0].net.fixLink(0)
		time.sleep(.1)
		assert mp[0].net.canSend == [True, True, False, True, True]
		mp[2].net.fixLink(0)
		time.sleep(.1)
		assert mp[0].net.canSend == [True, True, True, True, True]
		assert mp[2].net.canSend == [True, True, True, True, True]
		
class TestMultiPaxos(unittest.TestCase):

	def setUp(self):
		sys.argv.append("debug")
		sys.argv.append(str(debugLevel))
	def tearDown(self):
		assert sys.argv.pop(-1) == str(debugLevel)
		assert sys.argv.pop(-1) == "debug"

	def test_defaults(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		for i in range(5):
			assert mp[i].pid==i
			assert mp[i].ballot_num == [0,0,0]
			assert mp[i].accept_num == None
			assert mp[i].accept_val == None

	def test_5_promises(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		assert mp[2].promises == 0
		mp[2].prepare()
		time.sleep(.1)
		assert mp[2].promises == 5
		assert mp[2].leader == 2
		
	def test_3_promises(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[2].net.failLink(1)
		mp[2].net.failLink(4)
		assert mp[2].promises == 0
		time.sleep(.1)
		mp[2].prepare()
		time.sleep(.1)
		assert mp[2].promises == 3
		assert mp[2].leader == 2

	def test_2_promises(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[4].net.failLink(1)
		mp[4].net.failLink(3)
		mp[4].net.failLink(4)
		assert mp[4].promises == 0
		time.sleep(.1)
		mp[4].prepare()
		time.sleep(.1)
		assert mp[4].promises == 2
		assert mp[4].leader == None

	def test_newer_leader(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		assert mp[2].promises == 0
		mp[0].prepare()
		time.sleep(0.1)
		mp[4].prepare()
		time.sleep(0.1)
		assert mp[0].leader == 0
		assert mp[4].leader == 4

	def test_older_leader(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		assert mp[2].promises == 0
		mp[2].net.failLink(3)
		mp[3].prepare()
		time.sleep(0.1)
		mp[2].net.fixLink(3)
		mp[2].prepare()
		time.sleep(0.1)
		assert mp[3].leader == 3
		assert mp[2].leader == None

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 0

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
	
	def test_send_recv(self):
		networks = [Network(i) for i in range(5)]
		networks[4].send(2, "hello")
		networks[2].send(2, "world")
		assert networks[2].pop_message() == ("hello",4)
		assert networks[2].pop_message() == ("world",2)

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
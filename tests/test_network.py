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

	def test_send_recv(self):
		networks = [Network(i) for i in range(5)]
		networks[0].send(4, "hello")
		networks[2].send(4, 4)
		assert networks[4].pop_message() == ("hello", 0)
		assert networks[4].pop_message() == (4, 2)

	def test_fail_link(self):
		networks = [Network(i) for i in range(5)]
		networks[0].send(4, "hello")
		networks[2].fail_link(0)
		time.sleep(.1)
		assert networks[2].canSend == [False, True, True, True, True]
		assert networks[0].canSend == [True, True, False, True, True]
		networks[2].send(4, 4)
		assert networks[4].pop_message() == ("hello", 0)
		assert networks[4].pop_message() == (4, 2)

	def test_fix_link(self):
		networks = [Network(i) for i in range(5)]
		networks[0].send(4, "hello")
		networks[2].fail_link(0)
		time.sleep(.1)
		assert networks[2].canSend == [False, True, True, True, True]
		assert networks[0].canSend == [True, True, False, True, True]
		networks[2].send(4, 4)
		assert networks[4].pop_message() == ("hello", 0)
		assert networks[4].pop_message() == (4, 2)
		networks[0].fix_link(2)
		time.sleep(.1)
		assert networks[2].canSend == [True, True, True, True, True]
		assert networks[0].canSend == [True, True, True, True, True]

	def test_broadcast(self):
		networks = [Network(i) for i in range(5)]
		networks[4].fail_link(2)
		networks[2].broadcast("message")
		time.sleep(.1)
		for i in range(4):
			assert networks[i].pop_message() == ("message",2)
		assert len(networks[4].messages)==0
	
	def test_failed_message(self):
		networks = [Network(i) for i in range(5)]
		networks[0].fail_link(4)
		networks[4].send(0, ("PREPARE", [1,1,1]))
		assert len(networks[0].recvMessages) == 0
		
		
if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
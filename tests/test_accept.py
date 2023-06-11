import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 0

class TestAccept:

	# def setup_method(self):
	# 	sys.argv.append("debug")
	# 	sys.argv.append(str(debugLevel))
	# def teardown_method(self):
	# 	assert sys.argv.pop(-1) == str(debugLevel)
	# 	assert sys.argv.pop(-1) == "debug"
		
	def test_accept_success(self):
		mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True) for i in range(5)]
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0
		mp[0].queue.append("value")
		mp[0].accept()
		time.sleep(.1)
		assert mp[0].leader == 0
		assert mp[1].leader == 0
		assert mp[2].leader == 0
		assert mp[3].leader == 0
		assert mp[4].leader == 0
		
	def test_accept_fail(self):
		mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True) for i in range(5)]
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0
		mp[0].queue.append("value")
		mp[0].net.fail_link(2)
		mp[0].net.fail_link(3)
		mp[0].net.fail_link(4)
		assert mp[0].accept() == False
		assert mp[0].leader == None

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
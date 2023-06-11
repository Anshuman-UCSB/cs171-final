import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 0

class TestPrepare:

	def setup_method(self):
		sys.argv.append("debug")
		sys.argv.append(str(debugLevel))
	def teardown_method(self):
		assert sys.argv.pop(-1) == str(debugLevel)
		assert sys.argv.pop(-1) == "debug"
		
	def test_leader_success(self):
		mp = [MultiPaxos(Network(i), i, Blog(), use_queue=False) for i in range(5)]
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0
		assert mp[0].ballot_num == [0,1,0]
		
	def test_leader_fail(self):
		mp = [MultiPaxos(Network(i), i, Blog(), use_queue=False) for i in range(5)]
		mp[4].net.fail_link(0)
		mp[4].net.fail_link(3)
		mp[4].net.fail_link(2)
		mp[4].prepare()
		time.sleep(.1)
		assert mp[4].leader == None
		
	def test_leader_fail_ignored(self):
		mp = [MultiPaxos(Network(i), i, Blog(), use_queue=False) for i in range(5)]
		mp[4].net.fail_link(0)
		mp[4].prepare()
		time.sleep(.1)
		assert mp[4].leader == 4
		for i in range(5):
			print(mp[i])
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == None

	def test_no_accept_num(self):
		mp = [MultiPaxos(Network(i), i, Blog(), use_queue=False) for i in range(5)]
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].accept_num == None
		assert mp[0].accept_val == None

	def test_one_accept_num(self):
		mp = [MultiPaxos(Network(i), i, Blog(), use_queue=False) for i in range(5)]
		mp[3].accept_num = [0,2,3]
		mp[3].accept_val = "value"
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].accept_num == [0,2,3]
		assert mp[0].accept_val == "value"

	def test_two_accept_num(self):
		mp = [MultiPaxos(Network(i), i, Blog(), use_queue=False) for i in range(5)]
		mp[3].accept_num = [0,2,3]
		mp[3].accept_val = "value"
		mp[4].accept_num = [0,2,4]
		mp[4].accept_val = "overwritten"
		mp[0].net.fail_link(2)
		mp[0].net.fail_link(1)
		time.sleep(.1)
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].accept_num == [0,2,4]
		assert mp[0].accept_val == "overwritten"
		


if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog

debugLevel = 0

class TestCatchup:
	def test_catchup_simple(self):
		mp = [MultiPaxos(Network(i), i, Blog(),debug_print=True) for i in range(5)]
		for i in range(5):
			mp[3].net.fail_link(i)
		assert any(mp[3].net.canSend) == False
		assert mp[0].net.canSend == [True, True, True, False, True]
		time.sleep(.1)
		mp[0].addQueue(("POST", "user", "titl", "cont"))
		while mp[0].ballot_num[0] < 1:
			time.sleep(.1)
		for i in range(5):
			mp[3].net.fix_link(i)
		assert mp[0].ballot_num[0] == 1
		assert mp[3].ballot_num[0] == 0

		mp[3].prepare()
		time.sleep(.3)
		assert mp[3].ballot_num[0] == 1

	def test_catchup_proxy(self):
		mp = [MultiPaxos(Network(i), i, Blog(),debug_print=True) for i in range(5)]
		for i in range(5):
			mp[3].net.fail_link(i)
		assert any(mp[3].net.canSend) == False
		assert mp[0].net.canSend == [True, True, True, False, True]
		time.sleep(.1)
		mp[0].addQueue(("POST", "user", "titl", "cont"))
		while mp[0].ballot_num[0] < 1:
			time.sleep(.1)
		for i in range(5):
			mp[3].net.fix_link(i)
		assert mp[0].ballot_num[0] == 1
		assert mp[3].ballot_num[0] == 0

		mp[2].prepare()
		time.sleep(.2)
		assert mp[3].ballot_num[0] == 1

	def test_catchup_multuple(self):
		mp = [MultiPaxos(Network(i), i, Blog(),debug_print=True) for i in range(5)]
		for i in range(5):
			mp[3].net.fail_link(i)
		assert any(mp[3].net.canSend) == False
		assert mp[0].net.canSend == [True, True, True, False, True]
		time.sleep(.1)
		mp[0].addQueue(("POST", "user", "title 1", "cont"))
		mp[0].addQueue(("POST", "user", "title 2", "cont"))
		mp[0].addQueue(("POST", "user", "title 3", "cont"))
		while mp[0].ballot_num[0] < 3:
			time.sleep(.1)
		for i in range(5):
			mp[3].net.fix_link(i)
		assert mp[0].ballot_num[0] == 3
		assert mp[3].ballot_num[0] == 0

		mp[3].prepare()
		time.sleep(1)
		assert mp[3].ballot_num[0] == 3

	def test_victory_royale(self):
		mp = [MultiPaxos(Network(i), i, Blog(),debug_print=True) for i in range(5)]
		mp[0].addQueue(("POST", "user", "title 1", "cont"))
		mp[0].addQueue(("POST", "user", "title 2", "cont"))
		mp[0].addQueue(("POST", "user", "title 3", "cont"))
		while mp[0].ballot_num[0] < 3:
			time.sleep(.05)
		for i in range(1,5):
			mp[i] = MultiPaxos(Network(i), i, Blog(),debug_print=True)
		mp[0].addQueue(("COMMENT", "comment", "title 2", "cmnt"))
		time.sleep(1)
		for i in range(1,4):
			assert mp[0].blog.blocks == mp[i].blog.blocks, i

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 0

class TestMultiPaxos:

	def setup_method(self):
		sys.argv.append("debug")
		sys.argv.append(str(debugLevel))
	def teardown_method(self):
		assert sys.argv.pop(-1) == str(debugLevel)
		assert sys.argv.pop(-1) == "debug"
		
	def test_defaults(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		for i in range(5):
			assert mp[i].pid==i
			assert mp[i].ballot_num == [0,0,0]
			assert mp[i].accept_num == None
			assert mp[i].accept_val == None

	def test_simple_leader(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0

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
		assert mp[0].leader == None
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

	def test_two_leaders(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[0].net.failLink(3)
		mp[0].net.failLink(4)
		mp[4].net.failLink(1)
		time.sleep(.1)
		mp[0].prepare()
		assert mp[2].ballot_num == mp[0].ballot_num
		time.sleep(.1)
		mp[4].prepare()
		assert mp[0].leader == 0
		assert mp[4].leader == 4
		assert mp[2].ballot_num == mp[4].ballot_num


class TestMultiPaxos2:
	def setup_method(self):
		sys.argv.append("debug")
		sys.argv.append(str(debugLevel))
	def teardown_method(self):
		assert sys.argv.pop(-1) == str(debugLevel)
		assert sys.argv.pop(-1) == "debug"

	def test_accept_fresh_value(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0

		mp[0].addToQueue("sneep")
		assert mp[0].queue == ['sneep']
		assert mp[0].accept() == True
		time.sleep(.1)
		assert mp[0].acceptances == 5
		assert mp[1].accept_num == mp[0].ballot_num
		assert mp[3].accept_val == "sneep"

	def test_accept_failed(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[0].net.failLink(3)
		mp[0].net.failLink(4)
		time.sleep(.1)
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0
		mp[0].net.failLink(0)
		time.sleep(.1)

		mp[0].addToQueue("sneep")
		assert mp[0].queue == ['sneep']
		assert mp[0].accept()==False
		time.sleep(.1)
		assert mp[0].acceptances == 2

	def test_accept_twice(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[0].net.failLink(3)
		mp[0].net.failLink(4)
		time.sleep(.1)
		mp[0].prepare()
		mp[0].addToQueue("shmeep")
		mp[0].accept()
		time.sleep(.1)
		for i in range(3):
			assert mp[i].accept_val == "shmeep"
			assert mp[i].accept_num == [0,1,5,2]
		mp[4].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0
		assert mp[4].leader == 4

		mp[4].addToQueue("shmop")
		mp[4].accept()
		for i in range(5):
			assert mp[i].accept_val == "shmeep"
		for i in range(1,5):
			assert mp[i].accept_num == [0,1,4]

	def test_accept_twice_2(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[0].prepare()
		time.sleep(.1)
		mp[4].prepare()
		time.sleep(.1)
		mp[0].addToQueue("12")
		mp[0].accept()

	def test_accept_twice_fail(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		
		mp[0].net.failLink(1)

		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0
		# 0 is leader to all but 1
		
		mp[1].prepare()
		time.sleep(.1)
		assert mp[1].leader == 1

		mp[0].accept("will you go out with me")
		time.sleep(.1)
		for i in range(1,5):
			assert mp[i].accept_val == None
		assert mp[0].queue == ['will you go out with me']
		mp[1].net.fixLink(0)
		time.sleep(.1)
		mp[1].accept("what about me")
		time.sleep(.1)
		for i in range(5):
			assert mp[i].accept_val == "what about me"
		assert mp[i].queue == []

	def test_forward_queue(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		for i in range(5):
			mp[0].addToQueue(i)
		assert mp[0].queue == [0,1,2,3,4]


if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
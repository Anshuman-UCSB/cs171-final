import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 1

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

		mp[0].addToQueue(("POST","user", "title", "message content"))
		time.sleep(.5)
		assert mp[0].acceptances == 5
		assert mp[1].accept_num == mp[0].ballot_num
		assert mp[3].accept_val == ("POST","user", "title", "message content")

	def test_accept_failed(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[0].net.fail_link(3)
		mp[0].net.fail_link(4)
		time.sleep(.1)
		mp[0].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0
		mp[0].net.fail_link(0)
		time.sleep(.1)

		mp[0].addToQueue(("POST","user", "title", "message content"))
		assert mp[0].queue == [("POST","user", "title", "message content")]
		assert mp[0].accept()==False
		time.sleep(.1)
		assert mp[0].acceptances == 2

	def test_accept_twice(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		mp[0].net.fail_link(3)
		mp[0].net.fail_link(4)
		time.sleep(.1)
		mp[0].prepare()
		mp[0].addToQueue(("POST","user", "title", "message content"))
		mp[0].accept()
		time.sleep(.1)
		for i in range(3):
			assert mp[i].accept_val == ("POST","user", "title", "message content")
			assert mp[i].accept_num == [0,1,0]
		mp[4].prepare()
		time.sleep(.1)
		assert mp[0].leader == 0
		assert mp[4].leader == 4

		mp[4].addToQueue(("POST","wrong user", "title", "message content"))
		mp[4].accept()
		for i in range(5):
			assert mp[i].accept_val == ("POST","user", "title", "message content")
		for i in range(1,5):
			assert mp[i].accept_num == [0,1,4]

	def test_accept_twice_fail(self):
		mp = [MultiPaxos(Network(i), i, Blog()) for i in range(5)]
		
		mp[0].net.fail_link(1)

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
		assert mp[0].queue == []
		mp[1].net.fix_link(0)
		time.sleep(.1)
		mp[1].accept(("POST","user", "title", "message content"))
		time.sleep(.1)
		for i in range(5):
			assert mp[i].accept_val == ("POST","user", "title", "message content")
		assert mp[i].queue == []

	def test_forward_queue(self):
		mp = [MultiPaxos(Network(i), i, Blog(), disable_queue=True) for i in range(5)]
		q = [("POST","user", "title", f"message content {i}") for i in range(5)]
		for m in q:
			mp[0].addToQueue(m)
		assert mp[0].queue == q
		mp[2].prepare()
		time.sleep(.1)
		assert mp[2].leader == 2
		assert mp[2].queue == q
		assert mp[0].queue == []


if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
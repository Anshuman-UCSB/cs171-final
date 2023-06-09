import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys

class TestStringMethods(unittest.TestCase):

	def setUp(self):
		sys.argv.append("debug")
		sys.argv.append("0")
	def tearDown(self):
		assert sys.argv.pop(-1) == "0"
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
		time.sleep(1)
		assert mp[2].promises == 5
		assert mp[2].leader == 2
if __name__ == '__main__':
	unittest.main()
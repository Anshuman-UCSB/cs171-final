import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog

debugLevel = 0

class TestDecide:

	# def setup_method(self):
	# 	sys.argv.append("debug")
	# 	sys.argv.append(str(debugLevel))
	# def teardown_method(self):
	# 	assert sys.argv.pop(-1) == str(debugLevel)
	# 	assert sys.argv.pop(-1) == "debug"
		
	def test_decide_success(self):
		mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True, use_queue=False) for i in range(5)]
		mp[0].ballot_num = [0,8,1]
		mp[0].accept_val = ("POST", "username", "Title 1==2", "content of post (truth)")
		mp[0].decide()
		time.sleep(.1)
		assert str(mp[0].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
		assert str(mp[1].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
		assert str(mp[2].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
		assert str(mp[3].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
		assert str(mp[4].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
		assert mp[2].ballot_num == [1,0,0]

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
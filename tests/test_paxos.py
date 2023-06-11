import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 0

class TestHeartbeat:
		
	def test_full_decide(self):
		mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True) for i in range(5)]
		mp[0].queue.append(("POST", "user", "title of post", "content here"))
		assert mp[0].prepare() == True
		assert mp[0].accept() == True
		mp[0].decide()
		time.sleep(.1)
		assert str(mp[0].blog.blocks[0].T) == "<POST,user,title of post,content here>"
		assert str(mp[2].blog.blocks[0].T) == "<POST,user,title of post,content here>"
		assert mp[0].ballot_num == [1,0,0]

	def test_fail_election_hijack(self):
		mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True) for i in range(5)]
		mp[0].queue.append(("POST", "user", "title of post", "content here"))
		mp[1].queue.append(("POST", "user_hijacked", "title of hijack", "content hijacked"))
		assert mp[1].prepare() == True
		print(mp[1].queue)
		
		mp[0].net.fail_link(1)
		time.sleep(.1)
		assert mp[1].accept() == True
		time.sleep(.1)
		print(mp)

		assert mp[0].prepare() == True
		assert mp[0].accept() == True
		mp[0].decide()
		time.sleep(.1)
		assert str(mp[0].blog.blocks[0].T) == "<POST,user_hijacked,title of hijack,content hijacked>"
		assert str(mp[2].blog.blocks[0].T) == "<POST,user_hijacked,title of hijack,content hijacked>"

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
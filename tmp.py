import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os, sys


mp = [MultiPaxos(Network(i), i, Blog(), debug_print=True, use_queue=False) for i in range(5)]
mp[0].ballot_num = [4,8,1]
mp[0].accept_val = ("POST", "username", "Title 1==2", "content of post (truth)")
mp[0].decide()
time.sleep(.1)
assert str(mp[0].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
assert str(mp[1].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
assert str(mp[2].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
assert str(mp[3].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
assert str(mp[4].blog.blocks[0].T) == "<POST,username,Title 1==2,content of post (truth)>"
assert mp[2].ballot_num == [1,0,0]
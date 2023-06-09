import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import sys
import os
import pytest
# import capsys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

debugLevel = 0

class TestBlockchain(unittest.TestCase):
	@pytest.fixture(autouse=True)
	def capfd(self, capfd):
		self.capfd = capfd
		
	def setUp(self):
		sys.argv.append("debug")
		sys.argv.append(str(debugLevel))
	def tearDown(self):
		assert sys.argv.pop(-1) == str(debugLevel)
		assert sys.argv.pop(-1) == "debug"

	def test_empty_blog(self):
		bc = Blog()
		bc.blog()
		output = self.capfd.readouterr()
		assert output.out.strip() == "BLOG EMPTY"

	def test_duplicate_blog(self):
		bc = Blog()
		bc.add("POST", "biggergig", "hello", "this is the content")
		bc.add("POST", "biggergig", "hello2", "this is the content")
		...

		# bc = Blog()
		# bc.add("POST", "biggergig", "hello", "this is the content")
		# bc.add("POST", "biggergig", "hello2", "this is the content")



		# bc.add("COMMENT", "biggergig", "hello", "comment #1 on hello")
		# bc.add("POST", "cdese", "hello3", "this is the content")
		# bc.add("COMMENT", "biggergig", "hello", "comment #2 on hello")
		# bc.blog()
		# bc.view("cdese")
		# bc.view("biggergig")
		
		# bc.read("hello")
		# bc.read("NaN")
		# bc.read("hello2")
		

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
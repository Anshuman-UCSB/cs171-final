import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest
import time
from multipaxos import MultiPaxos
from network import Network
from blockchain import Blog
import pytest
# import capsys

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
		
		bc.view('test')
		output = self.capfd.readouterr()
		assert output.out.strip() == "NO POST"
		
		bc.read('test')
		output = self.capfd.readouterr()
		assert output.out.strip() == "POST NOT FOUND"

	def test_add_post(self):
		bc = Blog()
		bc.add("POST", "username", "Title 1", "this is the content")
		output = self.capfd.readouterr()
		assert output.out.strip() == "NEW POST `Title 1` from username"
		
		bc.blog()
		output = self.capfd.readouterr()
		assert output.out.strip() == "[\n\tTitle 1\n]"

		bc.view("username")
		output = self.capfd.readouterr()
		assert output.out.strip() == "Title 1\nthis is the content"

		bc.read("Title 1")
		output = self.capfd.readouterr()
		assert output.out.strip() == "Title 1 - username\nthis is the content"
	
	def test_add_comment(self):
		bc = Blog()
		bc.add("POST", "username", "Title 1", "this is the content")
		output = self.capfd.readouterr()
		bc.add("COMMENT", "username 2", "Title 1", "this is a comment")
		output = self.capfd.readouterr()
		assert output.out.strip() == "NEW COMMENT `Title 1` from username 2"

		bc.view("username 2")
		output = self.capfd.readouterr()
		assert output.out.strip() == "NO POST"

		bc.read("Title 1")
		output = self.capfd.readouterr()
		assert output.out.strip() == "Title 1 - username\nthis is the content\n\ncomment by username 2: this is a comment"		

	def test_add_comment_no_post(self):
		bc = Blog()
		bc.add("POST", "username", "Title 1", "this is the content")
		output = self.capfd.readouterr()
		bc.add("COMMENT", "username", "Title 2", "this is a comment")
		output = self.capfd.readouterr()
		assert output.out.strip() == "CANNOT COMMENT"

		bc.read("Title 1")
		output = self.capfd.readouterr()
		assert output.out.strip() == "Title 1 - username\nthis is the content"
	
	def test_duplicate_blog(self):
		bc = Blog()
		bc.add("POST", "username", "Title 1", "this is the content")
		output = self.capfd.readouterr()
		bc.add("POST", "username", "Title 1", "this is the content")
		output = self.capfd.readouterr()
		assert output.out.strip() == "DUPLICATE TITLE"
		assert len(bc.blocks) == 1
		
		bc.blog()
		output = self.capfd.readouterr()
		assert output.out.strip() == "[\n\tTitle 1\n]"

	def test_multiple_posts_comments(self):
		bc = Blog()
		bc.add("POST", "username 1", "Title 1", "this is the content")
		output = self.capfd.readouterr()
		bc.add("POST", "username 1", "Title 2", "this is the content")
		output = self.capfd.readouterr()
		
		bc.add("POST", "username 2", "Title 3", "this is the content")
		output = self.capfd.readouterr()
		bc.add("POST", "username 2", "Title 4", "this is the content")
		output = self.capfd.readouterr()

		bc.add("COMMENT", "username 3", "Title 1", "this is a comment 1")
		output = self.capfd.readouterr()
		bc.add("COMMENT", "username 4", "Title 1", "this is a comment 2")
		output = self.capfd.readouterr()

		bc.blog()
		output = self.capfd.readouterr()
		assert output.out.strip() == "[\n\tTitle 1,\n\tTitle 2,\n\tTitle 3,\n\tTitle 4\n]"

		bc.view("username 1")
		output = self.capfd.readouterr()
		assert output.out == "\tTitle 1\nthis is the content\n\n\tTitle 2\nthis is the content\n\n"

		bc.read("Title 1")
		output = self.capfd.readouterr()
		assert output.out == "\tTitle 1 - username 1\nthis is the content\n\ncomment by username 3: this is a comment 1\ncomment by username 4: this is a comment 2\n"
		
		

if __name__ == '__main__':
	try:
		debugLevel = int(sys.argv[-1])
		sys.argv.pop(-1)
	except:
		...
	unittest.main()
from sys import stdout,argv
from blockchain import Blog
from network import Network
from multipaxos import MultiPaxos
from utils import *
from os import _exit
import threading

class Server:
	def __init__(self,pid:int):
		self.pid = int(pid)
		self.blog = Blog()
		self.net = Network(self.pid)
		self.mp = MultiPaxos(self.net, self.pid, self.blog)

		threading.Thread(target=self.handleInput).start()

	def debug(self, *args, **kwargs):
		self.mp.debug(*args, **kwargs)
	def demo(self, *args, **kwargs):
		self.mp.demo(*args, **kwargs)

	def crash(self):
		self.debug("manual crash", flush=True)
		stdout.flush()
		_exit(0)
		

	def handleInput(self):
		while True:
			inp = input("> ")
			
			# protocol-related inputs
			if inp == "crash":
				self.crash()
			elif inp.startswith("failLink"):
				target = parseNums(inp)
				if len(target) > 1:
					target = target[0]
					self.net.fail_link(target)
					self.debug("broke link to",target)
			elif inp.startswith("fixLink"):
				target = parseNums(inp)
				if len(target) > 1:
					target = target[0]
					self.net.fix_link(target)
					self.debug("fixed link to",target)
			elif inp == "blockchain":
				print(self.blog)
			elif inp == "queue":
				print(self.mp.queue)

			# application-related inputs
			elif inp.startswith("post"):
				args = parseArgs(inp)
				if len(args) == 3:
					self.debug(args)
					self.mp.addQueue(("POST", args[0], args[1], args[2]))
			elif inp.startswith("comment"):
				args = parseArgs(inp)
				self.debug(args)
				self.mp.addQueue(("COMMENT", args[0], args[1], args[2]))
			elif inp == "blog":
				self.blog.blog()
			elif inp.startswith("view"):
				name = parseArgs(inp)[0]
				self.blog.view(name)
			elif inp.startswith("read"):
				title = parseArgs(inp)[0]
				self.blog.read(title)
			else:
				if isDebug():
					if inp.startswith("send"):
						dest = parseNums(inp)[0]
						msg = inp.split(',')[1][:-1].strip()
						self.net.send(dest, msg)
					else:
						debug("ERROR: invalid command")	
				else:
					print("ERROR: invalid command")

if __name__ == "__main__":
	try:
		s = Server(argv[1])
	except IndexError:
		print("ERROR: Format is python3 server.py [pid] [debug?]")
		exit(1)
from sys import stdout,argv
from blockchain import Blog
from network import Network
from utils import debug, parseNums, parseArgs, isDebug
from os import _exit
import threading

class Server:
	def __init__(self,pid:int):
		self.pid = int(pid)
		self.blog = Blog()
		self.net = Network(self.pid)

		threading.Thread(target=self.handleInput).start()

	def crash(self):
		debug("manual crash", flush=True)
		stdout.flush()
		_exit(0)
		

	def handleInput(self):
		while True:
			inp = input("> ")
			if inp == "crash":
				self.crash()
			elif inp.startswith("failLink"):
				target = parseNums(inp)[0]
				self.net.failLink(target)
				debug("broke link to",target)
			elif inp.startswith("fixLink"):
				target = parseNums(inp)[0]
				self.net.fixLink(target)
				debug("fixed link to",target)
			elif inp == "blockchain":
				print(self.blog)
			elif inp == "queue":
				# TODO: don't really understand how to do the multipaxos queue
				...
			elif inp.startswith("post"):
				args = parseArgs(inp)
				debug(args)
				self.blog.add("POST",*args)
			elif inp.startswith("comment"):
				args = parseArgs(inp)
				debug(args)
				self.blog.add("COMMENT",*args)
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
import hashlib
import sys

def debug(*args, **kwargs):
	if "debug" in sys.argv:
		print(*args, **kwargs)

def sha256(inp):
	return hashlib.sha256(inp.encode('UTF-8')).hexdigest()

class Content:
	def __init__(self, OP, username, title, content):
		self.OP = OP                					# operation	    
		self.username = username
		self.title = title
		self.content = content
	def __str__(self):
		return f"<{self.OP},{self.username},{self.title},{self.content}>"

class HashBlock:
	def __init__(self, H,OP, username, title, content):
		self.H = H		                                # hash pointer
		
		self.T = Content(OP, username, title, content)  # writing operation details
		
		self.N = 0		                                # nonce
		self.hash = None                                # current hash value
		self.mine()
	def mine(self):
		self.hash = sha256(str(self))
		while int(self.hash,16)>int("000"+"1"*253,2):
			self.N += 1
			self.hash = sha256(str(self))
	def __str__(self):
		return f"{self.H}{self.T}{self.N}"
	def __repr__(self):
		return f"{self.H}{self.T}{self.N}"

class Blockchain:
	def __init__(self):
		self.blocks = []
	def add(self, OP, username, title, content):
		h_prev = self.blocks[-1].hash if self.blocks else "0"*64
		
		posts_found = sum([b.T.title == title and b.T.OP == "POST" for b in self.blocks])
		if OP == "COMMENT":
			if posts_found != 1:
				print("CANNOT COMMENT")
				return False
		elif OP == "POST":
			if posts_found != 0:
				print("DUPLICATE TITLE")
				return False
		else:
			debug("invalid operation given, recieved OP",OP)
			return False
		
		self.blocks.append(HashBlock(h_prev, OP, username, title, content))
	def __str__(self):
		out = '[\n'
		for block in self.blocks:
			out+=f"\t{block.T},\n"
		out = out[:-2]
		out += '\n]'
		return out

if __name__ == "__main__":
	bc = Blockchain()
	bc.add("POST", "biggergig", "hello", "this is the content")
	bc.add("POST", "biggergig", "hello", "this is the content")
	bc.add("COMMENT", "biggergig", "hello", "comment #1 on hello")
	bc.add("POST", "cdese", "hello", "this is the content")
	bc.add("POST", "cdese", "hello2", "this is the content")
	bc.add("COMMENT", "biggergig", "hello", "comment #2 on hello")

	print(bc)
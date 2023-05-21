import hashlib
from utils import debug

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

class Blog:
	def __init__(self):
		self.blocks = []
	def add(self, OP, username, title, content):
		debug("Attempting to add block to blockchain")

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
	def blog(self):
		debug("print blog")

		titles = [b.T.title for b in self.blocks if b.T.OP == "POST"]
		if len(titles) == 0:
			print("BLOG EMPTY")
		else:
			print('[')
			for t in titles[:-1]:
				print(f"\t{t},")
			print(f"\t{titles[-1]}\n]")
	def view(self, username):
		debug("print content of", username)

		is_empty = True
		for b in self.blocks:
			if b.T.OP == "POST" and b.T.username == username:
				is_empty = False
				print("\t"+b.T.title)
				print(b.T.content)
				print()
		if is_empty:
			print("NO POST")
		
	def read(self, title):
		debug("read comments of", title)

		post = None
		for b in self.blocks:
			if b.T.OP == "POST" and b.T.title == title:
				post = b
		
		if post:
			print(f'\t{post.T.title} - {post.T.username}')
			print(post.T.content)
			print()
			
			for b in self.blocks:
				if b.T.OP == "COMMENT" and b.T.title == title:
					print(f"comment by {b.T.username}: {b.T.content}")
		
		else:
			print('POST NOT FOUND')
		
	def __str__(self):
		if len(self.blocks) == 0:
			return "[]"
		out = '[\n'
		for block in self.blocks:
			out+=f"\t{block.T},\n"
		out = out[:-2]
		out += '\n]'
		return out

if __name__ == "__main__":
	bc = Blog()
	bc.add("POST", "biggergig", "hello", "this is the content")
	bc.add("POST", "biggergig", "hello2", "this is the content")
	bc.add("COMMENT", "biggergig", "hello", "comment #1 on hello")
	bc.add("POST", "cdese", "hello3", "this is the content")
	bc.add("COMMENT", "biggergig", "hello", "comment #2 on hello")
	bc.blog()
	bc.view("cdese")
	bc.view("biggergig")
	
	bc.read("hello")
	bc.read("NaN")
	bc.read("hello2")
	# print(bc)
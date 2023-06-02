import socket
import threading
from utils import debug
import pickle
from time import sleep

class Network:
	def __init__(self, pid):
		self.pid = pid
		self.messages = []
		self.messageLock = threading.Lock()

		self.ip = "127.0.0.1"
		self.base_port = 9000

		self.UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		self.UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.UDP.bind((self.ip, self.base_port+self.pid))

		threading.Thread(target=self.read_messages).start()
		self.canSend = [True]*5

	def pop_message(self):
		while len(self.messages) == 0:
			sleep(.01)
		with self.messageLock:
			m =  self.messages.pop(0)
			print("popping", m, self.messages)
			return m

	def read_messages(self):
		while True:
			message,address = self.UDP.recvfrom(1024)
			message = pickle.loads(message)
			
			with self.messageLock:
				if message == "fail":
					self.canSend[address[1]-self.base_port] = False
				elif message == "fix":
					self.canSend[address[1]-self.base_port] = True
				else:
					if self.canSend[address[1]-self.base_port]:
						self.messages.append((message,address[1]-self.base_port))
						debug(self.pid,"Received message:",self.messages[-1])
						debug(self.messages)
					else:
						debug(self.pid,"didn't recieve message:",(message,address[1]-self.base_port))

	def broadcast(self, message):
		debug(self.pid, "broadcasting message",message)
		for dest in range(5):
			self.send(dest, message)

	def send(self, dest: int, message):
		# assert dest != self.pid, "uh oh, tried to send to self"
		if self.canSend[dest] == False:
			debug(self.pid, "failed to send a message to",dest,"due to broken link")
			return False
		self.UDP.sendto(pickle.dumps(message), (self.ip, self.base_port + dest))
		debug(self.pid,f"sent message {message} to {dest}")

	def failLink(self, dest):
		self.canSend[dest] = True
		self.send(dest, "fail")
		self.canSend[dest] = False
	def fixLink(self, dest):
		self.canSend[dest] = True
		self.send(dest, "fix")
	

if __name__ == "__main__":
	from time import sleep
	net = [Network(i) for i in range(5)]
	net[0].failLink(3)
	net[0].send(2, "message to 2")
	net[0].send(3, "message to 3")
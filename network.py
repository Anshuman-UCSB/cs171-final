import socket
import threading
from utils import debug
import pickle
from collections import deque
from copy import deepcopy
import time

class Network:
	def __init__(self, id, base_port = 9000, delay = None):
		self.id = id
		self.messages = deque()
		self.messageLock = threading.Lock()

		self.recvMessages = deque()
		self.recvMessageLock = threading.Lock()

		self.ip = "127.0.0.1"
		self.base_port = base_port

		self.UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		self.UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.UDP.bind((self.ip, self.base_port+self.id))

		threading.Thread(target=self.read_messages).start()
		self.canSend = [True]*5

		self.delay = delay or 0
		self.outgoing_msgs = []
		self.outgoing_lock = threading.Lock()

		threading.Thread(target=self.handle_out_queue).start()

	def pop_message(self):
		while len(self.messages) == 0:
			time.sleep(.1)
		
		with self.messageLock:
			return self.messages.popleft()
			
	def pop_recv_message(self):
		while len(self.recvMessages) == 0:
			time.sleep(.1)
		
		with self.messageLock:
			return self.recvMessages.popleft()

	def handle_out_queue(self):
		while True:
			with self.outgoing_lock:
				to_send = []
				for msg in self.outgoing_msgs:
					if msg[0] <= time.time():
						to_send.append(msg)
				self.outgoing_msgs = [x for x in self.outgoing_msgs if x not in to_send]
				for msg in to_send:
					debug("sending", msg)
					self.send(msg[1], msg[2])
			time.sleep(.05)

	def read_messages(self):
		while True:
			message,address = self.UDP.recvfrom(1024)
			message = pickle.loads(message)
			
			if message == "fail":
				self.canSend[address[1]-self.base_port] = False
				debug(self.id, "recieved fail link from", address[1]-self.base_port, self.canSend)
			elif message == "fix":
				self.canSend[address[1]-self.base_port] = True
			else:
				if self.canSend[address[1]-self.base_port]:
					if type(message) is tuple and message[0] in (
						"PROMISE", "ACCEPTED", "DECIDE", "PING", "PONG", "QUERY", "DATA"
						):
						with self.recvMessageLock:
							self.recvMessages.append((message,address[1]-self.base_port))
						debug(self.id,"Received message (R):",self.recvMessages[-1], level=3)
					else:
						with self.messageLock:
							self.messages.append((message,address[1]-self.base_port))
						debug(self.id,"Received message:",self.messages[-1], level = 3)
				else:
					debug(self.id,"didn't recieve message:",(message,address[1]-self.base_port), level = 3)

	def broadcast(self, message):
		debug("broadcasting message",message)
		for dest in range(5):
			debug("queuing message", dest, message)
			self.queue_message(dest, message)
		# print(self.outgoing_msgs, time.time())

	def queue_message(self, dest, message):
		message = deepcopy(message)
		with self.outgoing_lock:
			self.outgoing_msgs.append((time.time() + self.delay, dest, message))

	def send(self, dest: int, message):
		if self.canSend[dest] == False:
			debug(self.id, "failed to send a message to",dest,"due to broken link", level = 3)
			return False
		self.UDP.sendto(pickle.dumps(message), (self.ip, self.base_port + dest))
		debug(self.id,f"sent message {message} to {dest}", level = 3)

	def fail_link(self, dest):
		self.canSend[dest] = True
		self.send(dest, "fail")
		self.canSend[dest] = False
	def fix_link(self, dest):
		self.canSend[dest] = True
		self.send(dest, "fix")
	

if __name__ == "__main__":
	net = [Network(i) for i in range(5)]
	net[0].fail_link(3)
	net[0].send(2, "message to 2")
	net[0].send(3, "message to 3")
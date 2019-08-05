import socketserver
import threading
from time import strftime, localtime

HOST = ''
PORT = 9009
lock = threading.Lock() # creating a synchronising thread

class Manager:
'''
- in charge of managing and sending chats
- manage entered users
- manage removed/exited users
- manage users logging in and out
- manage all the user msg
'''

	def __init__(self):
		self.users = {} # dictionary of all the users {username : (socket, addr)}

	### adding user ID to self.users
	def addUser(self, username, conn, addr):
		if username in self.users:
			conn.send('Username taken\n'.encode())
			return None

		# adding new user
		lock.acquire() # lock required to block thread synchronisation
		self.users[username] = (conn, addr)
		lock.release() # release lock after update

		self.sendMessageToAll(f'[{username}] has connected')
		print(f'Users connected: [{len(self.users)}]')

		return username

	### removing user ID from self.users
	def removeUser(self, username):
		if username not in self.users:
			return

		lock.acquire()
		del self.users[username]
		lock.release()

		self.sendMessageToAll(f'{username} has left')
		print(f'Users connected: {len(self.users)}')

	### manage all sent msg
	def messageHandler(self, username, msg):
		
		if msg[0] != '/':
			currtime = strftime('%H:%M', localtime())
			self.sendMessageToAll(f'[{currtime}] @{username}: {msg}')
			return

		# if user puts /quit command, remove that user
		if msg.strip() == '/quit':
			self.removeUser(username)
			return -1

	def sendMessageToAll(self, msg):
		for conn, addr in self.users.values():
			conn.send(msg.encode())


class TCPHandler(socketserver.BaseRequestHandler):
	manager = Manager()

	### print client addr once client connects
	def handle(self):
		print(f'{self.client_address[0]} has joined')

		try:
			username = self.registerUsername()
			msg = self.request.recv(1024)
			while msg:

				print(msg.decode())
				# if user wants to quit
				if self.manager.messageHandler(username, msg.decode()) == -1:
					self.request.close()
					break

				# else receive message of 1024 bytes
				msg = self.request.recv(1024)

		except Exception as e:
			print(e)

		print(f'{self.client_address[0]} has disconnected')
		self.manager.removeUser(username)

	def registerUsername(self):
		while True:
			self.request.send('Username:'.encode())
			username = self.request.recv(1024)
			username = username.decode().strip()
			if self.manager.addUser(username, self.request, self.client_address):
				return username

class ChattingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

def runServer():
	print('Server initialised')
	print('Press Ctrl+C to end server')

	try:
		server = ChattingServer((HOST, PORT), TCPHandler)
		server.serve_forever()

	except KeyboardInterrupt:
		print('Ending chat server')
		server.shutdown()
		server.server_close()

runServer()
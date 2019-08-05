import socket
import threading
import os

HOST = 'localhost'
PORT = 9009

lock = threading.Lock()

def recvMsg(sock):
	while True:
		try:
			data = sock.recv(1024)
			if not data:
				break
			print(data.decode())
		except:
			pass

 
def runChat():

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	t = threading.Thread(target = recvMsg, args = (sock,), daemon = True)
	t.start()

	while True:
		msg = input()

		if msg == '/quit':
			sock.send(msg.encode())
			break
		sock.send(msg.encode())

runChat()
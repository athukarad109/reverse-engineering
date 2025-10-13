#!/usr/bin/env python3

import socket
import threading


class Server:
	def __init__(self, addr):
		self.s = socket.socket()
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind(addr)
		self.cs = dict()

	def serve(self):
		self.s.listen(1)
		while True:
			c, a = self.s.accept()
			print("Connection from {0}".format(a))
			self.cs[c] = a
			threading.Thread(target=handle, args=(a, self, c), daemon=True).start()

	def broadcast(self, line):
		for c in self.cs.keys():
			c.sendall(line.encode())

	def done(self, c):
		print("Disconnected: {0}".format(self.cs[c]))
		del self.cs[c]


def handle(name, s, c):
	buf = b''
	while True:
		temp = c.recv(1000)
		if temp == b'':
			break
		buf+= temp
		lines = buf.split(b'\n')
		for l in lines[:-1]:
			s.broadcast(name[0] + ': ' + l.decode())
		buf = lines[-1]
	s.done(c)


def main():
	s = Server(('0.0.0.0', 12345))
	s.serve()


if __name__ == '__main__':
	main()

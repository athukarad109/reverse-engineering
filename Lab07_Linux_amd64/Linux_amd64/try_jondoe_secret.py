#!/usr/bin/env python3
import socket, struct, sys

HOST = sys.argv[1] if len(sys.argv)>1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv)>2 else 7664

def recvn(s, n, timeout=1.0):
    s.settimeout(timeout); b=b''
    while len(b)<n:
        c=s.recv(n-len(b))
        if not c: break
        b+=c
    return b

s = socket.socket()
s.connect((HOST, PORT))
print("[*] greeting:", recvn(s,1))
# set user
user = b"johndoe\x00"
s.send(struct.pack("<BH", 0, len(user)) + user)
print("[*] SET_USER ack:", recvn(s,1))
_ = recvn(s, len(user))
# try pass
pw = b"password\x00"
s.send(struct.pack("<BH", 2, len(pw)) + pw)
ack = recvn(s,1)
print("[*] TRY_PASS ack:", ack)
if ack == b'\x08':
    print("[+] Auth succeeded, requesting secret")
    s.send(struct.pack("<BH", 4, 0xffff))
    if recvn(s,1) == b'\x0a':
        secret = recvn(s, 65535)
        print("[+] Secret (first 512 bytes):")
        print(secret[:512])
    else:
        print("[!] Did not receive secret ACK")
else:
    print("[!] Auth failed (server did not return success)")
s.close()

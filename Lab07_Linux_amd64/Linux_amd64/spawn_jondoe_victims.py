#!/usr/bin/env python3
# spawn_johndoe_victims.py
import socket, struct, threading, time, sys

if len(sys.argv) < 4:
    print("usage: python3 spawn_johndoe_victims.py HOST PORT NUM_VICTIMS")
    raise SystemExit(1)

HOST = sys.argv[1]
PORT = int(sys.argv[2], 0)
NUM = int(sys.argv[3])
HOLD = 300  # seconds to hold connections; change as needed

def recvn(s, n, timeout=1.0):
    s.settimeout(timeout)
    buf = b''
    while len(buf) < n:
        try:
            chunk = s.recv(n - len(buf))
        except Exception:
            break
        if not chunk:
            break
        buf += chunk
    return buf

def victim_thread(i):
    try:
        s = socket.socket()
        s.connect((HOST, PORT))
        _ = recvn(s,1)
        uname = b"johndoe\x00"
        pwd = b"password\x00"
        s.send(struct.pack('<BH', 0, len(uname)) + uname)
        _ = recvn(s,1); _ = recvn(s, len(uname))
        s.send(struct.pack('<BH', 2, len(pwd)) + pwd)
        _ = recvn(s,1)
        time.sleep(HOLD)
        s.close()
    except Exception as e:
        print("victim", i, "error:", e)

threads = []
for i in range(NUM):
    t = threading.Thread(target=victim_thread, args=(i,))
    t.daemon = True
    t.start()
    threads.append(t)
    time.sleep(0.01)

print(f"Spawned {NUM} johndoe victims. They will hold for {HOLD} seconds.")

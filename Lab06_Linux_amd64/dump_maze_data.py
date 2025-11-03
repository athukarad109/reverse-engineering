#!/usr/bin/env python3
"""
dump_maze_full.py - Maze data and wall interpretation dumper

Connects to maze server, prints:
  - raw bytes grid
  - bitflags grid
  - interpreted wall info per cell (N/S/W/E)

Usage:
  python3 dump_maze_full.py [HOST] [PORT]
"""
import socket, struct, sys, time

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8008

def recv_exact(s, n, timeout=None):
    if timeout is not None:
        s.settimeout(timeout)
    data = b""
    while len(data) < n:
        chunk = s.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket closed while receiving")
        data += chunk
    s.settimeout(None)
    return data

def read_message(s, timeout=3.0):
    t = recv_exact(s, 1, timeout)[0]
    if t == 0x00:
        payload = recv_exact(s, 2)
    elif t in (0x01, 0x02):
        ln = struct.unpack("<H", recv_exact(s, 2))[0]
        payload = struct.pack("<H", ln) + recv_exact(s, ln)
    elif t == 0x07:
        payload = recv_exact(s, 3)
    elif t in (0x08, 0x0A, 0x0B, 0x0C, 0x09):
        payload = recv_exact(s, 1)
    else:
        payload = b""
    return t, payload

def parse_maze(payload):
    ln = struct.unpack("<H", payload[:2])[0]
    data = payload[2:2 + ln]
    w, h = data[0], data[1]
    cells = list(data[2:])
    if len(cells) != w * h:
        print(f"[WARN] Maze len mismatch: got {len(cells)} vs expected {w*h}")
    return w, h, cells

def interpret_walls(byte_val):
    """Return dict with N/S/W/E -> 'wall' or 'open' based on bits."""
    walls = {}
    walls['N'] = 'wall' if byte_val & 0x08 else 'open'
    walls['W'] = 'wall' if byte_val & 0x04 else 'open'
    walls['S'] = 'wall' if byte_val & 0x02 else 'open'
    walls['E'] = 'wall' if byte_val & 0x01 else 'open'
    return walls

def print_raw_grid(w, h, cells):
    print("\n=== Raw maze bytes (hex) ===")
    for y in range(h):
        print(" ".join(f"{cells[y*w+x]:02x}" for x in range(w)))

def print_bitflags(w, h, cells):
    print("\n=== Cell bitflags (b3 b2 b1 b0) ===")
    for y in range(h):
        row = []
        for x in range(w):
            b = cells[y*w + x]
            bits = "".join(str((b >> i) & 1) for i in reversed(range(4)))
            row.append(bits)
        print(" ".join(row))

def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    player_id = None
    w = h = 0
    cells = []
    pos = None

    # Sync: read until we have maze and our pos
    while True:
        t, p = read_message(s, timeout=5.0)
        if t == 0x00:
            player_id, maxp = p[0], p[1]
            print(f"[INFO] Welcome: player {player_id+1}/{maxp}")
        elif t == 0x01:
            w, h, cells = parse_maze(p)
            print(f"[MAZE] {w}x{h} ({len(cells)} bytes)")
        elif t == 0x07:
            pid, x, y = p
            if player_id is not None and pid == player_id:
                pos = (x, y)
                print(f"[POS] Player {pid} at {pos}")
        elif t == 0x08 and player_id is not None and p[0] == player_id:
            print(f"[TURN] Player {p[0]+1}'s turn")
            break
        if w and h and pos:
            break

    if not cells:
        print("[ERR] No maze data received.")
        return

    print_raw_grid(w, h, cells)
    print_bitflags(w, h, cells)

    print("\n=== Interpreted Walls per Cell ===")
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            val = cells[idx]
            walls = interpret_walls(val)
            walls_str = " ".join([f"{d}:{state}" for d, state in walls.items()])
            print(f"({x:02},{y:02}) 0x{val:02x} -> {walls_str}")

    s.close()
    print("\n[DONE] Maze dump complete.")

if __name__ == "__main__":
    main()

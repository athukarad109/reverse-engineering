#!/usr/bin/env python3
"""
dump_maze_visual.py
Connects to the maze server and prints each cell's walls in human-readable form.
Mapping confirmed: bits = (S,W,N,E), 1=open, 0=wall.
"""

import socket, struct, sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8008

# ------------------- Networking helpers -------------------

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
    elif t in (0x08, 0x09, 0x0A, 0x0B, 0x0C):
        payload = recv_exact(s, 1)
    else:
        payload = b""
    return t, payload

def parse_maze(payload):
    ln = struct.unpack("<H", payload[:2])[0]
    data = payload[2:2+ln]
    w, h = data[0], data[1]
    cells = list(data[2:])
    if len(cells) != w*h:
        print(f"[WARN] Maze length mismatch (expected {w*h}, got {len(cells)})")
    return w, h, cells

# ------------------- Maze decoding -------------------

# ✅ Final confirmed mapping: bits = (S,W,N,E), 1=open, 0=wall
def interpret_walls(byte_val):
    S = (byte_val >> 3) & 1
    W = (byte_val >> 2) & 1
    N = (byte_val >> 1) & 1
    E = (byte_val >> 0) & 1
    return {
        'N': 'open' if N else 'wall',
        'S': 'open' if S else 'wall',
        'E': 'open' if E else 'wall',
        'W': 'open' if W else 'wall',
    }

# Convert to arrow visualization
def arrow_view(walls):
    arrows = []
    if walls['N'] == 'open': arrows.append('↑')
    if walls['S'] == 'open': arrows.append('↓')
    if walls['E'] == 'open': arrows.append('→')
    if walls['W'] == 'open': arrows.append('←')
    return "".join(arrows) if arrows else "█"

# ------------------- Main logic -------------------

def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    player_id = None
    w = h = 0
    cells = []
    pos = None

    print("[*] Waiting for welcome + maze + position...")
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
                print(f"[POS] You are at ({x},{y})")
        elif t == 0x08 and player_id is not None and p[0] == player_id:
            print(f"[TURN] Player {p[0]+1}'s turn")
            break
        if w and h and pos:
            break

    if not cells:
        print("[ERR] No maze data received.")
        return

    print("\n=== Maze Layout ===")
    for y in range(h):
        for x in range(w):
            val = cells[y*w + x]
            walls = interpret_walls(val)
            arrows = arrow_view(walls)
            print(f"({x:02},{y:02}) 0x{val:02x} -> {arrows:<4} "
                  f"[N:{walls['N']:<5} S:{walls['S']:<5} E:{walls['E']:<5} W:{walls['W']:<5}]")
        print()

    s.close()
    print("\n[DONE] Maze data visualization complete.")

if __name__ == "__main__":
    main()

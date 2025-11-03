#!/usr/bin/env python3
"""
finalbot_jump.py
Automatic maze solver with BFS + up to 3 jumps.
Mapping confirmed: bits = (S,W,N,E), 1=open, 0=wall.
"""

import socket, struct, sys, time
from collections import deque

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8008

# Basic step commands
DIRS = {
    "N": (0, -1, 0x10),
    "S": (0, +1, 0x12),
    "E": (+1, 0, 0x0f),
    "W": (-1, 0, 0x11),
}
# Jump commands
JUMPS = {
    "N": (0, -2, 0x14),
    "S": (0, +2, 0x16),
    "E": (+2, 0, 0x13),
    "W": (-2, 0, 0x15),
}

def recv_exact(s, n, timeout=None):
    if timeout is not None:
        s.settimeout(timeout)
    data = b""
    while len(data) < n:
        chunk = s.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket closed")
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
    return w, h, cells

# bits = (S,W,N,E), 1=open
def interpret_walls(byte_val):
    S = (byte_val >> 3) & 1
    W = (byte_val >> 2) & 1
    N = (byte_val >> 1) & 1
    E = (byte_val >> 0) & 1
    return {'N': bool(N), 'S': bool(S), 'E': bool(E), 'W': bool(W)}

def build_graph(w, h, cells):
    """Adjacency graph with strict wall & border validation."""
    graph = {}
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}

    for y in range(h):
        for x in range(w):
            idx = y * w + x
            cell = interpret_walls(cells[idx])
            edges = []

            # --- Normal 1-step moves ---
            for d, (dx, dy, _) in DIRS.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                target = interpret_walls(cells[ny * w + nx])
                if cell[d] and target[opp[d]]:
                    edges.append((nx, ny, d, False))

            # --- Jump (2-step) moves ---
            for d, (dx2, dy2, _) in JUMPS.items():
                # early boundary rejection
                if (d == "N" and y < 2) or (d == "S" and y > h - 3) or \
                   (d == "W" and x < 2) or (d == "E" and x > w - 3):
                    continue

                ix, iy = x + dx2 // 2, y + dy2 // 2
                nx, ny = x + dx2, y + dy2

                if not (0 <= nx < w and 0 <= ny < h):
                    continue  # redundant but safe

                inter = interpret_walls(cells[iy * w + ix])
                target = interpret_walls(cells[ny * w + nx])

                # must be open all along (source, mid, dest)
                if cell[d] and inter[d] and target[opp[d]]:
                    edges.append((nx, ny, d, True))

            graph[(x, y)] = edges

    return graph



def bfs_with_jumps(graph, start, goal, max_jumps=3):
    """BFS over (x,y,jumps_used). Path holds (dir, is_jump)."""
    queue = deque([(start, [], 0)])
    visited = {(start, 0)}
    while queue:
        (x, y), path, jumps = queue.popleft()
        if (x, y) == goal:
            return path
        for nx, ny, d, is_jump in graph[(x, y)]:
            new_jumps = jumps + (1 if is_jump else 0)
            state = ((nx, ny), new_jumps)
            if new_jumps <= max_jumps and state not in visited:
                visited.add(state)
                queue.append(((nx, ny), path + [(d, is_jump)], new_jumps))
    return None

def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    player_id = None
    w = h = 0
    cells = []
    pos = None

    print("[*] Syncing with server...")
    while True:
        t, p = read_message(s, timeout=5.0)
        if t == 0x00:
            player_id, maxp = p[0], p[1]
            print(f"[INFO] Player {player_id+1}/{maxp}")
        elif t == 0x01:
            w, h, cells = parse_maze(p)
            print(f"[MAZE] {w}x{h} received.")
        elif t == 0x07:
            pid, x, y = p
            if pid == player_id:
                pos = (x, y)
                print(f"[POS] Start = {pos}")
        elif t == 0x08 and p[0] == player_id:
            print("[TURN] It's our turn.")
            break
        if w and h and pos:
            break

    if not cells:
        print("[ERR] No maze data received.")
        return

    goal = (w-1, h-1)
    graph = build_graph(w, h, cells)
    path = bfs_with_jumps(graph, pos, goal, max_jumps=3)
    if not path:
        print("[!] No path found (even with jumps).")
        s.close()
        return

    print(f"[PATH] {len(path)} steps")
    print(" -> ".join([f"{d}{'J' if j else ''}" for d, j in path]))

    # Execute path
    for d, is_jump in path:
        cmd = (JUMPS[d][2] if is_jump else DIRS[d][2])
        s.send(bytes([cmd]))
        print(f"[>] {'JUMP' if is_jump else 'WALK'} {d} -> 0x{cmd:02x}")
        time.sleep(0.15)

        # Read feedback until pos/illegal/win
        while True:
            try:
                t, p = read_message(s, timeout=1.0)
            except socket.timeout:
                break
            if t == 0x05:
                print(f"[!] Illegal move {d} ({'jump' if is_jump else 'walk'})")
                break
            elif t == 0x07 and p[0] == player_id:
                pos = (p[1], p[2])
                print(f"[POS] {pos}")
                break
            elif t == 0x0C:
                print(f"[🏁] Player {p[0]+1} WINS!")
                s.close()
                return

    s.close()
    print("[DONE] Path execution complete.")

if __name__ == "__main__":
    main()

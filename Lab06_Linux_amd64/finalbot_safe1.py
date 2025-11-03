#!/usr/bin/env python3


import socket, struct, sys, time
from collections import deque

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8008

# Directions
DIRS = {
    "N": (0, -1, 0x10),
    "S": (0, +1, 0x12),
    "E": (+1, 0, 0x0f),
    "W": (-1, 0, 0x11),
}
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}

# Helper funtion for reveiving exact number of bytes

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

# Wall interpretation
def interpret_walls(byte_val):
    S = (byte_val >> 3) & 1
    W = (byte_val >> 2) & 1
    N = (byte_val >> 1) & 1
    E = (byte_val >> 0) & 1
    return {
        'N': bool(N),
        'S': bool(S),
        'E': bool(E),
        'W': bool(W),
    }

def build_graph(w, h, cells):
    """Create adjacency list graph for maze."""
    graph = {}
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            cell = interpret_walls(cells[idx])
            edges = []
            for d, (dx, dy, _) in DIRS.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if cell[d]:  # if this direction is open
                        edges.append((nx, ny, d))
            graph[(x, y)] = edges
    return graph

def bfs_path(graph, start, goal):
    """Return path of directions from start to goal using BFS."""
    queue = deque([(start, [])])
    visited = {start}
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path
        for nx, ny, d in graph[(x, y)]:
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [d]))
    return None

# Main function

def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    player_id = None
    w = h = 0
    cells = []
    pos = None

    # --- Sync Phase ---
    print("[*] Waiting for welcome + maze + position...")
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
            if player_id is not None and pid == player_id:
                pos = (x, y)
                print(f"[POS] Player start = {pos}")
        elif t == 0x08 and player_id is not None and p[0] == player_id:
            print(f"[TURN] Player {p[0]+1}'s turn.")
            break
        if w and h and pos:
            break

    if not cells:
        print("[ERR] No maze data received.")
        return

    # Build graph + BFS path
    graph = build_graph(w, h, cells)
    goal = (w - 1, h - 1)
    path = bfs_path(graph, pos, goal)
    if not path:
        print("[!] No path found!")
        s.close()
        return

    print(f"[PATH] Found path ({len(path)} steps): {' '.join(path)}")

    # Movement Phase 
    for move in path:
        dx, dy, cmd = DIRS[move]
        s.send(bytes([cmd]))
        print(f"[>] Move {move} -> send 0x{cmd:02x}")
        time.sleep(0.15)

        # read feedback until position or error
        while True:
            try:
                t, p = read_message(s, timeout=1.0)
            except socket.timeout:
                break
            if t == 0x05:
                print(f"[!] Illegal move attempted ({move})")
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

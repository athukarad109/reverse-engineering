#!/usr/bin/env python3
import socket, struct, sys
from collections import deque

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = 8008

# Walk-only commands
CMD = {"N": 0x10, "S": 0x12, "W": 0x11, "E": 0x0f}
DIRS = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}

# ---------- Network ----------
def recv_exact(s, n):
    data = b""
    while len(data) < n:
        chunk = s.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket closed")
        data += chunk
    return data

def read_msg(s):
    t = recv_exact(s, 1)[0]
    if t in (0x00,):      # welcome
        payload = recv_exact(s, 2)
    elif t in (0x01, 0x02):  # maze
        ln = struct.unpack("<H", recv_exact(s, 2))[0]
        payload = struct.pack("<H", ln) + recv_exact(s, ln)
    elif t == 0x07:
        payload = recv_exact(s, 3)
    elif t in (0x08, 0x05, 0x0C, 0x0E, 0x0B):
        payload = recv_exact(s, 1)
    else:
        payload = b""
    return t, payload

# ---------- Maze decoding ----------
def interpret_walls(b):
    """Final verified mapping: bits (S,W,N,E) = (1,2,4,8) ; 1 = wall"""
    return {
        "S": not (b & 0x01),
        "W": not (b & 0x02),
        "N": not (b & 0x04),
        "E": not (b & 0x08),
    }

def build_graph(w, h, cells):
    g = {}
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            cell = interpret_walls(cells[idx])
            edges = []
            for d, (dx, dy) in DIRS.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    target = interpret_walls(cells[ny * w + nx])
                    if cell[d] and target[OPP[d]]:
                        edges.append((nx, ny, d))
            g[(x, y)] = edges
    return g

def bfs(g, start, goal):
    q = deque([(start, [])])
    seen = {start}
    while q:
        (x, y), path = q.popleft()
        if (x, y) == goal:
            return path
        for nx, ny, d in g[(x, y)]:
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append(((nx, ny), path + [d]))
    return None

# ---------- Main ----------
def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    player = None
    w = h = 0
    cells = []
    pos = (0, 0)

    # Sync until maze + position + turn
    while True:
        t, p = read_msg(s)
        if t == 0x00:
            player, maxp = p
            print(f"[SYNC] You are player {player+1}/{maxp}")
        elif t in (0x01, 0x02):
            ln = struct.unpack("<H", p[:2])[0]
            maze = p[2:]
            w, h = maze[0], maze[1]
            cells = list(maze[2:])
            print(f"[SYNC] Maze {w}x{h} received.")
        elif t == 0x07:
            pid, px, py = p
            if pid == player:
                pos = (px, py)
                print(f"[SYNC] Position {pos}")
        elif t == 0x08 and p[0] == player:
            print("[TURN] Our turn starts.")
            break

    graph = build_graph(w, h, cells)
    goal = (w-1, h-1)
    path = bfs(graph, pos, goal)
    if not path:
        print("[!] No path found.")
        return

    print(f"[PATH] {len(path)} steps.")
    print(" -> ".join(path))

    for d in path:
        s.send(bytes([CMD[d]]))
        while True:
            t, p = read_msg(s)
            if t == 0x07 and p[0] == player:
                pos = (p[1], p[2])
                print(f"[MOVE] {d} -> {pos}")
                break
            elif t == 0x05:
                print(f"[!] Illegal move {d}")
                break
            elif t == 0x0C:
                print("[WIN] Victory!")
                s.close()
                return
            elif t == 0x08:
                if p[0] != player:
                    print("[WAIT] Opponent's turn.")
                else:
                    break
    print("[DONE]")
    s.close()

if __name__ == "__main__":
    main()

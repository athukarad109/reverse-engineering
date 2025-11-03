#!/usr/bin/env python3

import socket, struct, sys, time
from collections import deque

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8008

# Directions (keep your bytes)
DIRS = {
    "N": (0, -1, 0x10),
    "S": (0, +1, 0x12),
    "E": (+1, 0, 0x0f),
    "W": (-1, 0, 0x11),
}
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}

# helpers 
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
    if t == 0x00:  # welcome
        payload = recv_exact(s, 2)
    elif t in (0x01, 0x02):  # maze (raw or compressed)
        ln = struct.unpack("<H", recv_exact(s, 2))[0]
        payload = struct.pack("<H", ln) + recv_exact(s, ln)
    elif t == 0x07:  # position
        payload = recv_exact(s, 3)
    elif t in (0x05, 0x06, 0x08, 0x09, 0x0A, 0x0B, 0x0C):  # small payload msgs
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


def interpret_walls(byte_val):
    # bit interpretation:
    S = (byte_val >> 3) & 1   # bit for South (1=open)
    W = (byte_val >> 2) & 1   # bit for West  (1=open)
    N = (byte_val >> 1) & 1   # bit for North (1=open)
    E = (byte_val >> 0) & 1   # bit for East  (1=open)
    return {
        'N': bool(N),
        'S': bool(S),
        'E': bool(E),
        'W': bool(W),
    }

def build_graph(w, h, cells):
    """Adjacency graph with BOTH-SIDES-OPEN rule."""
    graph = {}
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            here = interpret_walls(cells[idx])
            edges = []
            for d, (dx, dy, _) in DIRS.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    # require both current direction open and neighbor opposite open
                    there = interpret_walls(cells[ny * w + nx])
                    if here[d] and there[OPP[d]]:
                        edges.append((nx, ny, d))
            graph[(x, y)] = edges
    return graph

def bfs_path(graph, start, goal):
    """Return path (list of 'N','S','E','W') using BFS."""
    q = deque([(start, [])])
    seen = {start}
    while q:
        (x, y), path = q.popleft()
        if (x, y) == goal:
            return path
        for nx, ny, d in graph[(x, y)]:
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append(((nx, ny), path + [d]))
    return None

def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    player_id = None
    w = h = 0
    cells = []
    pos = None

    # Sync Phase 
    print("[*] Waiting for welcome + maze + position + our turn...")
    have_maze = False
    have_pos = False
    our_turn = False

    while True:
        t, p = read_message(s, timeout=5.0)

        if t == 0x00:
            player_id, maxp = p[0], p[1]
            print(f"[INFO] Player {player_id+1}/{maxp}")

        elif t == 0x01:
            w, h, cells = parse_maze(p)
            print(f"[MAZE] {w}x{h} received ({len(cells)} bytes).")
            have_maze = True

        elif t == 0x07:
            pid, x, y = p
            if player_id is not None and pid == player_id:
                pos = (x, y)
                have_pos = True
                print(f"[POS] Player start = {pos}")

        elif t == 0x08:
            turn_id = p[0]
            if player_id is not None and turn_id == player_id:
                our_turn = True
                print(f"[TURN] Player {turn_id+1}'s turn (ours).")
                if have_maze and have_pos:
                    break
            else:
                # not our turn yet; keep syncing
                pass

        # if server sends maze & pos before explicit turn, we can proceed once turn arrives
        if have_maze and have_pos and our_turn:
            break

    if not cells or w*h != len(cells):
        print("[ERR] No valid maze data received.")
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

    #  Movement Phase (turn-gated per move) 
    
    for move in path:
        # wait for our turn before each step (multiplayer-safe)
        if not our_turn:
            while True:
                t, p = read_message(s, timeout=5.0)
                if t == 0x08:
                    our_turn = (p[0] == player_id)
                    if our_turn:
                        break
                elif t == 0x07 and p[0] == player_id:
                    pos = (p[1], p[2])
                elif t == 0x05:
                    print("[!] Illegal move reported outside our step?")
                elif t == 0x0C:
                    print(f"Player {p[0]+1} WINS!")
                    s.close()
                    return

        dx, dy, cmd = DIRS[move]
        s.send(bytes([cmd]))
        print(f"[>] Move {move} -> send 0x{cmd:02x}")

        # read until we get our position update or illegal/win/turn
        while True:
            t, p = read_message(s, timeout=3.0)
            if t == 0x07 and p[0] == player_id:
                pos = (p[1], p[2])
                print(f"[POS] {pos}")
                # after a successful step, server typically announces next turn
                # but if not, we explicitly wait again above.
                break
            elif t == 0x05:
                print(f"[!] Illegal move attempted ({move})")
                s.close()
                return
            elif t == 0x08:
                our_turn = (p[0] == player_id)
                # keep looping until pos or illegal/win; we’ll gate next step above
            elif t == 0x0C:
                print(f"Player {p[0]+1} WINS!")
                s.close()
                return

        # after making a move, assume it’s no longer our turn until told otherwise
        our_turn = False

    s.close()
    print("[DONE] Path execution complete.")

if __name__ == "__main__":
    main()

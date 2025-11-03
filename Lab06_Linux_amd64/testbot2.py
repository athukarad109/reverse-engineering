#!/usr/bin/env python3
import socket, struct, time, sys
from collections import deque

# ===================== CONFIG =====================
HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = 8008
CMD_UP, CMD_DOWN, CMD_LEFT, CMD_RIGHT = 0x10, 0x12, 0x11, 0x0f
MOVES = {
    "N": (0, -1, CMD_UP),
    "S": (0, +1, CMD_DOWN),
    "W": (-1, 0, CMD_LEFT),
    "E": (+1, 0, CMD_RIGHT),
}
DIR_BITS = {"N": 0x04, "S": 0x01, "W": 0x02, "E": 0x08}
OPPOSITE = {"N": "S", "S": "N", "W": "E", "E": "W"}
# ===================================================

def recv_exact(s, n):
    data = b""
    while len(data) < n:
        chunk = s.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket closed")
        data += chunk
    return data

def read_message(s):
    t = recv_exact(s, 1)[0]
    if t == 0x00:
        payload = recv_exact(s, 2)
    elif t == 0x01:
        ln = struct.unpack("<H", recv_exact(s, 2))[0]
        payload = recv_exact(s, ln)
    elif t == 0x07:
        payload = recv_exact(s, 3)
    elif t in (0x08, 0x0A, 0x0B, 0x0C):
        payload = recv_exact(s, 1)
    else:
        payload = b""
    return t, payload

def parse_maze(payload):
    w, h = payload[0], payload[1]
    cells = list(payload[2:])
    return w, h, cells

def can_move(cells, w, h, x, y, d):
    bit = DIR_BITS[d]
    idx = y * w + x
    if cells[idx] & bit:  # wall present
        return False
    dx, dy, _ = MOVES[d]
    nx, ny = x + dx, y + dy
    if not (0 <= nx < w and 0 <= ny < h):
        return False
    # check opposite wall of target
    opposite_bit = DIR_BITS[OPPOSITE[d]]
    if cells[ny * w + nx] & opposite_bit:
        return False
    return True

def bfs_path(cells, w, h, start, visited):
    q = deque([(start, [])])
    seen = {start}
    while q:
        (x, y), path = q.popleft()
        for d in "NSEW":
            if not can_move(cells, w, h, x, y, d):
                continue
            dx, dy, _ = MOVES[d]
            nx, ny = x + dx, y + dy
            if (nx, ny) in seen:
                continue
            if (nx, ny) not in visited:
                return path + [d]
            seen.add((nx, ny))
            q.append(((nx, ny), path + [d]))
    return []

def print_maze_ascii(w, h, cells):
    N, S, W, E = 0x04, 0x01, 0x02, 0x08
    print("═══ MAZE (Verified Mapping) ═══")
    for y in range(h):
        # top borders
        top = "+"
        for x in range(w):
            top += "---+" if (cells[y*w+x] & N) else "   +"
        print(top)
        mid = "|"
        for x in range(w):
            mid += "   "
            mid += "|" if (cells[y*w+x] & E) else " "
        print(mid)
    # bottom border
    print("+" + "---+" * w)
    print("════════════════════════════════")

def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    player_id = None
    w = h = 0
    cells = []
    pos = (0, 0)
    visited = set()
    jumps_left = 3

    while True:
        t, p = read_message(s)
        if t == 0x00:
            player_id, maxp = p
            print(f"[SERVER] Welcome player {player_id+1}/{maxp}")
        elif t == 0x01:
            w, h, cells = parse_maze(p)
            print(f"[MAZE] Received {w}x{h} ({len(cells)} bytes)")
            print_maze_ascii(w, h, cells)
        elif t == 0x07:
            pid, px, py = p
            if pid == player_id:
                pos = (px, py)
                print(f"[POS] Player {pid} @ {pos}")
        elif t == 0x08:
            pid = p[0]
            if pid != player_id:
                continue
            print(f"[TURN] Player {pid+1}")
            visited.add(pos)
            path = bfs_path(cells, w, h, pos, visited)
            if not path:
                print("[BFS] Maze fully explored or blocked. Idling.")
                continue
            d = path[0]
            dx, dy, cmd = MOVES[d]
            nx, ny = pos[0] + dx, pos[1] + dy
            print(f"[>] Move {d} -> ({nx},{ny}) cmd=0x{cmd:02x}")
            s.send(bytes([cmd]))
        elif t == 0x05:
            print("[!] Server: Illegal move — retrying next turn")
        elif t == 0x0C:
            pid = p[0]
            print(f"[SERVER] Player {pid+1} wins!")
            break
        elif t == 0x0E:
            print("[SERVER] Terminated")
            break

if __name__ == "__main__":
    main()

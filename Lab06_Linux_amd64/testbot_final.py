#!/usr/bin/env python3
import socket, struct, sys
from collections import deque

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = 8008

# ==================== COMMAND MAP ====================
CMD = {
    "N": 0x10, "S": 0x12, "W": 0x11, "E": 0x0f,
    "JN": 0x14, "JS": 0x16, "JW": 0x15, "JE": 0x13
}

# ==================== WALL BITS ====================
# Confirmed visually (matches server):
# 0x01 = North wall
# 0x04 = South wall
# 0x08 = West wall
# 0x02 = East wall
N_BIT, S_BIT, W_BIT, E_BIT = 0x01, 0x04, 0x08, 0x02
OPP = {"N": "S", "S": "N", "W": "E", "E": "W"}
DIRS = {
    "N": (0, -1, N_BIT, CMD["N"]),
    "S": (0, +1, S_BIT, CMD["S"]),
    "W": (-1, 0, W_BIT, CMD["W"]),
    "E": (+1, 0, E_BIT, CMD["E"]),
}

# ==================== INDEXING ====================
def idx_of(x, y, w, h):
    # Server stores maze bytes column-major
    return x * h + y

# ==================== HELPERS ====================
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
    if t == 0x00:
        pl = recv_exact(s, 2)
    elif t == 0x01:
        ln = struct.unpack("<H", recv_exact(s, 2))[0]
        pl = recv_exact(s, ln)
    elif t == 0x07:
        pl = recv_exact(s, 3)
    elif t in (0x08, 0x05, 0x0A, 0x0B, 0x0C, 0x0E):
        pl = recv_exact(s, 1)
    else:
        pl = b""
    return t, pl

def parse_maze(payload):
    w, h = payload[0], payload[1]
    cells = list(payload[2:])
    return w, h, cells

def can_move(cells, w, h, x, y, d):
    dx, dy, bit, _ = DIRS[d]
    i = idx_of(x, y, w, h)
    if cells[i] & bit:  # Wall on current cell
        return False
    nx, ny = x + dx, y + dy
    if not (0 <= nx < w and 0 <= ny < h):
        return False
    opp_bit = DIRS[OPP[d]][2]
    j = idx_of(nx, ny, w, h)
    if cells[j] & opp_bit:  # Wall on neighbor
        return False
    return True

def bfs_to_unvisited(cells, w, h, start, visited):
    q = deque([(start, [])])
    seen = {start}
    while q:
        (x, y), path = q.popleft()
        if (x, y) not in visited and (x, y) != start:
            return path
        for d in ("N", "S", "W", "E"):
            if not can_move(cells, w, h, x, y, d):
                continue
            dx, dy, _, _ = DIRS[d]
            nx, ny = x + dx, y + dy
            if (nx, ny) in seen:
                continue
            seen.add((nx, ny))
            q.append(((nx, ny), path + [d]))
    return []

def draw_ascii(w, h, cells, pos, visited):
    print("\n=== ASCII Maze (server-aligned) ===")
    for y in range(h):
        # Top border of each cell
        line = "+"
        for x in range(w):
            line += "---+" if (cells[idx_of(x, y, w, h)] & N_BIT) else "   +"
        print(line)
        # Mid line with walls
        mid = "|"
        for x in range(w):
            ch = "0" if (x, y) == pos else ("." if (x, y) in visited else " ")
            mid += f" {ch} "
            mid += "|" if (cells[idx_of(x, y, w, h)] & E_BIT) else " "
        print(mid)
    print("+" + "---+" * w)

# ==================== MAIN ====================
def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")

    player = None
    w = h = 0
    cells = []
    pos = None
    visited = set()

    while True:
        t, p = read_msg(s)

        if t == 0x00:
            player, maxp = p
            print(f"Player {player+1}/{maxp}")

        elif t == 0x01:
            w, h, cells = parse_maze(p)
            print(f"[MAZE] Received {w}x{h} ({len(cells)} bytes)")
            print(f"[CHECK] cell(0,0)=0x{cells[idx_of(0,0,w,h)]:02x}")

        elif t == 0x07:
            pid, x, y = p
            if pid == player:
                pos = (x, y)

        elif t == 0x08:
            pid = p[0]
            if pid != player or pos is None:
                continue

            visited.add(pos)
            path = bfs_to_unvisited(cells, w, h, pos, visited)

            if not path:
                print("[BFS] No unvisited reachable cells (fully explored). Idle.")
                draw_ascii(w, h, cells, pos, visited)
                continue

            d = path[0]
            dx, dy, _, cmd = DIRS[d]
            nx, ny = pos[0] + dx, pos[1] + dy

            if can_move(cells, w, h, pos[0], pos[1], d):
                s.send(bytes([cmd]))
                pos = (nx, ny)
                print(f"[MOVE] Walk {d} -> {pos}")
            else:
                print(f"[BLOCKED] {d} wall hit. Skipping.")

        elif t == 0x05:
            print("[!] Illegal Move — server rejected step.")

        elif t == 0x0C:
            pid = p[0]
            print(f"[WIN] Player {pid+1} wins!")
            break

        elif t == 0x0E:
            print("[SERVER] Terminated.")
            break

if __name__ == "__main__":
    main()

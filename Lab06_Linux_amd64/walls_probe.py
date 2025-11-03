#!/usr/bin/env python3
import socket, struct, sys, time

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = 8008

# Commands from client binary
CMD_UP, CMD_DOWN, CMD_LEFT, CMD_RIGHT = 0x10, 0x12, 0x11, 0x0f
MOVES = {
    "N": (0, -1, CMD_UP),
    "S": (0, +1, CMD_DOWN),
    "W": (-1, 0, CMD_LEFT),
    "E": (+1, 0, CMD_RIGHT),
}
OPP = {"N": "S", "S": "N", "W": "E", "E": "W"}

def recv_exact(s, n, timeout=None):
    s.settimeout(timeout)
    data = b""
    while len(data) < n:
        chunk = s.recv(n - len(data))
        if not chunk:
            raise ConnectionError("socket closed")
        data += chunk
    s.settimeout(None)
    return data

def read_message(s, timeout=1.0):
    """Read one complete server message."""
    t = recv_exact(s, 1, timeout)[0]
    if t == 0x00:
        payload = recv_exact(s, 2)
    elif t == 0x01:
        ln = struct.unpack("<H", recv_exact(s, 2))[0]
        payload = struct.pack("<H", ln) + recv_exact(s, ln)
    elif t == 0x02:
        ln = struct.unpack("<H", recv_exact(s, 2))[0]
        payload = struct.pack("<H", ln) + recv_exact(s, ln)
    elif t == 0x07:
        payload = recv_exact(s, 3)
    elif t in (0x08, 0x0A, 0x0B, 0x0C):
        payload = recv_exact(s, 1)
    else:
        payload = b""
    return t, payload

def parse_maze(payload):
    w, h = payload[0], payload[1]
    return w, h, list(payload[2:])

def deduce_candidates(cell_byte, results):
    bits = [1, 2, 4, 8]
    goods = set()
    for n in bits:
        for s in bits:
            for w in bits:
                for e in bits:
                    if len({n, s, w, e}) < 4:
                        continue
                    ok = True
                    for d, want in results.items():
                        bit = {"N": n, "S": s, "W": w, "E": e}[d]
                        has_wall = bool(cell_byte & bit)
                        if (want == "wall") != has_wall:
                            ok = False
                            break
                    if ok:
                        goods.add((n, s, w, e))
    return goods

def probe_cell(s, w, h, cells, x, y, player_id, our_xy):
    """Probe one cell and return candidates + current_xy"""
    idx = y * w + x
    cell_byte = cells[idx]
    print(f"[PROBE] Cell ({x},{y}) byte 0x{cell_byte:02x}")
    results = {}

    for d, (dx, dy, cmd) in MOVES.items():
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            results[d] = "wall"
            continue
        s.send(bytes([cmd]))
        got = None
        start = time.time()
        while time.time() - start < 1.0:
            try:
                t, p = read_message(s, timeout=0.7)
            except (socket.timeout, ConnectionError):
                break
            if t == 0x05:
                got = "wall"
                break
            elif t == 0x07:
                pid, px, py = p[0], p[1], p[2]
                if pid == player_id and (px, py) != our_xy:
                    got = "open"
                    # move back
                    s.send(bytes([MOVES[OPP[d]][2]]))
                    while True:
                        try:
                            t2, p2 = read_message(s, timeout=0.7)
                        except (socket.timeout, ConnectionError):
                            break
                        if t2 == 0x07 and p2[0] == player_id:
                            our_xy = (p2[1], p2[2])
                            break
                    break
        if got:
            results[d] = got
            print(f"  [TRY] {d} -> {got}")
        else:
            print(f"  [TRY] {d} -> no response")

    print(f"  [RESULT] {results}")
    candidates = deduce_candidates(cell_byte, results)
    print(f"  [CANDIDATES] {len(candidates)} possible\n")
    return candidates, our_xy

def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    player_id = None
    w = h = 0
    cells = []
    our_x = our_y = None

    print("[*] Syncing with server...")
    while True:
        t, payload = read_message(s, timeout=5.0)
        if t == 0x00:
            player_id, maxp = payload
            print(f"[SERVER] Player {player_id+1}/{maxp}")
        elif t == 0x01:
            ln = struct.unpack("<H", payload[:2])[0]
            maze_payload = payload[2:]
            w, h = maze_payload[0], maze_payload[1]
            cells = list(maze_payload[2:])
            print(f"[SERVER] Maze {w}x{h}")
        elif t == 0x07:
            pid, px, py = payload
            if pid == player_id:
                our_x, our_y = px, py
                print(f"[POS] ({px},{py})")
        elif t == 0x08:
            pid = payload[0]
            if pid == player_id:
                break

    all_candidates = None
    probes_done = 0
    current_xy = (our_x, our_y)

    while probes_done < 3:
        cands, current_xy = probe_cell(
            s, w, h, cells, current_xy[0], current_xy[1], player_id, current_xy
        )
        if all_candidates is None:
            all_candidates = cands
        else:
            all_candidates &= cands
        print(f"[INTERSECT] {len(all_candidates)} remain after {probes_done+1} probes")
        probes_done += 1

        if not all_candidates or len(all_candidates) <= 1:
            break

        # auto move one cell south (if possible)
        dx, dy, cmd = MOVES["S"]
        nx, ny = current_xy[0] + dx, current_xy[1] + dy
        if 0 <= nx < w and 0 <= ny < h:
            print(f"[MOVE] Stepping South to ({nx},{ny})")
            s.send(bytes([cmd]))
            while True:
                try:
                    t2, p2 = read_message(s, timeout=0.7)
                except (socket.timeout, ConnectionError):
                    break
                if t2 == 0x07 and p2[0] == player_id:
                    current_xy = (p2[1], p2[2])
                    print(f"[POS] Now at {current_xy}")
                    break
        else:
            print("[STOP] Can't move further south.")
            break

    print("\n=== FINAL CANDIDATE MAPPINGS ===")
    if not all_candidates:
        print("No valid mapping found (ambiguous data). Try again.")
    else:
        for (n, sbit, wbit, ebit) in sorted(all_candidates):
            print(f"N=0x{n:02x} S=0x{sbit:02x} W=0x{wbit:02x} E=0x{ebit:02x}")

    s.close()
    print("[DONE]")

if __name__ == "__main__":
    main()

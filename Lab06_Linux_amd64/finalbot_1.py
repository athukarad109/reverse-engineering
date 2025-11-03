#!/usr/bin/env python3
# testbot_resilient.py
import socket, struct, sys, time
from collections import deque, defaultdict

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.2.15"
PORT = 8008

# Commands (from client handle_input)
CMD = {"N":0x10, "S":0x12, "W":0x11, "E":0x0f,
       "JN":0x14,"JS":0x16,"JW":0x15,"JE":0x13}

# Wall bits (as we've been using; keep but we also allow learning)
# Corrected wall bits — high nibble encoding
N_BIT, S_BIT, W_BIT, E_BIT = 0x10, 0x40, 0x80, 0x20

DIRS = {
    "N": (0,-1,N_BIT,CMD["N"]),
    "S": (0, 1,S_BIT,CMD["S"]),
    "W": (-1,0,W_BIT,CMD["W"]),
    "E": (1, 0,E_BIT,CMD["E"]),
}
OPP = {"N":"S","S":"N","W":"E","E":"W"}

def recv_exact(s, n):
    data = b""
    while len(data) < n:
        chunk = s.recv(n-len(data))
        if not chunk:
            raise ConnectionError("socket closed")
        data += chunk
    return data

def read_msg(s):
    t = recv_exact(s,1)[0]
    payload = b""
    if t == 0x00:
        payload = recv_exact(s,2)           # player, max_players
    elif t == 0x01:
        ln = struct.unpack("<H", recv_exact(s,2))[0]
        payload = recv_exact(s, ln)         # maze raw
    elif t == 0x02:
        ln = struct.unpack("<H", recv_exact(s,2))[0]
        payload = recv_exact(s, ln)         # compressed (not used)
    elif t == 0x07:
        payload = recv_exact(s,3)           # pos update: pid, x, y
    elif t in (0x05, 0x06, 0x08, 0x0A, 0x0B, 0x0C, 0x0E):
        # some of these have 1 byte payload
        if t in (0x05, 0x06):
            payload = b""                   # no extra bytes according to runs
        else:
            # 0x08 and others have 1-byte payload
            payload = recv_exact(s,1)
    else:
        # unknown types - try no payload to avoid blocking
        payload = b""
    return t, payload

def idx_of(x,y,w,h):
    # **CRITICAL**: server uses column-major: bytes go x-major then y.
    return x * h + y

def parse_maze(payload):
    # payload[0]=w, payload[1]=h, then w*h bytes
    w, h = payload[0], payload[1]
    cells = list(payload[2:])
    return w, h, cells

def draw_ascii(w,h,cells,pos=None,visited=None):
    if visited is None: visited=set()
    print("\n=== ASCII Maze (server-aligned) ===")
    for y in range(h):
        # top row of cells
        top = "+"
        for x in range(w):
            top += "---+" if (cells[idx_of(x,y,w,h)] & N_BIT) else "   +"
        print(top)
        mid = "|"
        for x in range(w):
            ch = "0" if pos==(x,y) else ("." if (x,y) in visited else " ")
            mid += f" {ch} "
            mid += "|" if (cells[idx_of(x,y,w,h)] & E_BIT) else " "
        print(mid)
    print("+" + "---+" * w)

def can_move(cells,w,h,x,y,d,blocked):
    dx,dy,bit,cmd = DIRS[d]
    i = idx_of(x,y,w,h)
    # if we've recorded blocked directed edge, deny
    if (x,y,d) in blocked:
        return False
    if cells[i] & bit:
        return False
    nx,ny = x+dx, y+dy
    if not (0<=nx<w and 0<=ny<h):
        return False
    j = idx_of(nx,ny,w,h)
    opp_bit = DIRS[OPP[d]][2]
    if cells[j] & opp_bit:
        return False
    return True

def bfs_to_unvisited(cells,w,h,start,visited,blocked):
    q = deque([ (start,[]) ])
    seen = {start}
    while q:
        (x,y),path = q.popleft()
        if (x,y) not in visited and (x,y)!=start:
            return path
        for d in ("N","S","W","E"):
            if not can_move(cells,w,h,x,y,d,blocked):
                continue
            dx,dy,_,_ = DIRS[d]
            nx,ny = x+dx,y+dy
            if (nx,ny) in seen: continue
            seen.add((nx,ny))
            q.append(((nx,ny), path+[d]))
    return []

def send_cmd_and_handle_response(s, cmd_byte, expect_pos_for_player=None, timeout=0.15):
    # send, then read any immediate server messages (non-blocking style):
    s.send(bytes([cmd_byte]))
    # give server tiny time to respond
    s.settimeout(timeout)
    got_msgs = []
    try:
        # read as many immediate messages as available (single read loop)
        while True:
            t,p = read_msg(s)
            got_msgs.append((t,p))
            # stop if message is not the "turn announcement" (0x08)
            # but we still gather all immediate msgs
    except socket.timeout:
        pass
    except ConnectionError:
        pass
    finally:
        s.settimeout(None)
    return got_msgs

def main():
    s = socket.socket()
    s.connect((HOST,PORT))
    print(f"Connected to {HOST}:{PORT}")
    player = None
    w=h=0
    cells=[]
    pos=None
    visited=set()
    blocked = set()  # directed edges that we learned are blocked: (x,y,dir)

    # the main loop: read incoming messages and react
    while True:
        t,p = read_msg(s)

        if t == 0x00:
            player, maxp = p[0], p[1]
            print(f"Player {player+1}/{maxp}")

        elif t == 0x01:
            w,h,cells = parse_maze(p)
            print(f"[MAZE] Received {w}x{h} ({len(cells)} bytes)")
            # debug cell 0,0
            print(f"[CHECK] cell(0,0)=0x{cells[idx_of(0,0,w,h)]:02x}")
            draw_ascii(w,h,cells,pos,visited)

        elif t == 0x07:
            pid, x, y = p[0], p[1], p[2]
            print(f"[POS] Player {pid} -> ({x},{y})")
            if pid == player:
                pos = (x,y)
                visited.add(pos)

        elif t == 0x08:
            # it's someone's turn; p[0] is player id
            pid = p[0]
            print(f"[TURN] Player {pid+1}")
            if pid != player:
                continue
            if pos is None:
                print("[WAIT] Haven't received our initial position yet.")
                continue

            # plan a path to nearest unvisited
            path = bfs_to_unvisited(cells,w,h,pos,visited,blocked)
            if not path:
                print("[BFS] No unvisited reachable cells (fully explored). Idle.")
                draw_ascii(w,h,cells,pos,visited)
                continue

            d = path[0]
            dx,dy,bit,cmd = DIRS[d]
            nx,ny = pos[0]+dx, pos[1]+dy

            print(f"[TRY] -> {d} cmd=0x{cmd:02x} attempting move from {pos} -> {(nx,ny)}")
            # DEBUG: print the two bytes we rely on
            cur_byte = cells[idx_of(pos[0],pos[1],w,h)]
            if 0 <= nx < w and 0 <= ny < h:
                nbr_byte = cells[idx_of(nx,ny,w,h)]
            else:
                nbr_byte = None
            print(f"       cur_byte=0x{cur_byte:02x} neighbor_byte={None if nbr_byte is None else hex(nbr_byte)}")
            # Attempt the move and capture immediate server messages
            got = send_cmd_and_handle_response(s, cmd, expect_pos_for_player=player)
            illegal = any(m[0]==0x05 for m in got)
            # If server sent a position update for us, update local pos accordingly
            pos_updated = False
            for (mt,mp) in got:
                if mt == 0x07:
                    pid2,x2,y2 = mp[0],mp[1],mp[2]
                    if pid2 == player:
                        pos = (x2,y2)
                        visited.add(pos)
                        pos_updated = True
                elif mt == 0x0C:
                    print("[WIN] Someone won!")
                elif mt == 0x0E:
                    print("[SERVER] Terminated.")
                    return
            if illegal:
                print("[!] Illegal Move — server rejected step.")
                # record this directed edge as blocked to avoid trying again
                blocked.add((pos[0],pos[1],d))
                # also don't change pos
            else:
                # if server didn't send explicit pos update, we optimistically update
                if not pos_updated:
                    pos = (nx,ny)
                    visited.add(pos)
                print(f"[MOVE] success -> {pos} (visited={len(visited)})")

        elif t == 0x05:
            print("[!] Illegal Move (async msg)")

        elif t == 0x0C:
            pid = p[0]
            print(f"[WIN] Player {pid+1} wins!")
            break

        elif t == 0x0E:
            print("[SERVER] Terminated")
            break

if __name__ == "__main__":
    main()

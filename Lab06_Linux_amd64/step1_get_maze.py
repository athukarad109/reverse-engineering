#!/usr/bin/env python3
import socket, struct, sys

HOST = sys.argv[1] if len(sys.argv)>1 else "10.0.2.15"
PORT = 8008
MSGFLAGS = socket.MSG_WAITALL

def recv_exact(s,n):
    buf=b""
    while len(buf)<n:
        chunk=s.recv(n-len(buf),MSGFLAGS)
        if not chunk: raise ConnectionError("closed")
        buf+=chunk
    return buf

def parse_maze(payload):
    w,h=payload[0],payload[1]
    return w,h,list(payload[2:])

def draw_maze(w,h,cells,N,S,W,E,title):
    def c(x,y): return cells[y*w+x]
    print(f"\n=== {title} ===")
    top="+"
    for x in range(w):
        top+="--" if c(x,0)&N else "  "
        top+="+"
    print(top)
    for y in range(h):
        row=""
        for x in range(w):
            row+="|" if c(x,y)&W else " "
            row+="  "
        row+="|" if c(w-1,y)&E else " "
        print(row)
        line="+"
        for x in range(w):
            line+="--" if c(x,y)&S else "  "
            line+="+"
        print(line)

def main():
    s=socket.socket()
    s.connect((HOST,PORT))
    print(f"Connected to {HOST}:{PORT}")

    while True:
        t=recv_exact(s,1)[0]
        if t==0x00: _=recv_exact(s,2)
        elif t==0x01:
            ln,=struct.unpack("<H",recv_exact(s,2))
            payload=recv_exact(s,ln)
            w,h,cells=parse_maze(payload)
            break
        elif t==0x02:
            ln,=struct.unpack("<H",recv_exact(s,2))
            _=recv_exact(s,ln)
            break
        elif t in (0x07,0x08,0x0A,0x0B,0x0C): _=recv_exact(s,1)
        elif t in (0x05,0x06,0x0D): pass
        elif t==0x0E: return

    draw_maze(w,h,cells,4,1,2,8,"Old mapping N=4 S=1 W=2 E=8")
    draw_maze(w,h,cells,4,1,8,2,"Swapped mapping N=4 S=1 W=8 E=2")

if __name__=="__main__":
    main()

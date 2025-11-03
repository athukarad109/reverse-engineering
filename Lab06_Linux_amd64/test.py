# bit_test_v2.py
maze_hex = """
18 11 1d 1c 11 1d 15 15 1d 14 
13 15 16 13 1c 12 19 1c 13 1c 
19 15 1d 14 13 1c 1a 13 15 1e 
13 1c 13 15 1c 1a 13 1c 19 16 
19 16 19 1d 16 13 15 16 13 1c 
12 19 16 1a 19 1d 15 15 1c 1a 
19 16 11 16 1a 13 1c 19 16 1a 
1a 19 15 1c 1a 18 1a 12 19 16 
1b 16 18 13 16 1a 13 1c 13 1c 
13 15 17 15 15 17 14 13 15 16
""".replace("\n"," ").strip()

maze_bytes = bytes.fromhex(maze_hex)
w = h = 10

orders = [
    "NESW","NSWE","ENWS","ESWN","SENW","SWNE","WNES","WESN"
]

def draw(cells, w, h, order):
    dirs = "NESW"
    bits = [dirs.index(c) for c in order]
    def wall(v,d): return bool(v & (1<<bits[d]))
    print(f"\n=== {order} ===")
    for y in range(h):
        top = "+"
        for x in range(w):
            v=cells[y*w+x]
            top += "---+" if wall(v,0) else "   +"
        print(top)
        mid="|"
        for x in range(w):
            v=cells[y*w+x]
            mid += "   |" if wall(v,1) else "    "
        print(mid)
    print("+"+"---+"*w)

for o in orders:
    draw(maze_bytes,w,h,o)

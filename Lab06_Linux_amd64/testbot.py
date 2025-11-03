import socket, struct

HOST = '10.0.2.15'
PORT = 8008

def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data), socket.MSG_WAITALL)
        if not chunk:
            raise ConnectionError("Socket connection lost")
        data += chunk
    return data

def parse_maze(data):
    w, h = data[0], data[1]
    cells = data[2:]
    print(f"Maze size: {w}x{h}")
    print("Maze layout:")
    for y in range(h):
        row = ''
        for x in range(w):
            b = cells[y * w + x]
            row += f"{b:02x} "
        print(row)


s = socket.socket()
s.connect((HOST, PORT))
print(f"Connected to server: {HOST}:{PORT}")

player_num = None
max_players = None
maze = None


while True:
    msg = s.recv(1, socket.MSG_WAITALL)
    if not msg:
        break
    msg_type = msg[0]

    if msg_type == 0x00:
        player_num = recv_exact(s, 1)[0]
        max_players = recv_exact(s, 1)[0]
        print(f"Player {player_num + 1} of {max_players} connected.")

    elif msg_type == 0x01:
        size_bytes = recv_exact(s, 2)
        (lenght,) = struct.unpack('>H', size_bytes)
        payload = recv_exact(s, lenght)
        parse_maze(payload)

    elif msg_type == 0x02:
        raise NotImplementedError("Compressed maze data not supported yet")
    
    elif msg_type == 0x08:
        player_id = s.recv(1, socket.MSG_WAITALL)[0]
        print(f"Player {player_id + 1}'s turn!")
        if player_id == player_num:
            print("It's my turn! next step will choose move here.")

    elif msg_type == 0x0A:
        pid = s.recv(1, socket.MSG_WAITALL)[0]
        print(f"Player {pid + 1} has joined the game!")

    elif msg_type == 0x07:
        data = s.recv(3, socket.MSG_WAITALL)
        pid, x, y = data
        print(f"[i] Plyer {pid + 1} position updated to ({x}, {y})")

    else:
        print(f"Unknown message type: {msg_type}")
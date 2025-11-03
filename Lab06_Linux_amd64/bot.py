#!/usr/bin/env python3

import socket
s = socket.socket()

#define the IP and port in seperate vars later

s.connect(("10.0.2.15", 8008))

while True:
    msg_type = s.recv(1, socket.MSG_WAITALL)
    if msg_type == 0:
        player_num = s.recv(1, socket.MSG_WAITALL)
        max_players = s.recv(1, socket.MSG_WAITALL)
        print(f"Player {player_num} of {max_players} connected.")
    elif msg_type == 1:
        #maze data
        maze_size = s.recv(2, socket.MSG_WAITALL)
    elif msg_type == 2:
        raise Exception("Not supported yet")
    elif msg_type == 8:
        player_id = s.recv(1, socket.MSG_WAITALL)
        print(f"Player {player_id+1}'s turn!")
        if player_id == player_num:
            print("todo_compute_and_send_move()")
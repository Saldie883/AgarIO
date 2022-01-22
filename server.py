import socket
import pickle
from copy import deepcopy
import threading
import sys
import random
from os import system

import codes as code


def recv_all_data(server, players_data, cells_data):
    print("Recieving...")

    # player data:
    #   { pos = (x, y)
    #     color = (r, g, b)
    #     mass = int }

    while True:
        data, addr = recieve(server)

        if data['code'] == code.CONNECT_REQUEST:
            new_player_pos = (random.randint(0, MAPSIZE), random.randint(0, MAPSIZE))
            new_player_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            players_data[addr] = {'pos': new_player_pos, 'color': new_player_color, 'mass': 20}

            print(f"Connected {addr}")
            send({'code': code.CONNECTED, 'addr': addr, 'cells': cells_data, 'players': players_data, \
                'mapsize': MAPSIZE, 'coords': new_player_pos, 'color': new_player_color}, addr)

        elif data['code'] == code.DATA_SEND:
            players_data[addr] = data

        elif data['code'] == code.CELL_EAT:
            del cells_data[data['cell']]
            print(f"got eaten cell: {data['cell']} ({len(cells_data)})")


def sync_data(players_data, cells_data):
    print("Sync started...")

    while True:
        cd = deepcopy(cells_data)
        pd = deepcopy(players_data)

        for p in players_data.copy():
            send({"code": code.DATA_SEND, "cells": cd, "players": pd}, p)


def send(data, client):
    server.sendto(pickle.dumps(data), client)


def recieve(server):
    data, addr = server.recvfrom(2048)
    return (pickle.loads(data), addr)


def make_cell(mapsize):
    return ((random.randint(10, mapsize-10), random.randint(10, mapsize-10)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))


HOST, PORT = 'localhost', 7777
GAMEEND = False

addr = (HOST, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(addr)

MAPSIZE = 2000
CELLS_AMOUNT = MAPSIZE//20
CELLS_DATA = dict()

for _ in range(CELLS_AMOUNT):
    new_cell = make_cell(MAPSIZE)

    CELLS_DATA[new_cell[0]] = new_cell[1]

system("CLS")
# -------------------------------------------------------

print("\t\t[ Server started ]")

PLAYERS_DATA = {}
recv_thread = threading.Thread(target=recv_all_data, args=(server, PLAYERS_DATA, CELLS_DATA))
send_thread = threading.Thread(target=sync_data, args=(PLAYERS_DATA, CELLS_DATA))


recv_thread.start()
send_thread.start()

if GAMEEND:
    server.close()

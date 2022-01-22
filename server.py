import socket
import pickle
from copy import deepcopy
import threading
import sys
from os import system

import codes as code
import time
from tools import *
import settings


def recv_all_data(server, players_data, cells_data):
    print("Recieving...")

    while True:
        try:
            data, addr = recieve(server)
        except ConnectionResetError:
            continue

        # Player connects
        if data['code'] == code.CONNECT_REQUEST:
            new_player_pos = (random.randint(0, MAPSIZE), random.randint(0, MAPSIZE))
            new_player_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            players_data[addr] = {'pos': new_player_pos, 'color': new_player_color, 'mass': 20}

            print(f"Connected {addr}")
            send({'code': code.CONNECTED, 'addr': addr, 'cells': cells_data, 'players': players_data, \
                'mapsize': MAPSIZE, 'coords': new_player_pos, 'color': new_player_color}, addr)

        # Recieve update from player
        elif data['code'] == code.DATA_SEND:
            players_data[addr] = data

        # Player eats cell
        elif data['code'] == code.CELL_EAT:
            print(f"cell at {data['cell']} eated")
            if data['cell'] in cells_data:
                del cells_data[data['cell']]

        # Player eats enemy 
        elif data['code'] == code.ENEMY_EAT:
            send({'code': code.DIED}, data['player'])
            del players_data[data['player']]

        # Player disconnects
        elif data['code'] == code.DISCONNECT:
            del players_data[addr]



def sync_data(players_data, cells_data):
    print("Sync started...")

    while True:
        # Generating new cells if old have been eaten
        while len(cells_data) < CELLS_AMOUNT:
            new_cell = make_cell(MAPSIZE)
            cells_data[new_cell[0]] = new_cell[1]

        cd = deepcopy(cells_data)
        pd = deepcopy(players_data)

        # Splitting all cells into tiles
        # Matrix of tiles
        tiles_data = []
        for _ in range(TILESAMOUNT):
            row = []
            for _ in range(TILESAMOUNT):
                row.append(dict())
            tiles_data.append(row)

        for c, color in cells_data.items():
            cell_tile = get_tile_of_point(*c, TILESIZE)
            tiles_data[cell_tile[1]][cell_tile[0]][c] = color

        # Splitting all enemies into tiles
        # Matrix of enemies
        enemies_data = []
        for _ in range(TILESAMOUNT):
            row = []
            for _ in range(TILESAMOUNT):
                row.append(dict())
            enemies_data.append(row)

        for enemy, info in players_data.items():
            enemy_tile = get_tile_of_point(*info['pos'], TILESIZE)
            enemies_data[enemy_tile[1]][enemy_tile[0]][enemy] = info

        # Sending data to players based on their tile
        for player, info in players_data.copy().items():
            ptx, pty = get_tile_of_point(*info['pos'], TILESIZE)

            cells_for_player = get_item_from_matrix(tiles_data, ptx-1, pty-1) | get_item_from_matrix(tiles_data, ptx-1, pty) | get_item_from_matrix(tiles_data, ptx-1, pty+1) | \
                               get_item_from_matrix(tiles_data, ptx, pty-1)   | get_item_from_matrix(tiles_data, ptx, pty)   | get_item_from_matrix(tiles_data, ptx, pty+1)   | \
                               get_item_from_matrix(tiles_data, ptx+1, pty-1) | get_item_from_matrix(tiles_data, ptx+1, pty) | get_item_from_matrix(tiles_data, ptx+1, pty+1)

            enemies_for_player = get_item_from_matrix(enemies_data, ptx-1, pty-1) | get_item_from_matrix(enemies_data, ptx-1, pty) | get_item_from_matrix(enemies_data, ptx-1, pty+1) | \
                                 get_item_from_matrix(enemies_data, ptx, pty-1)   | get_item_from_matrix(enemies_data, ptx, pty)   | get_item_from_matrix(enemies_data, ptx, pty+1)   | \
                                 get_item_from_matrix(enemies_data, ptx+1, pty-1) | get_item_from_matrix(enemies_data, ptx+1, pty) | get_item_from_matrix(enemies_data, ptx+1, pty+1)

            send({"code": code.DATA_SEND, "cells": cells_for_player, "players": enemies_for_player}, player)


def send(data, client):
    server.sendto(pickle.dumps(data), client)


def recieve(server):
    data, addr = server.recvfrom(settings.BUFSIZE)
    return (pickle.loads(data), addr)


# Map parameters -----------------------------------------
TILESIZE = 800      # tile size = screen size
TILESAMOUNT = 10
MAPSIZE = TILESIZE * TILESAMOUNT

CELLS_AMOUNT = MAPSIZE//10
CELLS_DATA = dict()

for _ in range(CELLS_AMOUNT):
    new_cell = make_cell(MAPSIZE)
    CELLS_DATA[new_cell[0]] = new_cell[1]

# -------------------------------------------------------

HOST, PORT = 'localhost', 7777
CLOSESERVER = False

addr = (HOST, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(addr)

system("CLS")

# -------------------------------------------------------

print("\t\t[ Server started ]")

PLAYERS_DATA = {}
recv_thread = threading.Thread(target=recv_all_data, args=(server, PLAYERS_DATA, CELLS_DATA))
send_thread = threading.Thread(target=sync_data, args=(PLAYERS_DATA, CELLS_DATA))

recv_thread.start()
send_thread.start()

if CLOSESERVER:
    server.close()

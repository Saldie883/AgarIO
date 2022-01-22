import pygame
import random
from math import sqrt


# Check collision between rect and circle
def collision(r1x, r1y, r1w, r1h, cx, cy, cr):
    r2x, r2y = cx-cr, cy-cr
    r2w = r2h = cr+cr

    return pygame.Rect(r1x, r1y, r1w, r1h).colliderect(pygame.Rect(r2x, r2y, r2w, r2h))


# Check if point in circle (for enemy eating)
def point_in_cirlce(cx, cy, r, x, y):
    return sqrt((x-cx)**2 + (y-cy)**2) < r


# Make new cell
def make_cell(mapsize):
    return ((random.randint(10, mapsize-10), random.randint(10, mapsize-10)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))


def get_tile_of_point(x, y, tilesize):
    return (int(x/tilesize), int(y/tilesize))

# Get cells located in tile (tx, ty)
def get_cells_for_tile(cells, tx, ty, tilesize):
    return set(filter(lambda c: c[0]//tilesize == tx and c[1]//tilesize == ty, cells))


def get_item_from_matrix(matrix, x, y):
    if x < 0 or x >= len(matrix) or y < 0 or y >= len(matrix):
        return dict()
    else:
        return matrix[y][x]


# TILESAMOUNT = 10
# TILESIZE = 30


# cells_data = {(161, 73): 1, (266, 44): 1, (17, 215): 1, (22, 163): 1, (60, 224): 1, (244, 89): 1, (197, 144): 1, (273, 10): 1, (165, 44): 1, (117, 55): 1, (280, 2): 1, (107, 157): 1, (277, 291): 1, (234, 59): 1, (81, 196): 1, (290, 71): 1, (86, 119): 1, (101, 74): 1, (155, 5): 1, (40, 12): 1, (179, 11): 1, (21, 0): 1, (153, 192): 1, (134, 82): 1, (68, 121): 1, (175, 237): 1, (26, 164): 1, (14, 91): 1, (65, 261): 1, (120, 188): 1, (116, 174): 1, (230, 298): 1, (34, 26): 1, (30, 106): 1, (227, 206): 1, (9, 81): 1, (292, 1): 1, (78, 261): 1, (223, 25): 1, (147, 103): 1}

# tiles_data = []
# for _ in range(TILESAMOUNT):
#     row = []
#     for _ in range(TILESAMOUNT):
#         row.append(dict())
#     tiles_data.append(row)


# for c, color in cells_data.items():
#     cell_tile = get_tile_of_point(*c, TILESIZE)
#     tiles_data[cell_tile[1]][cell_tile[0]][c] = color



# for r in tiles_data:
#     for e in r:
#         print(f"{e}   |   ", end = '')
#     print()


# ptx, pty = 1, 2

# cells_for_player = get_item_from_matrix(tiles_data, ptx-1, pty-1) | get_item_from_matrix(tiles_data, ptx-1, pty) | get_item_from_matrix(tiles_data, ptx-1, pty+1) | \
#                    get_item_from_matrix(tiles_data, ptx, pty-1)   | get_item_from_matrix(tiles_data, ptx, pty)   | get_item_from_matrix(tiles_data, ptx, pty+1)   | \
#                    get_item_from_matrix(tiles_data, ptx+1, pty-1) | get_item_from_matrix(tiles_data, ptx+1, pty) | get_item_from_matrix(tiles_data, ptx+1, pty+1)

# print(cells_for_player)

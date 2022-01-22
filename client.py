import pygame
from pygame.locals import K_w, K_a, K_s, K_d, K_i
from math import sqrt, hypot
import pickle
import sys
import random
import codes as code
import socket

pygame.init()
SCREEN_SIZE = [800, 800]

screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

elapsed = 0
FPS = 200
RUNNING = True

PLAYER_COLORS = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(100)]

# ---------------------------

def send_to_server(client, data, server):
    client.sendto(pickle.dumps(data), server)


def recieve_from_server(server):
    try:
        data, addr = server.recvfrom(2048)
        return pickle.loads(data)
    except BlockingIOError:
        return None

# ---------------------------

def collision(r1x, r1y, r1w, r1h, cx, cy, cr):
    r2x, r2y = cx-cr, cy-cr
    r2w = r2h = cr+cr

    return pygame.Rect(r1x, r1y, r1w, r1h).colliderect(pygame.Rect(r2x, r2y, r2w, r2h))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, mass=20, color=None):
        super(Player, self).__init__()
        self.speed = 220
        self.color = color if color else random.choice(PLAYER_COLORS)

        self.mass = mass
        self.x = x
        self.y = y


    def update(self, time, camera, cells, borders):
        # Moving

        if pygame.mouse.get_focused():
            mouse_position = pygame.mouse.get_pos()
            player_position = camera.translate_coords(self)

            x_offset = mouse_position[0]-player_position[0]
            y_offset = mouse_position[1]-player_position[1]

            bef = (self.x, self.y)

            self.x += x_offset * time
            for b in borders:
                if collision(b.x, b.y, b.w, b.h, self.x, self.y, self.mass):
                    self.x = bef[0]
                    break

            self.y += y_offset * time
            for b in borders:
                if collision(b.x, b.y, b.w, b.h, self.x, self.y, self.mass):
                    self.y = bef[1]
                    break

        # Eating cells
        for c in cells.copy():
            if sqrt((c.x-self.x)**2 + (c.y-self.y)**2) < c.mass + self.mass:
                self.mass += c.mass
                cells.remove(c)

                send_to_server(client, {"code": code.CELL_EAT, "cell": (c.x, c.y)}, (HOST, PORT))



    def draw(self, screen, camera):
        pygame.draw.circle(screen, self.color, camera.translate_coords(self), self.mass)



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, mass, color=None):
        super(Enemy, self).__init__()
        self.mass = mass
        self.x = x
        self.y = y
        self.color = color if color else random.choice(PLAYER_COLORS)


    def draw(self, screen, camera):
        pygame.draw.circle(screen, self.color, camera.translate_coords(self), self.mass)



class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, mass=0.5, color=None):
        super(Cell, self).__init__()
        self.mass = mass
        self.x = x
        self.y = y
        self.color = color if color else random.choice(PLAYER_COLORS)


    def draw(self, screen, camera):
        pygame.draw.circle(screen, self.color, camera.translate_coords(self), self.mass*10)



class Border(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(254, 113, 113)):
        super(Border, self).__init__()

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color


    def draw(self, screen, camera):
        pygame.draw.rect(screen, self.color, (*camera.translate_coords(self), self.w, self.h))



class Camera():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.ow = w
        self.oh = h

        self.scale = 1


    def translate_coords(self, obj):
        return (obj.x-(self.x-(self.w//2)), obj.y-(self.y-(self.h//2)))


    def update(self, player):
        self.x = player.x
        self.y = player.y


# connecting to server ---------------


HOST, PORT = 'localhost', 7777

print(f"Connecting to {HOST}:{PORT}")
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.setblocking(False)

send_to_server(client, {"code": code.CONNECT_REQUEST}, (HOST, PORT))

connected = False
print("waiting for connection")
while not connected:
    data = recieve_from_server(client)

    if not data:
        continue

    if data["code"] == code.CONNECTED:
        print("Connected")

        MAPSIZE = data['mapsize']
        player_coordinates = data['coords']
        player_color = data['color']
        player_address = data['addr']

        cells = pygame.sprite.Group()
        for c in data['cells']:
            cells.add(Cell(*c, color=data['cells'][c]))

        enemies = set()
        for enemy, info in data['players'].items():
            if enemy == player_address:
                continue
            enemies.add(Enemy(*info['pos'], color=info['color'], mass=info['mass']))

        connected = True

    elif data['code'] == code.DATA_SEND:
        pass

    else:
        print("Can't connect")
        sys.exit()


# ------------------------------------

player = Player(*player_coordinates, color=player_color)
camera = Camera(player.x, player.y, *SCREEN_SIZE)
borders = (Border(0, 0, 5, MAPSIZE), Border(0, 0, MAPSIZE, 5), Border(MAPSIZE, 0, 5, MAPSIZE), Border(0, MAPSIZE, MAPSIZE, 5))

print("\n\n\tStarted game")
# Game loop --------------------------------------------
while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False

    # Getting fresh data -------------------------------

    fresh_data = None

    # getting latest data
    while True:
        data = recieve_from_server(client)

        if data:
            fresh_data = data
        else:
            break

    # working with latest data
    if fresh_data:
        cells = set()
        for c in fresh_data['cells']:
            cells.add(Cell(*c, color=fresh_data['cells'][c]))

        enemies = set()
        for enemy, info in fresh_data['players'].items():
            if enemy == player_address:
                continue
            enemies.add(Enemy(*info['pos'], color=info['color'], mass=info['mass']))


    # --------------------------------------------------

    player.update(elapsed, camera, cells, borders)
    camera.update(player)


    # Drawing ------------------------------------------
    screen.fill((35, 35, 35))

    # Else



    player.draw(screen, camera)

    for c in cells:
        c.draw(screen, camera)

    for e in enemies:
        e.draw(screen, camera)

    for b in borders:
        b.draw(screen, camera)

    # Sending fresh info to server ---------------------

    send_to_server(client, {"code": code.DATA_SEND, "pos": (player.x, player.y), "color": player.color, "mass": player.mass}, (HOST, PORT))

    # --------------------------------------------------

    pygame.display.flip()
    elapsed = clock.tick(FPS)/1000
    pygame.display.set_caption(str(elapsed))


pygame.quit()

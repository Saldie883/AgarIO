from pygame.locals import K_w, K_a, K_s, K_d, K_i
from math import sqrt, hypot
import pickle
import sys
import random
import codes as code
import socket
from tools import *
import settings

pygame.init()
SCREEN_SIZE = settings.SCREEN_SIZE

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30)
font_s = pygame.font.SysFont('Comic Sans MS', 18)
clock = pygame.time.Clock()

elapsed = 0
RUNNING = True
OBJ_COLORS = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(100)]

# ---------------------------

def send_to_server(client, data, server):
    client.sendto(pickle.dumps(data), server)


def recieve_from_server(server):
    try:
        data, addr = server.recvfrom(settings.BUFSIZE)
        return pickle.loads(data)
    except BlockingIOError:
        return None

# ---------------------------


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, mass=20, color=None):
        super(Player, self).__init__()
        self.speed = 220
        self.color = color if color else random.choice(OBJ_COLORS)

        self.mass = mass
        self.x = x
        self.y = y


    def update(self, time, camera, cells, borders, enemies):
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


        # Eating enemies
        for e in enemies:
            # If enemy center inside player circle and player's mass greater than enemy - player eat enemy
            if point_in_cirlce(self.x, self.y, self.mass, e.x, e.y) and self.mass / e.mass >= 1.2:
                # Sending ENEMY_EAT event to server
                send_to_server(client, {"code": code.ENEMY_EAT, "player": e.addr}, (HOST, PORT))

                self.mass += e.mass * 0.8     # Adding enemy mass to player's mass


    def draw(self, screen, camera):
        pygame.draw.circle(screen, self.color, camera.translate_coords(self), self.mass)



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, mass, addr, nickname, color=None):
        super(Enemy, self).__init__()
        self.mass = mass
        self.x = x
        self.y = y
        self.color = color if color else random.choice(OBJ_COLORS)
        self.addr = addr
        self.nickname = nickname


    def draw(self, screen, camera):
        pygame.draw.circle(screen, self.color, camera.translate_coords(self), self.mass)



class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, mass=0.5, color=None):
        super(Cell, self).__init__()
        self.mass = mass
        self.x = x
        self.y = y
        self.color = color if color else random.choice(OBJ_COLORS)


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

nickname = ""

while len(nickname) < 3 or len(nickname) > 20:
    nickname = input("Enter nickname: ")

print(f"Connecting to {HOST}:{PORT}")
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.setblocking(False)

# Request server for connection (for getting init info)
send_to_server(client, {"code": code.CONNECT_REQUEST, "nickname": nickname}, (HOST, PORT))

connected = False
print("Waiting for connection")
while not connected:
    data = recieve_from_server(client)

    if not data:
        continue

    # Waiting for CONNECTED response from server
    if data["code"] == code.CONNECTED:
        print("Connected")

        # Getting init info
        MAPSIZE = data['mapsize']
        player_coordinates = data['coords']
        player_color = data['color']
        player_address = data['addr']

        cells = set()       # Creating cells
        enemies = set()     # Creating enemies

        connected = True

    elif data['code'] == code.DATA_SEND:
        pass

    else:
        print("Can't connect")
        sys.exit()


# ------------------------------------

print("\n\n\tStarted game")

# Spawning player at position given by server
player = Player(*player_coordinates, color=player_color)
# Configurating the camera according to player position
camera = Camera(player.x, player.y, *SCREEN_SIZE)
# Placing arena borders
borders = (Border(0, 0, 5, MAPSIZE), Border(0, 0, MAPSIZE, 5), Border(MAPSIZE, 0, 5, MAPSIZE), Border(0, MAPSIZE, MAPSIZE, 5))
scoreboard = None

# Game loop --------------------------------------------
while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # If window closes - sending DISCONNECT code to server for handling this event
            send_to_server(client, {"code": code.DISCONNECT}, (HOST, PORT))
            RUNNING = False

    # Getting relevant data -------------------------------
    relevant_data = None

    # Getting latest data
    while True:
        data = recieve_from_server(client)

        if data:
            if data['code'] == code.DIED:
                sys.exit()

            relevant_data = data
        else:
            break

    # working with latest data
    if relevant_data:
        cells = set()
        for c in relevant_data['cells']:
            cells.add(Cell(*c, color=relevant_data['cells'][c]))

        enemies = set()
        for enemy, info in relevant_data['players'].items():
            if enemy == player_address:
                continue
            enemies.add(Enemy(*info['pos'], addr=enemy, color=info['color'], mass=info['mass'], nickname=info['nickname']))

        scoreboard = relevant_data['scoreboard']


    # Updating -----------------------------------------
    player.update(elapsed, camera, cells, borders, enemies)
    camera.update(player)

    # Drawing ------------------------------------------
    screen.fill((35, 35, 35))

    player.draw(screen, camera)

    for c in cells:
        c.draw(screen, camera)

    for e in enemies:
        e.draw(screen, camera)
        nickname_rendered = font_s.render(e.nickname, False, (255, 255, 255))
        nick_coords = camera.translate_coords(e)
        screen.blit(nickname_rendered, (nick_coords[0]-nickname_rendered.get_width()//2, nick_coords[1]-nickname_rendered.get_height()//2))    


    for b in borders:
        b.draw(screen, camera)

    # GUI
    xc = font.render(f"X: {round(player.x, 1)}", False, (255, 255, 255))
    yc = font.render(f"Y: {round(player.y, 1)}", False, (255, 255, 255))
    score = font.render(f"Score: {player.mass}", False, (255, 255, 255))
    nickname_rendered = font_s.render(nickname, False, (255, 255, 255))

    offset_score = SCREEN_SIZE[1]-score.get_height()-10
    offset_y = offset_score-yc.get_height()-10
    offset_x = offset_y-xc.get_height()-10

    screen.blit(xc, (10, offset_x))
    screen.blit(yc, (10, offset_y))
    screen.blit(score, (10, offset_score))
    screen.blit(nickname_rendered, (SCREEN_SIZE[0]//2 - nickname_rendered.get_width()//2, SCREEN_SIZE[1]//2 - nickname_rendered.get_height()//2))

    # Scoreboard
    if scoreboard:
        for pos, (nick, mass) in enumerate(scoreboard.items(), 1):
            text = font.render(f"{pos}. {nick} - {mass}", False, (255, 255, 255))
            print(pos, nick, mass, (10, 10*pos))
            screen.blit(text, (10, 10+(text.get_height()*(pos-1))))

    # Sending relevant info to server ---------------------

    send_to_server(client, {"code": code.DATA_SEND, "pos": (player.x, player.y), "color": player.color, "mass": player.mass, "nickname": nickname}, (HOST, PORT))

    # --------------------------------------------------

    pygame.display.flip()
    elapsed = clock.tick(settings.FPS)/1000
    pygame.display.set_caption("AgarIO")
    pygame.display.set_caption(str(elapsed))

pygame.quit()

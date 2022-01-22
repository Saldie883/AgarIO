import pygame
from pygame.locals import K_w, K_a, K_s, K_d, K_i
from math import atan2,degrees,sin,cos,radians,sqrt
import pickle
import sys
import random

pygame.init()
SCREEN_SIZE = [800, 800]

screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

elapsed = 0
FPS = 200
RUNNING = True

PLAYER_COLORS = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(100)]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, mass=20, color=None):
        super(Player, self).__init__()
        self.speed = 220
        self.color = color if color else random.choice(PLAYER_COLORS)

        self.mass = mass
        self.x = x
        self.y = y


    def update(self, time, pressed_keys, cells):
        if pressed_keys[K_w]:
            self.y -= self.speed * time

        if pressed_keys[K_s]:
            self.y += self.speed * time

        if pressed_keys[K_a]:
            self.x -= self.speed * time

        if pressed_keys[K_d]:
            self.x += self.speed * time


        for c in cells:
            if sqrt((c.x-self.x)**2 + (c.y-self.y)**2) < c.mass + self.mass:
                self.mass += c.mass
                cells.remove(c)



    def draw(self, screen, camera):
        pygame.draw.circle(screen, self.color, camera.translate_coords(self), self.mass)


class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, mass=5, color=None):
        super(Cell, self).__init__()
        self.mass = mass
        self.x = x
        self.y = y
        self.color = color if color else random.choice(PLAYER_COLORS)


    def draw(self, screen, camera):
        pygame.draw.circle(screen, self.color, camera.translate_coords(self), self.mass)


class Camera():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


    def translate_coords(self, obj):
        return (obj.x-(self.x-(self.w//2)), obj.y-(self.y-(self.h//2)))


    def update(self, player):
        self.x = player.x
        self.y = player.y


MAPSIZE = [8000, 8000]

player = Player(4500, 4500)
camera = Camera(player.x, player.y, *SCREEN_SIZE)

cells = pygame.sprite.Group()
cells.add(Cell(random.randint(0, MAPSIZE[0]), random.randint(0, MAPSIZE[1])) for _ in range(2000))

# Game loop --------------------------------------------
while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False

    player.update(elapsed, pygame.key.get_pressed(), cells)
    camera.update(player)


    # Drawing ------------------------------------------
    screen.fill((35, 35, 35))
    player.draw(screen, camera)

    for c in cells:
        c.draw(screen, camera)

    pygame.display.flip()
    elapsed = clock.tick(FPS)/1000
    pygame.display.set_caption(str(elapsed))


pygame.quit()

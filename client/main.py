# Библиотеки
import sys 
import pygame
import math
from pygame.locals import *
import pygame_menu

pygame.init()

# Константы
DISPLAY_WIDTH   = 1280
DISPLAY_HEIGHT  = 720

# Переменные
mainScreen = pygame.display.set_mode([DISPLAY_WIDTH, DISPLAY_HEIGHT])
pygame.display.set_caption("Agar.io")

mainClock = pygame.time.Clock() 

# Меню
menu  = pygame_menu.Menu('Agar.io', DISPLAY_WIDTH, DISPLAY_HEIGHT, theme=pygame_menu.themes.THEME_BLUE)

def start_the_game():
    global gameState, menu 
    name = userNameTextInput.get_value()
    if len(name) < 4:
        print("Имя слишком короткое")
    else:
        menu.disable()

userNameTextInput = menu.add.text_input('Name :', default='Tester')
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)



class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        self.zoom = 0.5

    def centre(self,blobOrPos):
        if isinstance(blobOrPos, Player):
            x, y = blobOrPos.x, blobOrPos.y
            self.x = (x - (x*self.zoom)) - x + (DISPLAY_WIDTH/2)
            self.y = (y - (y*self.zoom)) - y + (DISPLAY_HEIGHT/2)
        elif type(blobOrPos) == tuple:
            self.x, self.y = blobOrPos

    def update(self, target):
        self.zoom = 100/(target.mass)+0.3
        self.centre(player)





cam = Camera()

while (True):
    mainClock.tick(60)
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()

    mainScreen.fill((255, 255, 255))

    if menu.is_enabled():
        menu.mainloop(mainScreen)

    pygame.display.flip()
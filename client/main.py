# Библиотеки
import sys 
import pygame
import math
import random
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
menu = pygame_menu.Menu('Agar.io', DISPLAY_WIDTH, DISPLAY_HEIGHT, theme=pygame_menu.themes.THEME_BLUE)

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


class Drawable:
    """ Абстрактный класс для обрисовки всех элементов
    """
    def __init__(self, surface, camera):
        self.surface = surface
        self.camera = camera

    def draw(self):
        pass

class Grid(Drawable):
    def __init__(self, surface, camera):
        super().__init__(surface, camera)
        self.color = (230,240,240)

    def draw(self):
        zoom = self.camera.zoom
        x, y = self.camera.x, self.camera.y
        for i in range(0,2001,25):
            pygame.draw.line(self.surface,  self.color, (x, i*zoom + y), (2001*zoom + x, i*zoom + y), 3)
            pygame.draw.line(self.surface, self.color, (i*zoom + x, y), (i*zoom + x, 2001*zoom + y), 3)

class Cell(Drawable): 
    """ Класс клеток которые игроки поднимают """
    CELL_COLORS = 
    [ # Цвета для клеток
        (80,252,54),
        (36,244,255),
        (243,31,46),
        (4,39,243),
        (254,6,178),
        (255,211,7),
        (216,6,254),
        (145,255,7),
        (7,255,182),
        (255,6,86),
        (147,7,255)
    ]
    
    def __init__(self, surface, camera):
        super().__init__(surface, camera)
        self.x = random.randint(20,1980)
        self.y = random.randint(20,1980)
        self.mass = 7
        self.color = random.choice(Cell.CELL_COLORS)

    def draw(self):
        zoom = self.camera.zoom
        x,y = self.camera.x, self.camera.y
        center = (int(self.x*zoom + x), int(self.y*zoom + y))
        pygame.draw.circle(self.surface, self.color, center, int(self.mass*zoom))

class CellList(Drawable):
    """ Класс группирования клеток """
    def __init__(self, surface, camera, numOfCells):
        super().__init__(surface, camera)
        self.count = numOfCells
        self.list = []
        for i in range(self.count): self.list.append(Cell(self.surface, self.camera))

    def draw(self):
        for cell in self.list:
            cell.draw()

cam = Camera()

grid = Grid(mainScreen, cam)
cells = CellList(mainScreen, cam, 2000)

while (True):
    mainClock.tick(60)
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()

    mainScreen.fill((255, 255, 255))

    if menu.is_enabled():
        menu.mainloop(mainScreen)
    else:
        grid.draw()
        cells.draw()

    pygame.display.flip()
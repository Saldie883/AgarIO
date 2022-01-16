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

font        = pygame.font.SysFont('Ubuntu',20,True)
big_font    = pygame.font.SysFont('Ubuntu',24,True)

# Меню
menu = pygame_menu.Menu('Agar.io', DISPLAY_WIDTH, DISPLAY_HEIGHT, theme=pygame_menu.themes.THEME_BLUE)

def start_the_game():
    global gameState, menu, player
    name = userNameTextInput.get_value()
    if len(name) < 4:
        print("Имя слишком короткое")
    else:
        menu.disable()
        player = Player(mainScreen, cam, name)

userNameTextInput = menu.add.text_input('Name :', default='Tester')
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)

def drawText(message,pos,color=(255,255,255)):
    mainScreen.blit(font.render(message,1,color),pos)

def getDistance(a, b):
    diffX = math.fabs(a[0]-b[0])
    diffY = math.fabs(a[1]-b[1])
    return ((diffX**2)+(diffY**2))**(0.5)


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
    CELL_COLORS = [ # Цвета для клеток
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


class Player(Drawable):
    """ Класс игрока
    """
    COLOR_LIST = [
    (37,7,255),
    (35,183,253),
    (48,254,241),
    (19,79,251),
    (255,7,230),
    (255,7,23),
    (6,254,13)]

    FONT_COLOR = (50, 50, 50)
    
    def __init__(self, surface, camera, name = ""):
        super().__init__(surface, camera)
        self.x = random.randint(100,400)
        self.y = random.randint(100,400)
        self.mass = 20
        self.speed = 4
        self.color = col = random.choice(Player.COLOR_LIST)
        self.outlineColor = (
            int(col[0]-col[0]/3),
            int(col[1]-col[1]/3),
            int(col[2]-col[2]/3))
        if name: self.name = name
        else: self.name = "Test"
        self.pieces = []


    def collisionDetection(self, edibles):
        """ Проверка коллизии
        """
        for edible in edibles:
            if(getDistance((edible.x, edible.y), (self.x,self.y)) <= self.mass/2):
                self.mass+=0.5
                edibles.remove(edible)


    def move(self):
        """ Обновление позиции игрока
        """
    
        dX, dY = pygame.mouse.get_pos()
        rotation = math.atan2(dY - float(DISPLAY_HEIGHT)/2, dX - float(DISPLAY_WIDTH)/2)
        rotation *= 180/math.pi
        normalized = (90 - math.fabs(rotation))/90
        vx = self.speed*normalized
        vy = 0
        if rotation < 0:
            vy = -self.speed + math.fabs(vx)
        else:
            vy = self.speed - math.fabs(vx)
        tmpX = self.x + vx
        tmpY = self.y + vy
        self.x = tmpX
        self.y = tmpY

    def draw(self):
        """ Отрисовка игрока
        """
        zoom = self.camera.zoom
        x, y = self.camera.x, self.camera.y
        center = (int(self.x*zoom + x), int(self.y*zoom + y))
        
        # Отрисовка круга вокруг игрока
        pygame.draw.circle(self.surface, self.outlineColor, center, int((self.mass/2 + 3)*zoom))
        # Отрисовка круга игрока
        pygame.draw.circle(self.surface, self.color, center, int(self.mass/2*zoom))
        # Отрисовка имени игрока
        fw, fh = font.size(self.name)
        drawText(self.name, (self.x*zoom + x - int(fw/2), self.y*zoom + y - int(fh/2)),
                 Player.FONT_COLOR)



cam = Camera()

grid = Grid(mainScreen, cam)
cells = CellList(mainScreen, cam, 2000)
player = None


while True:
    mainClock.tick(60)
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            quit()

    if menu.is_enabled():
        menu.mainloop(mainScreen)
    else:
        player.move()
        player.collisionDetection(cells.list)
        cam.update(player)
        mainScreen.fill((255, 255, 255))
        grid.draw()
        cells.draw()
        player.draw()

    pygame.display.flip()
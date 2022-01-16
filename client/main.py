import pygame
pygame.init()

defaultSize = 24

screen = pygame.display.set_mode([640, 480])

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    pygame.draw.circle(screen, (0, 0, 255), (250, 250), defaultSize)

    pygame.display.flip()

pygame.quit()
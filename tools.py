import pygame
from math import sqrt


# Check collision between rect and circle
def collision(r1x, r1y, r1w, r1h, cx, cy, cr):
    r2x, r2y = cx-cr, cy-cr
    r2w = r2h = cr+cr

    return pygame.Rect(r1x, r1y, r1w, r1h).colliderect(pygame.Rect(r2x, r2y, r2w, r2h))


# Check if point in circle (for enemy eating)
def point_in_cirlce(cx, cy, r, x, y):
    return sqrt((x-cx)**2 + (y-cy)**2) < r

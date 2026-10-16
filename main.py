import pygame
import sys

pygame.init()

#this is a tower defense game, only some very basic base code so far

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Tower Defense Game")

FPS = 60
clock = pygame.time.Clock()
GREEN = (3, 139, 34) #grass background
GRAY = (128, 128, 128) #enemy path

PATH = [(0, 300), (300, 300), (300, 100), (600, 100), (600, 600)]

#this is the main game loop that runs the game
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(GREEN) #fill background with grass
    if len(PATH) > 1:
        pygame.draw.lines(screen, GRAY, False, PATH, width = 40) #drawing the enemy path
    pygame.display.flip()

pygame.quit() #closing the program
sys.exit()
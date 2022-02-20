import pygame

from sprites import Player, Wall, Enemy
from engine import Engine
from config import SCREEN_WIDTH, \
    SCREEN_HEIGHT, \
    DEFAULT_OBJ_SIZE, \
    __FRAMES_PER_SECOND, \
    BACKGROUND_COLOR


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

engine = Engine(screen=screen, clock=clock)
enemy = Enemy()
player = Player()

Wall.generate_walls((SCREEN_WIDTH, SCREEN_HEIGHT),
                    (DEFAULT_OBJ_SIZE, DEFAULT_OBJ_SIZE))

engine.running = True
engine.player = player

while engine.running:
    engine.events_handling()

    # Update all groups
    engine.groups_update()
    engine.screen.fill(BACKGROUND_COLOR)

    # Draw all sprites
    enemy.create_enemy()
    engine.draw_all_sprites()
    engine.indicators()
    pygame.display.flip()
    engine.clock.tick(__FRAMES_PER_SECOND)

pygame.quit()

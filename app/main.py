import pygame

from sprites import Player, Wall
from engine import Engine
from config import (SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                    DEFAULT_OBJ_SIZE,
                    FRAMES_PER_SECOND,
                    BACKGROUND_COLOR)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

engine = Engine(screen=screen, clock=clock)

player = Player()

Wall.generate_walls((SCREEN_WIDTH, SCREEN_HEIGHT),
                    (DEFAULT_OBJ_SIZE, DEFAULT_OBJ_SIZE))

engine.running = True

while engine.running:
    engine.events_handling()

    # Update all groups
    engine.groups_update()

    engine.screen.fill(BACKGROUND_COLOR)

    engine.cteate_text()
    # Draw all sprites
    engine.draw_all_sprites()

    pygame.display.flip()
    engine.clock.tick(FRAMES_PER_SECOND)

pygame.quit()

import pygame

from sprites import Player, Wall, Enemy
from engine import Engine
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_OBJ_SIZE


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

engine = Engine(screen=screen, clock=clock)

enemy = Enemy()

player = Player()

Wall.generate_walls((SCREEN_WIDTH, SCREEN_HEIGHT),
                    (DEFAULT_OBJ_SIZE, DEFAULT_OBJ_SIZE))

engine.running = True

while engine.running:
    engine.events_handling()

    enemy.create_enemy()

    # Update all groups
    engine.groups_update()

    engine.screen.fill((0, 0, 0))

    # Draw all sprites
    engine.draw_all_sprites()

    pygame.display.flip()
    engine.clock.tick(60)

pygame.quit()

import pygame

from sprites import Player, Wall
from enemies.enemy import Enemy
from engine import Engine
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_OBJ_SIZE,
    BACKGROUND_COLOR, FRAMES_PER_SECOND
)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

engine = Engine(screen=screen, clock=clock)
engine.spawner.add_enemy_with_spawn_chance_to_pull(Enemy, 1)
player = Player()

Wall.generate_walls((SCREEN_WIDTH, SCREEN_HEIGHT),
                    (DEFAULT_OBJ_SIZE, DEFAULT_OBJ_SIZE))

engine.running = True

while engine.running:
    engine.events_handling()

    # Update all groups
    engine.groups_update()

    engine.screen.fill(BACKGROUND_COLOR)

    # Draw scoreboard interface
    if engine.running:
        engine.scoreboard.draw_interface(engine)

    # Draw all sprites
    engine.draw_all_sprites()

    pygame.display.flip()
    engine.clock.tick(FRAMES_PER_SECOND)

pygame.quit()

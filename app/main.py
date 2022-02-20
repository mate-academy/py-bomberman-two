import pygame

from sprites import Wall
from sprites import engine
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_OBJECT_SIZE


Wall.generate_walls((SCREEN_WIDTH, SCREEN_HEIGHT),
                    (DEFAULT_OBJECT_SIZE, DEFAULT_OBJECT_SIZE))
engine.running = True

while engine.running:
    engine.events_handling()

    # Update all groups
    engine.groups_update()

    engine.screen.fill((0, 0, 0))
    engine.redrawGameWindow()
    # Draw all sprites
    engine.draw_all_sprites()

    pygame.display.flip()
    engine.clock.tick(60)

pygame.quit()

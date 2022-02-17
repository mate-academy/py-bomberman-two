import pygame
from app.sprites import Player, Wall, Spider
from app.engine import Engine
from app.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DEFAULT_OBJ_SIZE,
    BACKGROUND_COLOR,
    FRAMES_PER_SECOND)

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

engine = Engine(screen=screen, clock=clock)

player = Player()

spider = Spider((670, 375))

Wall.generate_walls((SCREEN_WIDTH, SCREEN_HEIGHT),
                    (DEFAULT_OBJ_SIZE, DEFAULT_OBJ_SIZE))
engine.player = player
engine.running = True

while engine.running:
    engine.events_handling()

    spider.create_spider()

    engine.groups_update()

    engine.screen.fill(BACKGROUND_COLOR)

    engine.draw_all_sprites()
    engine.draw_text()

    pygame.display.flip()
    engine.clock.tick(FRAMES_PER_SECOND)

pygame.quit()

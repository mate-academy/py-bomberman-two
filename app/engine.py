import pygame

from collections import defaultdict

from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from app.config import SCREEN_WIDTH


def singleton(class_):
    _instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in _instances:
            _instances[class_] = class_(*args, **kwargs)
        return _instances[class_]

    return get_instance


@singleton
class Engine:
    def __init__(self, screen, clock):
        self.running = True
        self.screen = screen
        self.clock = clock

        self.groups = defaultdict(pygame.sprite.Group)
        self.all_sprites = pygame.sprite.Group()

    def events_handling(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False

            # Did user click quit button?
            elif event.type == QUIT:
                self.running = False

    def add_to_group(self, sprite, group):
        self.groups[group].add(sprite)
        self.all_sprites.add(sprite)

    def groups_update(self):
        groups = list(self.groups.values())
        for group in groups:
            group.update()

    def draw_all_sprites(self):
        for sprite in self.all_sprites:
            self.screen.blit(sprite.surf, sprite.rect)

    def draw_current_condition(self, player_health, player_speed):
        font = pygame.font.SysFont("comicsans", 14, False)

        health = "Health: " + str(player_health)
        speed = "Speed: " + str(player_speed)

        health = font.render(health, True, (0, 255, 0))
        speed = font.render(speed, True, (0, 255, 0))
        self.screen.blit(health, (SCREEN_WIDTH - 78, 0))
        self.screen.blit(speed, (SCREEN_WIDTH - 60, 20))

import pygame

from collections import defaultdict

from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from app.config import BLUE_COLOR


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
        self.my_font = pygame.font.SysFont('Comic Sans MS', 20)
        self.blue = BLUE_COLOR
        self.groups = defaultdict(pygame.sprite.Group)
        self.all_sprites = pygame.sprite.Group()
        self.score = 0
        self.player = None

    def cteate_text(self):
        text_hp = self.my_font.render(f'HP: {self.player.health_of_player}'
                                      , False, self.blue)
        text_speed = self.my_font.render(f'SPEED: {self.player.speed}'
                                         , False, self.blue)
        text_score = self.my_font.render(f'Score: {self.score}'
                                         , False, self.blue)
        self.screen.blit(text_hp, (550, 3))
        self.screen.blit(text_speed, (550, 24))
        self.screen.blit(text_score, (10, 10))

    def events_handling(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False

            # Did user click quit button?
            elif event.type == QUIT:
                self.running = False

    def add_to_group(self, sprite, group):
        if group == "player":
            self.player = sprite
        self.groups[group].add(sprite)
        self.all_sprites.add(sprite)

    def groups_update(self):
        groups = list(self.groups.values())
        for group in groups:
            group.update()

    def draw_all_sprites(self):
        for sprite in self.all_sprites:
            self.screen.blit(sprite.surf, sprite.rect)

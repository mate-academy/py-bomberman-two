import pygame

from collections import defaultdict

from pygame.locals import K_ESCAPE, KEYDOWN, QUIT


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
        self.score = 0
        self.player_health = 100
        self.speed = 5
        self.groups = defaultdict(pygame.sprite.Group)
        self.all_sprites = pygame.sprite.Group()
        pygame.font.init()
        self.font = pygame.font.SysFont("comicsans", 15, True)

    def events_handling(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False

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

        self.screen.blit(self.font.render(
            f"Score: {self.score}", False, (255, 0, 0)), (0, 0))
        self.screen.blit(self.font.render(
            f"Health: {self.player_health}", False, (0, 255, 0)), (550, 0))
        self.screen.blit(self.font.render(
            f"Speed: {self.speed}", False, (0, 255, 0)), (550, 20))

import pygame

from app.config import DEFAULT_SCORE_INCREASE
from app.sprites import CollisionMixin, EngineSprite


class Enemy(EngineSprite, CollisionMixin):
    def __init__(self, initial_position):
        super(Enemy, self).__init__()
        self.engine.add_to_group(self, 'enemies')
        self.engine.add_to_group(self, '__flammable')
        self.speed = 2
        self.surf = pygame.image.load("images/spider_front.png").convert_alpha()
        self.rect = self.surf.get_rect(center=initial_position)
        self.player = self.engine.groups['player'].sprites()[0]

    def player_chase(self):
        if self.rect.centerx > self.player.rect.centerx:
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)
        if self.rect.centerx < self.player.rect.centerx:
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)
        if self.rect.centery > self.player.rect.centery:
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
        if self.rect.centery < self.player.rect.centery:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)

    def update(self):
        self.player_chase()

    def kill(self) -> None:
        self.engine.scoreboard.score += DEFAULT_SCORE_INCREASE
        super(Enemy, self).kill()

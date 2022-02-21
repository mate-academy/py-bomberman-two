import pygame

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


class Player(pygame.sprite.Sprite):
    def __init__(self, bm_game):
        super(Player, self).__init__()

        self.screen = bm_game.screen
        self.screen_rect = self.screen.get_rect()

        self.image_front = pygame.image.load(
            "images/player_front.png"
        ).convert_alpha()
        self.image_back = pygame.image.load(
            "images/player_back.png"
        ).convert_alpha()
        self.image_left = pygame.image.load(
            "images/player_left.png"
        ).convert_alpha()
        self.image_right = pygame.image.load(
            "images/player_right.png"
        ).convert_alpha()
        self.image = self.image_front
        self.rect = self.image.get_rect()

        self.speed = 5
        self.health = 100
        self.score = 0

    def update(self, pressed_keys):
        if sum(pressed_keys) == 1:
            if pressed_keys[K_UP]:
                self.image = self.image_back
                self.rect.move_ip(0, -self.speed)
            if pressed_keys[K_DOWN]:
                self.image = self.image_front
                self.rect.move_ip(0, self.speed)
            if pressed_keys[K_LEFT]:
                self.image = self.image_left
                self.rect.move_ip(-self.speed, 0)
            if pressed_keys[K_RIGHT]:
                self.image = self.image_right
                self.rect.move_ip(self.speed, 0)

        self._check_edges()

    def _check_edges(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_rect.right:
            self.rect.right = self.screen_rect.right
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= self.screen_rect.bottom:
            self.rect.bottom = self.screen_rect.bottom

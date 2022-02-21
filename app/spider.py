import random
import pygame


class Spider(pygame.sprite.Sprite):
    def __init__(self, bm_game):
        super(Spider, self).__init__()

        self.screen = bm_game.screen
        self.screen_rect = self.screen.get_rect()
        self.config = bm_game.config

        self.image_front = pygame.image.load(
            "images/spider_front.png"
        ).convert_alpha()
        self.image_back = pygame.image.load(
            "images/spider_back.png"
        ).convert_alpha()
        self.image_left = pygame.image.load(
            "images/spider_left.png"
        ).convert_alpha()
        self.image_right = pygame.image.load(
            "images/spider_right.png"
        ).convert_alpha()

        self.image = self.image_front
        self.rect = self.image.get_rect(
            center=(
                random.choice([-75, self.config.SCREEN_WIDTH + 75]),
                random.choice(
                    [i * 50 + 25 for i in range(
                        0, self.config.SCREEN_HEIGHT // 50, 2)]
                )
            )
        )

        self.speed = 2
        self.is_moving = False
        self.target = None

    def update(self):
        if self.target[0] == "Left" and self.target[1] > 0:
            self.rect.move_ip(-self.speed, 0)
            self.target[1] -= self.speed
        elif self.target[0] == "Right" and self.target[1] > 0:
            self.rect.move_ip(self.speed, 0)
            self.target[1] -= self.speed
        elif self.target[0] == "Up" and self.target[1] > 0:
            self.rect.move_ip(0, -self.speed)
            self.target[1] -= self.speed
        elif self.target[0] == "Down" and self.target[1] > 0:
            self.rect.move_ip(0, self.speed)
            self.target[1] -= self.speed
        else:
            self.is_moving = False

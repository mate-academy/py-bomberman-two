import pygame


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center_pos: tuple):
        super(Explosion, self).__init__()

        self.image_1 = pygame.image.load(
            "images/explosion_1.png"
        ).convert_alpha()
        self.image_2 = pygame.image.load(
            "images/explosion_2.png"
        ).convert_alpha()
        self.image_3 = pygame.image.load(
            "images/explosion_3.png"
        ).convert_alpha()
        self.images = [self.image_1, self.image_2, self.image_3]

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=center_pos)

        self.stage = 0
        self.time_to_next_stage = 5

    def update(self):
        if self.time_to_next_stage <= 0:
            self.stage += 1
            self.time_to_next_stage = 5
            if self.stage != 3:
                self.image = self.images[self.stage]
        else:
            self.time_to_next_stage -= 1

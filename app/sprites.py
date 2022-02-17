import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from engine import Engine
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_OBJ_SIZE,
    DEFAULT_PLAYER_HP, DEFAULT_PLAYER_SPEED, IMAGE_LEFT,
    IMAGE_RIGHT, IMAGE_FRONT, IMAGE_BACK,
    BOMB_TIMER, ENEMY_TIMER, DEFAULT_SCORE,
    EXPLODE_TIMER, EXPLOSION_1, EXPLOSION_2, EXPLOSION_3)


class EngineMixin:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.engine = Engine()


class EngineSprite(EngineMixin, pygame.sprite.Sprite):
    pass


class Player(EngineSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "player")
        self.speed = DEFAULT_PLAYER_SPEED
        self.health = DEFAULT_PLAYER_HP

        self.bomb_timer = BOMB_TIMER
        self.create_an_enemy = ENEMY_TIMER
        self.is_on_bomb = False
        # Images
        self.image_front = IMAGE_FRONT.convert_alpha()
        self.image_back = IMAGE_BACK.convert_alpha()
        self.image_left = IMAGE_LEFT.convert_alpha()
        self.image_right = IMAGE_RIGHT.convert_alpha()

        self.surf = self.image_front
        self.rect = self.surf.get_rect()
        self.score = DEFAULT_SCORE

    def update(self):
        pressed_keys = pygame.key.get_pressed()

        if self.bomb_timer:
            self.bomb_timer -= 1

        if self.create_an_enemy:
            self.create_an_enemy -= 1
        else:
            Enemy((0, 0))
            self.create_an_enemy = 60

        if pygame.sprite.spritecollideany(self, self.engine.groups["enemies"]):
            self.health -= 10
            self.score += 10

            if self.health == 0:
                self.kill()
                self.engine.running = False

        if not pygame.sprite.spritecollideany(
                self, self.engine.groups["bombs"]
        ):
            self.is_on_bomb = False

        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
            self.surf = self.image_back

        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
            self.surf = self.image_front

        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)
            self.surf = self.image_left

        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)
            self.surf = self.image_right

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        if pressed_keys[K_SPACE]:
            self.place_bomb()

    def move_collision_out(self, x_speed: int, y_speed: int):
        if (pygame.sprite.spritecollideany(
            self, self.engine.groups["walls"]
        ) or pygame.sprite.spritecollideany(
            self, self.engine.groups["bombs"]
        ) and not self.is_on_bomb):
            self.rect.move_ip(-x_speed, -y_speed)

    def place_bomb(self):
        if not self.bomb_timer:
            self.is_on_bomb = True
            Bomb(self.rect.center)
            self.bomb_timer = 45


class Wall(EngineSprite):
    def __init__(self, center_pos: tuple):
        super().__init__()
        self.engine.add_to_group(self, "walls")
        self.surf = pygame.image.load("images/wall.png").convert_alpha()
        self.rect = self.surf.get_rect(center=center_pos)

    @classmethod
    def generate_walls(cls, field_size: tuple, wall_size: tuple):
        walls_centers = cls.create_centers_of_walls(field_size, wall_size)
        for obs_center in walls_centers:
            Wall(obs_center)

    @staticmethod
    def create_centers_of_walls(field_size: tuple, wall_size: tuple):
        center_width = wall_size[0] + wall_size[0] // 2
        center_height = wall_size[1] + wall_size[1] // 2
        centers = []

        while center_height < field_size[1] - wall_size[1]:
            while center_width < field_size[0] - wall_size[0]:
                centers.append((center_width, center_height))
                center_width += 2 * wall_size[0]
            center_height += 2 * wall_size[1]
            center_width = wall_size[0] + wall_size[0] // 2

        return centers


class Bomb(EngineSprite):
    def __init__(self, owner_center: tuple):
        super().__init__()
        self.engine.add_to_group(self, "bombs")
        self.surf = pygame.image.load("images/bomb.png").convert_alpha()
        self.rect = self.surf.get_rect(center=owner_center)
        self.rect.center = self.get_self_center()
        self.explode_bomb_clock = EXPLODE_TIMER

    def get_self_center(self):
        lines = self.get_line_bomb_placed()
        return (
            lines[0] * DEFAULT_OBJ_SIZE + self.rect.width // 2,
            lines[1] * DEFAULT_OBJ_SIZE + self.rect.height // 2,
        )

    def get_line_bomb_placed(self):
        width = self.rect.centerx // DEFAULT_OBJ_SIZE
        height = self.rect.centery // DEFAULT_OBJ_SIZE
        return width, height

    def update(self):
        if self.explode_bomb_clock:
            self.explode_bomb_clock -= 1

            if self.explode_bomb_clock == 40:
                self.surf = EXPLOSION_1.convert_alpha()
            if self.explode_bomb_clock == 20:
                self.surf = EXPLOSION_2.convert_alpha()
            if self.explode_bomb_clock == 1:
                self.surf = EXPLOSION_3.convert_alpha()
                self.kill()


class Fire(EngineSprite):
    def __init__(self, owner_center: tuple):
        super(Fire, self).__init__()
        self.engine.add_to_group(self, "fires")
        self.surf = pygame.image.load("images/bomb.png").convert_alpha()
        self.rect = self.surf.get_rect(center=owner_center)
        self.rect.center = self.get_self_center()

    def get_self_center(self):
        lines = self.get_line_bomb_placed()
        return (
            lines[0] * DEFAULT_OBJ_SIZE + self.rect.width // 2,
            lines[1] * DEFAULT_OBJ_SIZE + self.rect.height // 2,
        )

    def get_line_bomb_placed(self):
        width = self.rect.centerx // DEFAULT_OBJ_SIZE
        height = self.rect.centery // DEFAULT_OBJ_SIZE
        return width, height
    # TODO make 2rd task


class Enemy(EngineSprite):
    def __init__(self, center_: (0, 0)):
        super(Enemy, self).__init__()
        self.engine.add_to_group(self, "enemies")
        self.surf = pygame.image.load("images\\spider_left.png")
        self.rect = self.surf.get_rect(center=center_)

    def update(self):
        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            print(self.engine.groups["player"])
            self.kill()

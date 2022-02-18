import random

import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from engine import Engine
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_OBJ_SIZE, \
    DEFAULT_PLAYER_SPEED, DEFAULT_PLAYER_HP, BOMB_TIMER


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
        self.placed_bomb_clock = 0
        self.is_on_bomb = False
        self.hp = DEFAULT_PLAYER_HP
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
        self.surf = self.image_front
        self.rect = self.surf.get_rect()

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if self.placed_bomb_clock:
            self.placed_bomb_clock -= 1

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

        if pygame.sprite.spritecollideany(
                self, self.engine.groups["explosions"]
        ):
            self.hp = 0

        if self.hp > 100:
            self.hp = 100

    def move_collision_out(self, x_speed: int, y_speed: int):
        if (pygame.sprite.spritecollideany(
            self, self.engine.groups["walls"]
        ) or pygame.sprite.spritecollideany(
            self, self.engine.groups["bombs"]
        ) and not self.is_on_bomb):
            self.rect.move_ip(-x_speed, -y_speed)

    def place_bomb(self):
        if not self.placed_bomb_clock:
            self.is_on_bomb = True
            Bomb(self.rect.center)
            self.placed_bomb_clock = 45


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
        self.time_to_explosion = 0

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
        self.time_to_explosion += 1
        if self.time_to_explosion == BOMB_TIMER:
            self.explode()
            self.kill()

    def explode(self):

        Explosion(self.rect.center)

        for i in range(1, 6):
            explosion = Explosion(
                (self.rect.centerx, self.rect.centery - DEFAULT_OBJ_SIZE * i)
            )
            if pygame.sprite.spritecollideany(
                    explosion, self.engine.groups["walls"]
            ):
                explosion.kill()
                break

        for i in range(1, 6):
            explosion = Explosion(
                (self.rect.centerx, self.rect.centery + DEFAULT_OBJ_SIZE * i)
            )
            if pygame.sprite.spritecollideany(
                    explosion, self.engine.groups["walls"]
            ):
                explosion.kill()
                break

        for i in range(1, 6):
            explosion = Explosion(
                (self.rect.centerx - DEFAULT_OBJ_SIZE * i, self.rect.centery)
            )
            if pygame.sprite.spritecollideany(
                    explosion, self.engine.groups["walls"]
            ):
                explosion.kill()
                break

        for i in range(1, 6):
            explosion = Explosion(
                (self.rect.centerx + DEFAULT_OBJ_SIZE * i, self.rect.centery)
            )
            if pygame.sprite.spritecollideany(
                    explosion, self.engine.groups["walls"]
            ):
                explosion.kill()
                break


class Explosion(EngineSprite):
    def __init__(self, owner_center: tuple):
        super().__init__()
        self.engine.add_to_group(self, "explosions")
        self.explosion_1 = pygame.image.load("images/explosion_1.png")
        self.explosion_2 = pygame.image.load("images/explosion_2.png")
        self.explosion_3 = pygame.image.load("images/explosion_3.png")
        self.surf = self.explosion_1
        self.rect = self.surf.get_rect(center=owner_center)
        self.time_of_explosion = 0

    def update(self):
        self.time_of_explosion += 1
        self.explosion_render()

    def explosion_render(self):
        if self.time_of_explosion == 5:
            self.surf = self.explosion_2
        if self.time_of_explosion == 10:
            self.surf = self.explosion_3
        if self.time_of_explosion == 15:
            self.kill()


class Enemy(EngineSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "enemies")
        self.enemy_image_front = pygame.image.load(
            "images/spider_front.png"
        ).convert_alpha()
        self.enemy_image_back = pygame.image.load(
            "images/spider_back.png"
        ).convert_alpha()
        self.enemy_image_left = pygame.image.load(
            "images/spider_left.png"
        ).convert_alpha()
        self.enemy_image_right = pygame.image.load(
            "images/spider_right.png"
        ).convert_alpha()
        self.surf = self.enemy_image_left
        self.rect = self.surf.get_rect(
            center=(
                (SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.start_time = 120
        self.speed = 2

    def update(self):
        try:
            player = self.engine.groups["player"].sprites()[0]
            x_diff = self.rect.centerx - player.rect.centerx
            y_diff = self.rect.centery - player.rect.centery

            if x_diff >= 0:
                self.rect.move_ip(-self.speed, 0)
                self.move_collision_out(-self.speed, 0)
                self.surf = self.enemy_image_left
            elif x_diff <= 0:
                self.rect.move_ip(self.speed, 0)
                self.move_collision_out(self.speed, 0)
                self.surf = self.enemy_image_right
            if y_diff >= 0:
                self.rect.move_ip(0, -self.speed)
                self.move_collision_out(0, -self.speed)
                self.surf = self.enemy_image_back
            elif y_diff <= 0:
                self.rect.move_ip(0, self.speed)
                self.move_collision_out(0, self.speed)
                self.surf = self.enemy_image_front

            if pygame.sprite.spritecollideany(
                    self, self.engine.groups["explosions"]
            ):
                player.hp += 10
                self.engine.score += 10
                self.kill()

            if pygame.sprite.spritecollideany(
                    self, self.engine.groups["player"]
            ):
                player.hp -= 10
                self.engine.score += 10
                self.kill()
        except IndexError:
            pass

    def create_enemy(self):
        self.start_time -= 1
        if not self.start_time:
            Enemy()
            self.start_time = 120

    def move_collision_out(self, x_speed: int, y_speed: int):
        if (pygame.sprite.spritecollideany(
            self, self.engine.groups["walls"]
        ) or pygame.sprite.spritecollideany(
            self, self.engine.groups["bombs"]
        )):
            self.rect.move_ip(-x_speed, -y_speed)

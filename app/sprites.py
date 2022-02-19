import random

import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from engine import Engine
from config import \
    SCREEN_WIDTH, \
    SCREEN_HEIGHT, \
    DEFAULT_OBJ_SIZE, \
    DEFAULT_HEALTH, \
    DEFAULT_SPEED, \
    EXPLOSION_RANGE


class EngineMixin:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.engine = Engine()

    def border_restrictions(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def move_collision_out(self):
        if pygame.sprite.spritecollideany(
                self, self.engine.groups["walls"]) \
                or pygame.sprite.spritecollideany(
                self, self.engine.groups["bombs"]):
            return True
        return False


class EngineSprite(EngineMixin, pygame.sprite.Sprite):
    pass


class Player(EngineSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "player")
        self.speed = DEFAULT_SPEED
        self.placed_bomb_clock = 0
        self.is_on_bomb = False
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
        self.time_appear_enemy = 1
        self.health_of_player = DEFAULT_HEALTH

    def touch_enemy(self):
        self.health_of_player -= 10
        if self.health_of_player <= 0:
            self.kill()
            self.engine.running = False

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
                self, self.engine.groups["explosions"]):
            self.kill()
            self.engine.running = False

    def get_health(self):
        return self.health_of_player

    def get_speed(self):
        return self.speed

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
        self.time_bomb = 200

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
        if self.time_bomb != 0:
            self.time_bomb -= 1
        else:
            Explosion.exictance_instance_check = Explosion(self.rect.center)
            self.kill()


class Explosion(EngineSprite):
    exictance_instance_check = None

    def __init__(self, bomb_center: tuple):
        super().__init__()
        self.engine.add_to_group(self, "explosions")
        self.explosion1 = pygame.image.load(
            "images/explosion_1.png").convert_alpha()
        self.explosion2 = pygame.image.load(
            "images/explosion_2.png").convert_alpha()
        self.explosion3 = pygame.image.load(
            "images/explosion_3.png").convert_alpha()
        self.surf = self.explosion1
        self.rect = self.surf.get_rect(center=bomb_center)
        self.time_expl = 30

    def update(self):
        if self.time_expl > 0:
            self.time_expl -= 1
        elif self.time_expl == 0:
            self.kill()
        if self.time_expl == 25:
            self.surf = self.explosion2
        if self.time_expl == 15:
            self.surf = self.explosion3

        if Explosion.exictance_instance_check is not None:
            center_tuple_right = Explosion.exictance_instance_check.rect.center
            center_tuple_left = Explosion.exictance_instance_check.rect.center
            center_tuple_top = Explosion.exictance_instance_check.rect.center
            center_tuple_bottom = \
                Explosion.exictance_instance_check.rect.center
            for i in range(EXPLOSION_RANGE):
                center_expl = list(center_tuple_right)
                center_expl[0] += DEFAULT_OBJ_SIZE
                flaim_inst = Explosion(tuple(center_expl))
                if pygame.sprite.spritecollideany(
                        flaim_inst, flaim_inst.engine.groups["walls"]):
                    flaim_inst.kill()
                    break
                center_tuple_right = tuple(center_expl)
            for i in range(EXPLOSION_RANGE):
                center_expl = list(center_tuple_left)
                center_expl[0] -= DEFAULT_OBJ_SIZE
                flaim_inst = Explosion(tuple(center_expl))
                if pygame.sprite.spritecollideany(
                        flaim_inst, flaim_inst.engine.groups["walls"]):
                    flaim_inst.kill()
                    break
                center_tuple_left = tuple(center_expl)
            for i in range(EXPLOSION_RANGE):
                center_expl = list(center_tuple_top)
                center_expl[1] += DEFAULT_OBJ_SIZE
                flaim_inst = Explosion(tuple(center_expl))
                if pygame.sprite.spritecollideany(
                        flaim_inst, flaim_inst.engine.groups["walls"]):
                    flaim_inst.kill()
                    break
                center_tuple_top = tuple(center_expl)
            for i in range(EXPLOSION_RANGE):
                center_expl = list(center_tuple_bottom)
                center_expl[1] -= DEFAULT_OBJ_SIZE
                flaim_inst = Explosion(tuple(center_expl))
                if pygame.sprite.spritecollideany(
                        flaim_inst, flaim_inst.engine.groups["walls"]):
                    flaim_inst.kill()
                    break
                center_tuple_bottom = tuple(center_expl)
            Explosion.exictance_instance_check = None


class Spider(EngineSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "spider")
        self.image_front = pygame.image.load(
            "images/spider_front.png").convert_alpha()
        self.image_back = pygame.image.load(
            "images/spider_back.png").convert_alpha()
        self.image_left = pygame.image.load(
            "images/spider_left.png").convert_alpha()
        self.image_right = pygame.image.load(
            "images/spider_right.png").convert_alpha()
        self.surf = self.image_front
        self.position = self.generate_position()
        self.rect = self.surf.get_rect(center=self.position[:2])
        self.speed = 3
        self.kill_spider_score = 10

    def collisions(self, speed_x: int, speed_y: int):
        if pygame.sprite.spritecollideany(
                self, self.engine.groups["explosions"]):
            self.engine.score += self.kill_spider_score
            self.kill()
        if super().move_collision_out():
            self.rect.move_ip(-speed_x, -speed_y)

    def update(self):
        player = self.engine.groups["player"].sprites()[0]
        x_diff = self.rect.center[0] - player.rect.center[0]
        y_diff = self.rect.center[1] - player.rect.center[1]

        if x_diff >= 0:
            self.rect.move_ip(-self.speed, 0)
            self.collisions(-self.speed, 0)
            self.surf = self.image_left
        elif x_diff <= 0:
            self.rect.move_ip(self.speed, 0)
            self.collisions(self.speed, 0)
            self.surf = self.image_right
        if y_diff >= 0:
            self.rect.move_ip(0, -self.speed)
            self.collisions(0, -self.speed)
            self.surf = self.image_back
        if y_diff <= 0:
            self.rect.move_ip(0, self.speed)
            self.collisions(0, self.speed)
            self.surf = self.image_front

        self.border_restrictions()

        if pygame.sprite.spritecollideany(self, self.engine.groups["player"]):
            player.touch_enemy()
            self.engine.score += self.kill_spider_score
            self.kill()

    @staticmethod
    def generate_position() -> tuple:
        delta = 50
        direction = random.choice(["left", "top", "right", "bottom"])
        if direction == "left":
            width = -delta
            height = random.randint(0, SCREEN_HEIGHT)

        if direction == "top":
            width = random.randint(0, SCREEN_WIDTH)
            height = -delta

        if direction == "right":
            width = SCREEN_WIDTH + delta
            height = random.randint(0, SCREEN_HEIGHT)

        if direction == "bottom":
            width = random.randint(0, SCREEN_WIDTH)
            height = SCREEN_HEIGHT + delta

        return width, height, direction

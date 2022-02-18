import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from engine import Engine
from config import (SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                    DEFAULT_OBJ_SIZE,
                    DEFAULT_PLAYER_HP,
                    DEFAULT_PLAYER_SPEED,
                    DEFAULT_ENEMY_SPEED,
                    DEFAULT_TIME_EXIST_FIRE,
                    DEFAULT_GET_SCORE,
                    DEFAULT_NEW_POSITIONS,
                    DEFAULT_TIME_EXIST_BOMB)


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
        if pygame.sprite.spritecollideany(self, self.engine.groups["walls"]) \
                or pygame.sprite.spritecollideany(self,
                                                  self.engine.groups["bombs"]):
            return True
        return False


class EngineSprite(EngineMixin, pygame.sprite.Sprite):
    pass


class Player(EngineSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "player")
        self.speed = DEFAULT_PLAYER_SPEED
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
        self.health_of_player = DEFAULT_PLAYER_HP

    def touch_enemy(self):
        self.health_of_player -= 10
        self.engine.score += DEFAULT_GET_SCORE
        if self.health_of_player < 0:
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
            self.move_collision_out_player(0, -self.speed)
            self.surf = self.image_back

        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out_player(0, self.speed)
            self.surf = self.image_front

        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out_player(-self.speed, 0)
            self.surf = self.image_left

        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out_player(self.speed, 0)
            self.surf = self.image_right

        self.border_restrictions()

        if pressed_keys[K_SPACE]:
            self.place_bomb()

        time_ = pygame.time.get_ticks() // 1000

        if time_ == self.time_appear_enemy:
            self.time_appear_enemy += 1
            Enemy()

    def move_collision_out_player(self, x_speed: int, y_speed: int):
        if pygame.sprite.spritecollideany(self, self.engine.groups['fire']):
            self.kill()
            self.engine.running = False
        if super().move_collision_out() and not self.is_on_bomb:
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

        self.time_exist_boom = DEFAULT_TIME_EXIST_BOMB

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
        self.time_exist_boom -= 1
        if self.time_exist_boom <= 0:
            self.kill()

            self.show_fires(self.create_coordinates()['fire_left'])
            self.show_fires(self.create_coordinates()['fire_right'])
            self.show_fires(self.create_coordinates()['fire_top'])
            self.show_fires(self.create_coordinates()['fire_bottom'])

    def show_fires(self, coordinates_fire):
        for coordinate in coordinates_fire:
            fire = Fire()
            fire.rect.center = coordinate[0], coordinate[1]
            if pygame.sprite.spritecollideany(fire,
                                              self.engine.groups["walls"]):
                fire.kill()
                break

    def create_coordinates(self):
        center = self.get_self_center()
        new_positions = DEFAULT_NEW_POSITIONS
        result_coordinates = {
            'fire_left': [
                (center[0] + position, center[1]) for position in new_positions
            ],
            'fire_right': [
                (center[0] - position, center[1]) for position in new_positions
            ],
            'fire_top': [
                (center[0], center[1] + position) for position in new_positions
            ],
            'fire_bottom': [
                (center[0], center[1] - position) for position in new_positions
            ]
        }
        return result_coordinates


class Enemy(EngineSprite):

    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "enemies")
        self.spider_front = pygame.image.load(
            "images/spider_front.png").convert_alpha()
        self.spider_left = pygame.image.load(
            "images/spider_left.png").convert_alpha()
        self.spider_right = pygame.image.load(
            "images/spider_right.png").convert_alpha()
        self.spider_back = pygame.image.load(
            "images/spider_back.png.").convert_alpha()
        self.surf = self.spider_front
        self.rect = self.surf.get_rect(center=(0, 0))
        self.speed = DEFAULT_ENEMY_SPEED

    def move_collision_out_enemy(self, x_speed: int, y_speed: int):
        if pygame.sprite.spritecollideany(self, self.engine.groups['fire']):
            self.engine.score += DEFAULT_GET_SCORE
            self.kill()
        if super().move_collision_out():
            self.rect.move_ip(-x_speed, -y_speed)

    def update(self):
        player = self.engine.player

        x_diff = self.rect.center[0] - player.rect.center[0]
        y_diff = self.rect.center[1] - player.rect.center[1]

        if x_diff > 0:
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out_enemy(-self.speed, 0)
            self.surf = self.spider_left
        elif x_diff < 0:
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out_enemy(self.speed, 0)
            self.surf = self.spider_right

        if y_diff > 0:
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out_enemy(0, -self.speed)
            self.surf = self.spider_back
        elif y_diff < 0:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out_enemy(0, self.speed)
            self.surf = self.spider_front

        self.border_restrictions()

        if pygame.sprite.spritecollideany(self, self.engine.groups['player']):
            player.touch_enemy()
            self.kill()


class Fire(EngineSprite):

    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "fire")
        self.surf = pygame.image.load(
            "images/explosion_1.png").convert_alpha()
        self.image_one = pygame.image.load(
            "images/explosion_2.png").convert_alpha()
        self.image_two = pygame.image.load(
            "images/explosion_3.png").convert_alpha()
        self.rect = self.surf.get_rect()
        self.time_exist_fire = DEFAULT_TIME_EXIST_FIRE

    def update(self):
        self.time_exist_fire -= 1
        if self.time_exist_fire == 25:
            self.surf = self.image_one
        if self.time_exist_fire == 20:
            self.surf = self.image_two
        if self.time_exist_fire == 15:
            self.kill()

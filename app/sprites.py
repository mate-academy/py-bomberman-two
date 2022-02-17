import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from app.engine import Engine
from app.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DEFAULT_OBJ_SIZE,
    DEFAULT_PLAYER_SPEED,
    BOMB_TIMER,
    EXPLOSION_RANGE,
    DEFAULT_SPYDER_SPEED, DEFAULT_PLAYER_HP)


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
        self.placed_bomb_clock = 0
        self.take_damage = 60
        self.start_timer = None
        self.is_on_bomb = False
        self.health = DEFAULT_PLAYER_HP
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
                self, self.engine.groups["bombs"]):
            self.is_on_bomb = False

        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -DEFAULT_PLAYER_SPEED)
            self.move_collision_out(0, -DEFAULT_PLAYER_SPEED)
            self.surf = self.image_back

        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, DEFAULT_PLAYER_SPEED)
            self.move_collision_out(0, DEFAULT_PLAYER_SPEED)
            self.surf = self.image_front

        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-DEFAULT_PLAYER_SPEED, 0)
            self.move_collision_out(-DEFAULT_PLAYER_SPEED, 0)
            self.surf = self.image_left

        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(DEFAULT_PLAYER_SPEED, 0)
            self.move_collision_out(DEFAULT_PLAYER_SPEED, 0)
            self.surf = self.image_right

        if pygame.sprite.spritecollideany(self, self.engine.groups["fire"]):
            self.kill()
            self.engine.running = False

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
                self, self.engine.groups["walls"])
                or pygame.sprite.spritecollideany(
                    self, self.engine.groups["bombs"])
                and not self.is_on_bomb):
            self.rect.move_ip(-x_speed, -y_speed)

    def place_bomb(self):
        if not self.placed_bomb_clock:
            self.is_on_bomb = True
            self.placed_bomb_clock = 45
            center_bomb = self.rect.center
            bomb = Bomb(center_bomb)
            bomb.start_timer = pygame.time.get_ticks()


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
        self.start_timer = None
        self.engine.add_to_group(self, "bombs")
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

    def update(self):
        if self.start_timer is not None:
            if pygame.time.get_ticks() - self.start_timer >= BOMB_TIMER:
                self.kill()
                fire = Fire(self.rect.center)
                all_pos = fire.create_position_fire()
                all_fire = [fire]
                for pos in all_pos:
                    for x, y in pos:
                        repeating_fire = Fire((x, y))
                        if pygame.sprite.spritecollideany(
                                repeating_fire, self.engine.groups["walls"]
                        ):
                            repeating_fire.kill()
                            break
                        all_fire.append(repeating_fire)

                for fire_range in all_fire:
                    fire_range.start_timer = pygame.time.get_ticks()


class Fire(EngineSprite):
    def __init__(self, owner_center: tuple):
        super().__init__()
        self.start_timer = None
        self.engine.add_to_group(self, "fire")
        self.first_step_boom = pygame.image.load(
            "images/explosion_1.png"
        ).convert_alpha()
        self.second_step_boom = pygame.image.load(
            "images/explosion_2.png"
        ).convert_alpha()
        self.third_step_boom = pygame.image.load(
            "images/explosion_3.png"
        ).convert_alpha()
        self.surf = self.first_step_boom
        self.rect = self.surf.get_rect(center=owner_center)

    def create_position_fire(self):
        position_right = [
            (self.rect.centerx + DEFAULT_OBJ_SIZE * i, self.rect.centery)
            for i in range(1, EXPLOSION_RANGE)
        ]
        position_bottom = [
            (self.rect.centerx, self.rect.centery + DEFAULT_OBJ_SIZE * i)
            for i in range(1, EXPLOSION_RANGE)
        ]
        position_top = [
            (self.rect.centerx, self.rect.centery - DEFAULT_OBJ_SIZE * i)
            for i in range(1, EXPLOSION_RANGE)
        ]
        position_left = [
            (self.rect.centerx - DEFAULT_OBJ_SIZE * i, self.rect.centery)
            for i in range(1, EXPLOSION_RANGE)
        ]

        return position_right, position_bottom, position_top, position_left

    def update(self):
        if self.start_timer is not None:
            if pygame.time.get_ticks() - self.start_timer >= 200:
                self.surf = self.second_step_boom
            if pygame.time.get_ticks() - self.start_timer >= 400:
                self.surf = self.third_step_boom
            if pygame.time.get_ticks() - self.start_timer >= 600:
                self.kill()


class Spider(EngineSprite):
    def __init__(self, center_pos: tuple):
        super().__init__()
        self.speed = DEFAULT_SPYDER_SPEED
        self.start_time = 60
        self.engine.add_to_group(self, "spiders")
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
        self.surf = self.image_front
        self.rect = self.surf.get_rect(center=center_pos)

    def update(self):

        spider_x = self.rect.centerx
        spider_y = self.rect.centery - 25

        if self.engine.player.rect.y <= spider_y:
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
            self.surf = self.image_back
        else:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
            self.surf = self.image_front

        if self.engine.player.rect.x <= spider_x:
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)
            self.surf = self.image_left
        else:
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

        if pygame.sprite.spritecollideany(self, self.engine.groups["fire"]):
            self.engine.score += 10
            self.kill()
        if pygame.sprite.spritecollideany(self, self.engine.groups["walls"]):
            self.move_collision_out(DEFAULT_SPYDER_SPEED, DEFAULT_SPYDER_SPEED)

        if pygame.sprite.spritecollideany(
                self.engine.player, self.engine.groups["spiders"]):
            self.engine.player.take_damage -= 1
            if self.engine.player.take_damage == 0:
                self.engine.player.take_damage = 60
                self.engine.player.health -= 10
                if self.engine.player.health <= 0:
                    self.engine.player.kill()
                    self.engine.running = False

    def move_collision_out(self, x_speed: int, y_speed: int):
        if (pygame.sprite.spritecollideany(
                self, self.engine.groups["walls"])
                or pygame.sprite.spritecollideany(
                    self, self.engine.groups["bombs"])):
            self.rect.move_ip(-x_speed, -y_speed)

    def create_spider(self):
        self.start_time -= 1
        if not self.start_time:
            Spider((670, 375))
            self.start_time = 60

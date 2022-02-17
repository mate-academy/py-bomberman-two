import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from engine import Engine
from config import SCREEN_WIDTH,\
    SCREEN_HEIGHT,\
    DEFAULT_OBJ_SIZE,\
    BOMB_EXPLOSION_TICKS,\
    FIRE_LIVING_TIME,\
    DEFAULT_FIRE_LENGTH, PLAYER_HP


class Directions:
    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)


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
        self.speed = 5
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
        self.enemy_spawn_counter = 120
        self.health_points = PLAYER_HP

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if self.placed_bomb_clock:
            self.placed_bomb_clock -= 1
        self.enemy_spawn_counter -= 1
        if not self.enemy_spawn_counter:
            Enemy()
            self.enemy_spawn_counter = 120

        if not pygame.sprite.spritecollideany(
                self, self.engine.groups["bombs"]
        ):
            self.is_on_bomb = False

        if pygame.sprite.spritecollideany(
            self, self.engine.groups['fires']
        ):
            print('Game over')
            self.kill()

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
        if not self.placed_bomb_clock:
            self.is_on_bomb = True
            Bomb(self.rect.center)
            self.placed_bomb_clock = 45

    def get_center(self):
        return self.rect.center

    def get_hit(self):
        self.health_points -= 10
        if not self.health_points:
            self.kill()


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
        self.placed_tick_counter = BOMB_EXPLOSION_TICKS

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
        self.placed_tick_counter -= 1
        if not self.placed_tick_counter:
            Fire.create_fires(self.get_self_center())
            self.kill()


class Fire(EngineSprite):
    def __init__(self, position: tuple):
        super().__init__()
        self.engine.add_to_group(self, "fires")
        self.surf = pygame.image.load("images/explosion_1.png").convert_alpha()
        self.rect = self.surf.get_rect(center=position)
        self.living_time = FIRE_LIVING_TIME

    def update(self):
        self.living_time -= 1
        if not self.living_time:
            self.kill()

    @classmethod
    def create_centers_of_fire(cls, starting_point: tuple, direction: tuple):
        centers = []
        for i in range(DEFAULT_FIRE_LENGTH):
            next_center = (
                (starting_point[0])
                + DEFAULT_OBJ_SIZE * (i + 1) * direction[0],
                (starting_point[1])
                + DEFAULT_OBJ_SIZE * (i + 1) * direction[1],
            )
            centers.append(next_center)
        return centers

    @classmethod
    def create_fires(cls, starting_poit):
        directions = [
            cls.create_centers_of_fire(starting_poit, Directions.UP),
            cls.create_centers_of_fire(starting_poit, Directions.DOWN),
            cls.create_centers_of_fire(starting_poit, Directions.LEFT),
            cls.create_centers_of_fire(starting_poit, Directions.RIGHT),
        ]

        for direction in directions:
            for center in direction:
                new_fire = Fire(center)
                if pygame.sprite.spritecollideany(
                        new_fire, new_fire.engine.groups['walls']
                ):
                    new_fire.kill()
                    break
        Fire(starting_poit)


class Enemy(EngineSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "enemies")
        self.surf = pygame.image.load(
            "images/spider_front.png").convert_alpha()
        self.rect = self.surf.get_rect(center=(0, 0))
        self.speed = 3

    def move(self, direction: tuple):
        self.rect.move_ip(direction[0], direction[1])
        if (pygame.sprite.spritecollideany(self, self.engine.groups['walls'])
                or pygame.sprite.spritecollideany(
                    self, self.engine.groups['bombs'])):
            self.rect.move_ip(-direction[0], -direction[1])
            return False
        return True

    def update(self):
        player_coords = None
        cur_player = None
        for player in self.engine.groups['player']:
            cur_player = player
            player_coords = player.get_center()

        coords = self.rect.center
        vertical_direction = 0
        horizontal_direction = 0

        if coords[0] > player_coords[0]:
            horizontal_direction = -self.speed
        else:
            horizontal_direction = self.speed
        if coords[1] > player_coords[1]:
            vertical_direction = -self.speed
        else:
            vertical_direction = self.speed

        self.move((horizontal_direction, 0))
        self.move((0, vertical_direction))
        if pygame.sprite.spritecollideany(self, self.engine.groups['fires']):
            self.engine.kill_count += 1
            self.kill()
        if pygame.sprite.spritecollideany(self, self.engine.groups['player']):
            cur_player.get_hit()
            self.kill()

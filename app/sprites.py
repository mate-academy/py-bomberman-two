import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from engine import Engine
from config import SCREEN_WIDTH, \
    SCREEN_HEIGHT, \
    DEFAULT_OBJ_SIZE, \
    DEFAULT_PLAYER_SPEED, \
    DEFAULT_PLAYER_HP, \
    EXPLOSION_RANGE, \
    DEFAULT_ENEMIES_SPEED,\
    BOMB_TIMER, \
    DEFAULT_ENEMIES_SPAWN_TIMEOUT


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
        self.placed_bomb_clock = 0
        self.take_damage = 10
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

        if pygame.sprite.spritecollideany(self, self.engine.groups["fires"]):
            self.kill()
            self.engine.running = False
            print("GAME OVER")

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
        self.life_time_count = 0

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
        if self.life_time_count == BOMB_TIMER * 60:
            self.kill()
            Fire(self.rect.centerx, self.rect.centery)
            for i in range(1, EXPLOSION_RANGE):
                fire = Fire(self.rect.centerx + i * 50, self.rect.centery)
                if pygame.sprite.spritecollideany(
                        fire, self.engine.groups["walls"]):
                    fire.kill()
                    break
                self.engine.add_to_group(fire, "fire")
            for i in range(1, EXPLOSION_RANGE):
                fire = Fire(self.rect.centerx - i * 50, self.rect.centery)
                if pygame.sprite.spritecollideany(
                        fire, self.engine.groups["walls"]):
                    fire.kill()
                    break
                self.engine.add_to_group(fire, "fire")
            for i in range(1, EXPLOSION_RANGE):
                fire = Fire(self.rect.centerx, self.rect.centery + i * 50)
                if pygame.sprite.spritecollideany(
                        fire, self.engine.groups["walls"]):
                    fire.kill()
                    break
                self.engine.add_to_group(fire, "fire")
            for i in range(1, EXPLOSION_RANGE):
                fire = Fire(self.rect.centerx, self.rect.centery - i * 50)
                if pygame.sprite.spritecollideany(
                        fire, self.engine.groups["walls"]):
                    fire.kill()
                    break
                self.engine.add_to_group(fire, "fire")
        self.life_time_count += 1


class Fire(EngineSprite):
    def __init__(self, center_x, center_y):
        super().__init__()
        self.engine.add_to_group(self, "fires")
        self.surf = pygame.image.load("images/explosion_1.png").convert_alpha()
        self.rect = self.surf.get_rect(center=(center_x, center_y))
        self.life_time_count = 0

    def update(self):
        if self.life_time_count == 5:
            self.surf = \
                pygame.image.load("images/explosion_2.png").convert_alpha()
        if self.life_time_count == 10:
            self.surf = \
                pygame.image.load("images/explosion_3.png").convert_alpha()
        if self.life_time_count == 15:
            self.kill()
        self.life_time_count += 1


class Enemy(EngineSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "enemies")
        self.speed = DEFAULT_ENEMIES_SPEED
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
        self.surf = self.image_left
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH - 25,
                                               SCREEN_HEIGHT - 125))
        self.timer = DEFAULT_ENEMIES_SPAWN_TIMEOUT * 60

    def update(self):
        if pygame.sprite.spritecollideany(self, self.engine.groups["fires"]):
            self.engine.score += 10
            self.kill()
        player_x = 0
        player_y = 0
        for current_player in self.engine.groups['player']:
            player_x = current_player.rect[0]
            player_y = current_player.rect[1]

        enemy_x = self.rect.centerx
        enemy_y = self.rect.centery - 25

        if enemy_y > player_y:
            self.surf = pygame.image.load("images/spider_back.png")
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)

        elif enemy_y < player_y:
            self.surf = pygame.image.load("images/spider_front.png")
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)

        if enemy_x > player_x:
            self.surf = pygame.image.load("images/spider_left.png")
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)

        elif enemy_x < player_x:
            self.surf = pygame.image.load("images/spider_right.png")
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        if pygame.sprite.spritecollideany(
                self.engine.player, self.engine.groups["enemies"]):
            self.engine.player.take_damage -= 1
            if self.engine.player.take_damage == 0:
                self.engine.player.take_damage = 60
                self.engine.player.health -= 10
                if self.engine.player.health <= 0:
                    self.engine.player.kill()
                    print("GAME OVER")
                    self.engine.running = False

    def move_collision_out(self, x_speed: int, y_speed: int):
        if (pygame.sprite.spritecollideany
            (self, self.engine.groups["walls"])
            or pygame.sprite.spritecollideany
                (self, self.engine.groups["bombs"])):
            self.rect.move_ip(-x_speed, -y_speed)

    def create_enemy(self):
        self.timer -= 1
        if not self.timer:
            Enemy()
            self.timer = DEFAULT_ENEMIES_SPAWN_TIMEOUT * 60

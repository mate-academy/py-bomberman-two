import pygame
import time

from engine import Engine
from random import choice
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from config import SCREEN_WIDTH, SCREEN_HEIGHT, \
    PLAYER_FRONT, PLAYER_BACK, PLAYER_LEFT, \
    PLAYER_RIGHT, WALL, BOMB, DEFAULT_OBJECT_SIZE, \
    FIRE2, FIRE3, FIRE1, SPIDER_FRONT, SPEED, SPIDER_RIGHT,\
    SPIDER_LEFT, SPIDER_BACK

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

engine = Engine(screen=screen, clock=clock)


class EngineMixin:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.engine = engine


class EngineSprite(EngineMixin, pygame.sprite.Sprite):
    pass


class Player(EngineSprite):
    timeout = 0
    score = 0

    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load(PLAYER_FRONT)
        self.rect = self.surf.get_rect()
        self.speed = SPEED
        self.health_points = 100
        self.engine.add_to_group(self, "player")
        self.is_on_bomb = False
        self.plant = False

    def update(self):

        pressed_keys = pygame.key.get_pressed()
        self.kill_player()

        if time.time() - Player.timeout >= 1 and pressed_keys[K_SPACE]:
            self.plant_bomb()

        if not pygame.sprite.spritecollideany(
                player, self.engine.groups["bombs"]
        ):
            self.is_on_bomb = False

        if pressed_keys[K_UP]:
            self.surf = pygame.image.load(PLAYER_BACK)
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)

        if pressed_keys[K_DOWN]:
            self.surf = pygame.image.load(PLAYER_FRONT)
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)

        if pressed_keys[K_LEFT]:
            self.surf = pygame.image.load(PLAYER_LEFT)
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)

        if pressed_keys[K_RIGHT]:
            self.surf = pygame.image.load(PLAYER_RIGHT)
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        if self.rect.top <= 0:
            self.rect.top = 0

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        if self.health_points <= 0:
            self.kill()
            pygame.quit()

    def plant_bomb(self):
        bomb = Bomb(self.rect.center)
        self.is_on_bomb = True
        Player.timeout = time.time()
        self.plant = True
        bomb.time = time.time()

    def move_collision_out(self, x, y):
        if pygame.sprite.spritecollideany(self, self.engine.groups["walls"]) \
                or pygame.sprite.\
                spritecollideany(self, self.engine.groups["bombs"]):
            if not self.is_on_bomb:
                player.rect.move_ip(-x, -y)

    def kill_player(self):
        if pygame.sprite.\
                spritecollideany(self, self.engine.groups["fires"]):
            self.kill()


player = Player()


class Wall(EngineSprite):
    def __init__(self, center_pos: tuple):
        super().__init__()
        self.engine.add_to_group(self, "walls")
        self.surf = pygame.image.load(WALL).convert_alpha()
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
    def __init__(self, player):
        super().__init__()
        self.surf = pygame.image.load(BOMB)
        self.engine.add_to_group(self, "bombs")
        self.player = player
        self.rect = self.surf.get_rect(center=player)
        self.rect.center = self.get_self_center()

    def update(self):
        self.burn_bombs()
        self.blow_up()

    def get_lines(self):
        width = self.rect.centerx // DEFAULT_OBJECT_SIZE
        height = self.rect.centery // DEFAULT_OBJECT_SIZE
        return width, height

    def get_self_center(self):
        lines = self.get_lines()
        return (
            lines[0] * DEFAULT_OBJECT_SIZE + self.rect.width // 2,
            lines[1] * DEFAULT_OBJECT_SIZE + self.rect.height // 2,
        )

    def blow_up(self):
        for bomb in self.engine.groups["bombs"]:
            if time.time() - bomb.time >= 4:
                bomb.kill()
                fire = Fire(bomb.rect.centerx, bomb.rect.centery)
                fire.fire_attack_x(bomb.rect.centerx, bomb.rect.centery)
                fire.fire_attack_y(bomb.rect.centerx, bomb.rect.centery)

    def burn_bombs(self):
        if pygame.sprite.spritecollideany(self, engine.groups["fires"]):
            self.kill()


class Fire(EngineSprite):

    def __init__(self, bomb_x, bomb_y):
        super().__init__()
        self.engine.add_to_group(self, "fires")
        self.surf = pygame.image.load(choice((FIRE1, FIRE2, FIRE3)))
        self.rect = self.surf.get_rect(center=(bomb_x, bomb_y))
        self.time = time.time()

    def update(self):
        self.fire_life()

    def fire_attack_x(self, bomb_x, bomb_y):
        while bomb_x < SCREEN_WIDTH - DEFAULT_OBJECT_SIZE // 2:
            if pygame.sprite.spritecollideany(Fire(bomb_x + 1, bomb_y),
                                              self.engine.groups["walls"]):
                break
            bomb_x = bomb_x + DEFAULT_OBJECT_SIZE

        while bomb_x > 0:
            if pygame.sprite.spritecollideany(Fire(bomb_x - 1, bomb_y),
                                              self.engine.groups["walls"]):
                break
            bomb_x = bomb_x - DEFAULT_OBJECT_SIZE

    def fire_attack_y(self, bomb_x, bomb_y):
        while bomb_y < SCREEN_HEIGHT:
            if pygame.sprite.spritecollideany(Fire(bomb_x, bomb_y + 1),
                                              self.engine.groups["walls"]):
                break
            bomb_y = bomb_y + DEFAULT_OBJECT_SIZE

        while bomb_y > 0:
            if pygame.sprite.spritecollideany(Fire(bomb_x, bomb_y - 1),
                                              self.engine.groups["walls"]):
                break
            bomb_y = bomb_y - DEFAULT_OBJECT_SIZE

    def fire_life(self):
        for fire in self.engine.groups["fires"]:
            if time.time() - fire.time >= 0.2:
                fire.kill()


class Enemy(EngineSprite):
    timeout = 0

    def __init__(self, spider_x, spider_y):
        super().__init__()
        self.spider_x = spider_x
        self.spider_y = spider_y
        self.speed = SPEED - 2
        self.engine.add_to_group(self, "enemies")
        self.surf = pygame.image.load(SPIDER_LEFT).convert_alpha()
        self.rect = self.surf.get_rect(center=(spider_x, spider_y))

    def update(self):

        x_diff = self.rect.centerx - player.rect.centerx
        y_diff = self.rect.centery - player.rect.centerx
        if x_diff >= 0:
            self.rect.move_ip(-self.speed, 0)
            self.move_collision_out(-self.speed, 0)
            self.surf = pygame.image.load(SPIDER_RIGHT)
        elif x_diff <= 0:
            self.rect.move_ip(self.speed, 0)
            self.move_collision_out(self.speed, 0)
            self.surf = pygame.image.load(SPIDER_LEFT)
        if y_diff >= 0:
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
            self.surf = pygame.image.load(SPIDER_BACK)
        elif y_diff <= 0:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
            self.surf = pygame.image.load(SPIDER_FRONT)

        if time.time() - Enemy.timeout >= 1:
            Enemy(choice((800, -20, 755)), choice((-20, 800, 755)))

            Enemy.timeout = time.time()
        self.burn_spiders()

    def move_collision_out(self, x, y):
        if pygame.sprite.spritecollideany(self, self.engine.groups["walls"]) \
                or pygame.sprite. \
                spritecollideany(self, self.engine.groups["bombs"]):
            self.rect.move_ip(-x, -y)

    def burn_spiders(self):
        if pygame.sprite.spritecollideany(self, engine.groups["fires"]) \
                or pygame.sprite. \
                spritecollideany(self, self.engine.groups["player"]):
            self.kill()
            self.engine.score += 10
            player.health_points -= 10


Enemy(650, 650)

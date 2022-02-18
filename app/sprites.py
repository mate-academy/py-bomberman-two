import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from engine import Engine
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_OBJ_SIZE


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
        self.speed = self.engine.speed
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

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if self.placed_bomb_clock:
            self.placed_bomb_clock -= 1

        if pygame.sprite.spritecollideany(self, self.engine.groups["fire"]):
            self.kill()

        if pygame.sprite.spritecollideany(self, self.engine.groups["enemy"]):
            self.engine.player_health -= 10

        if not self.engine.player_health:
            self.kill()

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
        if not self.placed_bomb_clock:
            self.is_on_bomb = True
            Bomb(self.rect.center)
            self.placed_bomb_clock = 60


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
        self.image_explosion_1 = pygame.image.load(
            "images/explosion_1.png").convert_alpha()
        self.image_explosion_2 = pygame.image.load(
            "images/explosion_2.png").convert_alpha()
        self.image_explosion_3 = pygame.image.load(
            "images/explosion_3.png").convert_alpha()
        self.rect = self.surf.get_rect(center=owner_center)
        self.rect.center = self.get_self_center()
        self.life_time = 180

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
        self.life_time -= 1
        if self.life_time == 30:
            self.surf = self.image_explosion_1
            for i in range(1, 4):
                fire = Fire(self.rect.centerx + i * 50, self.rect.centery)
                if pygame.sprite.spritecollideany(
                        fire, self.engine.groups["walls"]):
                    fire.kill()
                    break
                self.engine.add_to_group(fire, "fire")
            for i in range(1, 4):
                fire = Fire(self.rect.centerx - i * 50, self.rect.centery)
                if pygame.sprite.spritecollideany(
                        fire, self.engine.groups["walls"]):
                    fire.kill()
                    break
                self.engine.add_to_group(fire, "fire")
            for i in range(1, 4):
                fire = Fire(self.rect.centerx, self.rect.centery + i * 50)
                if pygame.sprite.spritecollideany(
                        fire, self.engine.groups["walls"]):
                    fire.kill()
                    break
                self.engine.add_to_group(fire, "fire")
            for i in range(1, 4):
                fire = Fire(self.rect.centerx, self.rect.centery - i * 50)
                if pygame.sprite.spritecollideany(
                        fire, self.engine.groups["walls"]):
                    fire.kill()
                    break
                self.engine.add_to_group(fire, "fire")
        if self.life_time == 20:
            self.surf = self.image_explosion_2
        if self.life_time == 10:
            self.surf = self.image_explosion_3
        if not self.life_time:
            self.kill()


class Fire(EngineSprite):
    def __init__(self, center_x, center_y):
        super().__init__()
        self.image_explosion_1 = pygame.image.load(
            "images/explosion_1.png").convert_alpha()
        self.image_explosion_2 = pygame.image.load(
            "images/explosion_2.png").convert_alpha()
        self.image_explosion_3 = pygame.image.load(
            "images/explosion_3.png").convert_alpha()
        self.surf = self.image_explosion_1
        self.rect = self.surf.get_rect(center=(center_x, center_y))
        self.fire_time = 30

    def update(self):
        self.fire_time -= 1
        if self.fire_time == 20:
            self.surf = self.image_explosion_2
        if self.fire_time == 10:
            self.surf = self.image_explosion_3
        if not self.fire_time:
            self.kill()


class Enemy(EngineSprite):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "enemy")
        self.speed = 2
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
                                               SCREEN_HEIGHT // 2))
        self.timer = 60

    def update(self):
        if (pygame.sprite.spritecollideany(self, self.engine.groups["fire"])
                or pygame.sprite.spritecollideany(
                    self, self.engine.groups["player"])):
            self.engine.score += 10
            self.kill()

        player = self.engine.groups['player'].sprites()[0]

        if self.rect.centery - player.rect.centery > 0:
            self.rect.move_ip(0, -self.speed)
            self.move_collision_out(0, -self.speed)
            self.surf = self.image_back
        else:
            self.rect.move_ip(0, self.speed)
            self.move_collision_out(0, self.speed)
            self.surf = self.image_front

        if self.rect.centerx - player.rect.centerx > 0:
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

    def move_collision_out(self, x_speed: int, y_speed: int):
        if (pygame.sprite.spritecollideany(self, self.engine.groups["walls"])
                or pygame.sprite.spritecollideany(
                    self, self.engine.groups["bombs"])):
            self.rect.move_ip(-x_speed, -y_speed)

    def create_enemy(self):
        self.timer -= 1
        if not self.timer:
            Enemy()
            self.timer = 60

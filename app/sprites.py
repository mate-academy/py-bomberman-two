import pygame

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from engine import Engine
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_OBJ_SIZE,
    DEFAULT_PLAYER_SPEED, EXPLOSION_RANGE, BOMB_TIMER,
    DEFAULT_PLAYER_HP, BOMB_COOLDOWN
)


class EngineMixin:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.engine = Engine()


class EngineSprite(EngineMixin, pygame.sprite.Sprite):
    pass


class CollisionMixin:
    def move_collision_out(self, x_speed: int, y_speed: int):
        is_on_bomb = self.is_on_bomb if hasattr(self, "is_on_bomb") else False
        if (pygame.sprite.spritecollideany(
            self, self.engine.groups["walls"]
        ) or pygame.sprite.spritecollideany(
            self, self.engine.groups["bombs"]
        ) and not is_on_bomb):
            self.rect.move_ip(-x_speed, -y_speed)


class Player(EngineSprite, CollisionMixin):
    def __init__(self):
        super().__init__()
        self.engine.add_to_group(self, "player")
        self.engine.add_to_group(self, '__flammable')
        self.speed = DEFAULT_PLAYER_SPEED
        self.health_point = DEFAULT_PLAYER_HP
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
        self.check_alive()
        self.collisions_handling()
        self.handle_player_action()

    def handle_player_action(self):
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

    def check_alive(self):
        if self.health_point < 1:
            self.kill()

    def place_bomb(self):
        if not self.placed_bomb_clock:
            self.is_on_bomb = True
            Bomb(self.rect.center)
            self.placed_bomb_clock = BOMB_COOLDOWN

    def get_health(self):
        return self.health_point

    def get_speed(self):
        return self.speed

    def change_health(self, poit):
        self.health_point += poit

    def collisions_handling(self):
        clashed_enemy = pygame.sprite.spritecollideany(self, self.engine.groups["enemies"])
        if clashed_enemy:
            self.change_health(-10)
            clashed_enemy.kill()

    def kill(self) -> None:
        super(Player, self).kill()
        self.engine.running = False


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
        self.explode_range = EXPLOSION_RANGE
        self.time_to_explode = BOMB_TIMER

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
        if self.time_to_explode:
            self.time_to_explode -= 1
        else:
            self.explode()
            self.kill()

    def generate_fire(self):
        Fire(self.rect.center)
        width = self.rect.centerx
        for blow in range(1, self.explode_range + 1):
            height = self.rect.centery + blow * DEFAULT_OBJ_SIZE
            if self.check_wall_collide((width, height)):
                break
            Fire((width, height))

            height = self.rect.centery - blow * DEFAULT_OBJ_SIZE
            if self.check_wall_collide((width, height)):
                break
            Fire((width, height))

        height = self.rect.centery
        for blow in range(1, self.explode_range + 1):
            width = self.rect.centerx + blow * DEFAULT_OBJ_SIZE
            if self.check_wall_collide((width, height)):
                break
            Fire((width, height))

            width = self.rect.centerx - blow * DEFAULT_OBJ_SIZE
            if self.check_wall_collide((width, height)):
                break
            Fire((width, height))

    def check_wall_collide(self, center):
        for wall in self.engine.groups['walls']:
            if wall.rect.collidepoint(center):
                return True
        return False

    def explode(self):
        self.generate_fire()


class Fire(EngineSprite):
    def __init__(self, center_pos: tuple):
        super().__init__()
        self.engine.add_to_group(self, "fires")
        self.surf = pygame.image.load("images/explosion_1.png").convert_alpha()
        self.rect = self.surf.get_rect(center=center_pos)
        self.rect.center = self.get_self_center()
        self.lifetime = 30

    def update(self):
        self.animate()
        self.damage_to_flammable()

    def damage_to_flammable(self):
        flamed = pygame.sprite.spritecollideany(
            self, self.engine.groups["__flammable"]
        )
        if flamed:
            flamed.kill()

    def animate(self):
        self.lifetime -= 1
        if self.lifetime < 1:
            self.kill()
        elif self.lifetime < 15:
            self.surf = pygame.image.load(
                "images/explosion_3.png"
            ).convert_alpha()
        elif self.lifetime < 25:
            self.surf = pygame.image.load(
                "images/explosion_2.png"
            ).convert_alpha()

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

import sys
import random
import pygame
from player import Player
from wall import Wall
from bomb import Bomb
from explosion import Explosion
from spider import Spider
from config import Config

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)


class Bomberman:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.config = Config()

        self.screen = pygame.display.set_mode(
            [self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT]
        )

        self.ADDENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ADDENEMY, 2000)

        self.player = Player(self)
        self.walls = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.current_bombs = []
        self.explosions = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self._create_walls()

    def _create_walls(self):
        for wall_center in Wall.create_centers_of_walls(
                (self.config.SCREEN_WIDTH,
                 self.config.SCREEN_HEIGHT),
                (self.config.DEFAULT_OBJECT_SIZE,
                 self.config.DEFAULT_OBJECT_SIZE)
        ):
            wall = Wall(wall_center)
            self.walls.add(wall)
            self.all_sprites.add(wall)

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_SPACE] and self.config.TIMER <= 0:
                self._plant_bomb()

            self._player_update(pressed_keys)
            self._bombs_update()
            self._explosions_update()
            self._enemies_update()

            self.screen.fill(self.config.BACKGROUND_COLOR)
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)

            pygame.display.flip()

            self.clock.tick(self.config.FRAMES_PER_SECOND)
            self.config.TIMER -= 1

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == self.ADDENEMY:
                enemy = Spider(self)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def _plant_bomb(self):
        center_x = self.player.rect.center[0] // 50 * 50 + 25
        center_y = self.player.rect.center[1] // 50 * 50 + 25
        bomb = Bomb((center_x, center_y))
        self.current_bombs.append(bomb)
        self.all_sprites.add(bomb)
        self.config.TIMER = 60

    def _player_update(self, pressed_keys):
        self.player.update(pressed_keys)
        self._check_player_collision(self.walls, pressed_keys)
        self._check_player_collision(self.bombs, pressed_keys)
        self._check_player_is_on_bomb()

        collisions_with_enemies = pygame.sprite.spritecollide(
            self.player, self.enemies, True
        )
        if collisions_with_enemies:
            self.player.health -= 10 * len(collisions_with_enemies)
            self.player.score += 10 * len(collisions_with_enemies)

        if self.player.health <= 0:
            self.player.kill()
            pygame.quit()
            sys.exit()

    def _check_player_collision(self, objects, pressed_keys):
        collision = pygame.sprite.spritecollideany(self.player, objects)

        if collision:
            if pressed_keys[K_UP]:
                self.player.rect.top = collision.rect.bottom
            if pressed_keys[K_DOWN]:
                self.player.rect.bottom = collision.rect.top
            if pressed_keys[K_LEFT]:
                self.player.rect.left = collision.rect.right
            if pressed_keys[K_RIGHT]:
                self.player.rect.right = collision.rect.left

    def _check_player_is_on_bomb(self):
        for bomb in self.current_bombs:
            if not pygame.sprite.collide_rect(self.player, bomb):
                self.bombs.add(bomb)
                self.current_bombs.remove(bomb)

    def _bombs_update(self):
        for bomb in self.bombs:
            if bomb.time_to_explosion <= 0 or pygame.sprite.spritecollideany(
                    bomb, self.explosions
            ):
                bomb.kill()
                self._spread_explosion(bomb)
            else:
                bomb.time_to_explosion -= 1

    def _spread_explosion(self, bomb):
        coordinates = [bomb.rect.center]

        for direction in (
                (self.config.DEFAULT_OBJECT_SIZE, 0),
                (-self.config.DEFAULT_OBJECT_SIZE, 0),
                (0, self.config.DEFAULT_OBJECT_SIZE),
                (0, -self.config.DEFAULT_OBJECT_SIZE)
                          ):
            new_coordinates = (
                bomb.rect.center[0] + direction[0],
                bomb.rect.center[1] + direction[1]
            )
            for wall in self.walls:
                if wall.rect.collidepoint(new_coordinates):
                    break

            for i in range(5):
                coordinates.append((
                    bomb.rect.center[0] + i * direction[0],
                    bomb.rect.center[1] + i * direction[1]
                ))

        for value in coordinates:
            explosion = Explosion(value)
            self.explosions.add(explosion)
            self.all_sprites.add(explosion)

    def _explosions_update(self):
        collisions = pygame.sprite.groupcollide(
            self.enemies, self.explosions, True, False
        )

        if collisions:
            self.player.score += 10 * len(collisions)

        if pygame.sprite.spritecollideany(self.player, self.explosions):
            self.player.kill()
            pygame.quit()
            sys.exit()

        for explosion in self.explosions:
            if explosion.stage == 3:
                explosion.kill()
            else:
                explosion.update()

    def _enemies_update(self):
        for enemy in self.enemies:
            if enemy.is_moving is False:
                self._define_enemy_target(enemy)
                enemy.is_moving = True
            else:
                enemy.update()

    def _define_enemy_target(self, enemy):
        player_coordinates = (
            round(self.player.rect.center[0] / 50) * 50,
            round(self.player.rect.center[1] / 50) * 50,
        )

        if player_coordinates[0] > enemy.rect.center[0]:
            if player_coordinates[1] > enemy.rect.center[1]:
                enemy.target = [random.choice(["Right", "Down"]), 100]
            elif player_coordinates[1] < enemy.rect.center[1]:
                enemy.target = [random.choice(["Right", "Up"]), 100]
            else:
                enemy.target = ["Right", 100]

        elif player_coordinates[0] < enemy.rect.center[0]:
            if player_coordinates[1] > enemy.rect.center[1]:
                enemy.target = [random.choice(["Left", "Down"]), 100]
            elif player_coordinates[1] < enemy.rect.center[1]:
                enemy.target = [random.choice(["Left", "Up"]), 100]
            else:
                enemy.target = ["Left", 100]

        else:
            if player_coordinates[1] > enemy.rect.center[1]:
                enemy.target = ["Down", 100]
            else:
                enemy.target = ["Up", 100]


if __name__ == '__main__':
    bomberman = Bomberman()
    bomberman.run_game()

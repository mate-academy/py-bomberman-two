import pygame

# Settings
SCREEN_WIDTH = 650
SCREEN_HEIGHT = 650
DEFAULT_OBJ_SIZE = 50
FRAMES_PER_SECOND = 60


# Colors
GREEN = (0, 255, 0)
BLOOD_RED = (136, 8, 8)
BLACK = (0, 0, 0)

# Player
DEFAULT_PLAYER_SPEED = 5
DEFAULT_PLAYER_HP = 100
DEFAULT_SCORE = 0

# Player images
IMAGE_RIGHT = pygame.image.load("images/player_right.png")
IMAGE_LEFT = pygame.image.load("images/player_left.png")
IMAGE_BACK = pygame.image.load("images/player_back.png")
IMAGE_FRONT = pygame.image.load("images/player_front.png")

# Bomb
BOMB_TIMER = 0
EXPLODE_TIMER = 120

# Enemy
ENEMY_TIMER = 120

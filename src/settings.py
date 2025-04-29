import pygame
import os
from parallax_background import ParallaxBackground

# Initialize parallax background
parallax_background = None

def initialize_parallax_background():
    """Initialize the parallax background system"""
    global parallax_background
    parallax_background = ParallaxBackground()
    return parallax_background

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)  # Speed power-up
ORANGE = (255, 165, 0)  # Extra time power-up
CYAN = (0, 255, 255)    # Bonus
BACKGROUND_COLOR = (67, 154, 255)  # Light blue background
MAP_BACKGROUND_COLOR = (208, 132, 92)  # Light brown for map gaps

# UI Colors
BUTTON_COLOR = (255, 255, 255)
BUTTON_HOVER_COLOR = (200, 200, 200)
BUTTON_TEXT_COLOR = (67, 154, 255)

# Font settings
pygame.font.init()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Game variables
BLOCK_SIZE = 40
BLOCK_GAP = 5
BLOCK_VISUAL_SIZE = BLOCK_SIZE - BLOCK_GAP
LEVEL_TIME = 15

# Block padding
BLOCK_PADDING = 2
ACTUAL_BLOCK_SIZE = BLOCK_SIZE - (2 * BLOCK_PADDING)

# Movement and power-up settings
DEFAULT_MOVE_COOLDOWN = 10
SPEED_BOOST_COOLDOWN = 5
SPEED_BOOST_DURATION = 5000  # 5 seconds in milliseconds

# Power-up types
POWERUP_SPEED = "speed"
POWERUP_EXTRA_TIME = "extra_time"
BONUS = "bonus"

# Asset paths
ASSETS_BASE = os.path.join("c:\\", "app", "random_blocks", "assets")
WALLS_PATH = os.path.join(ASSETS_BASE, "images", "blocks", "obs", "Tiles", "Marble")
ROAD_IMAGE_PATH = os.path.join(ASSETS_BASE, "images", "blocks", "obs", "Tiles", "roads", "r_1.png")
CHARACTER_SKINS_PATH = os.path.join(ASSETS_BASE, "images", "PNG", "animals")
BONUS_IMAGE_PATH = os.path.join("c:\\", "app", "random_blocks", "assets", "images", "coins", "coin_27.png")
DOOR_A_IMAGE_PATH = os.path.join("c:\\", "app", "random_blocks", "assets", "images", "doors", "door(a).png")
DOOR_B_IMAGE_PATH = os.path.join("c:\\", "app", "random_blocks", "assets", "images", "doors", "door(b).png")

# Load door images with proper scaling and fallback
try:
    door_a_image = pygame.image.load(DOOR_A_IMAGE_PATH).convert_alpha()
    door_b_image = pygame.image.load(DOOR_B_IMAGE_PATH).convert_alpha()
    door_a_image = pygame.transform.scale(door_a_image, (BLOCK_SIZE - 2 * BLOCK_PADDING, BLOCK_SIZE - 2 * BLOCK_PADDING))
    door_b_image = pygame.transform.scale(door_b_image, (BLOCK_SIZE - 2 * BLOCK_PADDING, BLOCK_SIZE - 2 * BLOCK_PADDING))
except (pygame.error, FileNotFoundError):
    # Create distinct fallback door images
    door_a_image = pygame.Surface((BLOCK_SIZE - 2 * BLOCK_PADDING, BLOCK_SIZE - 2 * BLOCK_PADDING))
    door_b_image = pygame.Surface((BLOCK_SIZE - 2 * BLOCK_PADDING, BLOCK_SIZE - 2 * BLOCK_PADDING))
    door_a_image.fill(GREEN)
    door_b_image.fill(RED)
    # Add some visual distinction
    pygame.draw.rect(door_a_image, WHITE, door_a_image.get_rect(), 3)
    pygame.draw.rect(door_b_image, WHITE, door_b_image.get_rect(), 3)

# Create fallback road
road_image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
road_image.fill(MAP_BACKGROUND_COLOR)

# UI Constants
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 25

# Weather system
WEATHER = {
    "rain": {"movement_penalty": 0.8, "texture": "rain_overlay.png"},
    "snow": {"visibility_reduction": 0.3, "texture": "snow_flakes.png"}
}

# Achievement system
ACHIEVEMENTS = {
    "quick_finish": {"condition": "time_left > 10", "reward": 500},
    "speed_runner": {"condition": "steps < 20", "reward": 1000},
    "coin_collector": {"condition": "coins_collected > 5", "reward": 750}
}

# Difficulty levels
DIFFICULTY_LEVELS = {
    "Easy": {"time_multiplier": 1.2, "score_multiplier": 1.0},
    "Normal": {"time_multiplier": 1.0, "score_multiplier": 1.5},
    "Hard": {"time_multiplier": 0.8, "score_multiplier": 2.0}
}
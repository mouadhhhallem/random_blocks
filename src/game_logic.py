import random
import heapq
import pygame
import os
from settings import *
from parallax_background import ParallaxBackground

# Constants for block padding and map layout
BLOCK_PADDING = 2  # Padding around each block
ACTUAL_BLOCK_SIZE = BLOCK_SIZE - BLOCK_PADDING * 2  # Size of block content (image)
MAP_PADDING = 20  # Padding around the entire map
BORDER_COLOR = CYAN  # Color for map border

# Camera settings
CAMERA_OFFSET_X = SCREEN_WIDTH // 2  # Center camera horizontally
CAMERA_OFFSET_Y = SCREEN_HEIGHT // 2  # Center camera vertically
CAMERA_SMOOTHNESS = 0.1  # Camera follow smoothness (0 = instant, 1 = very slow)

# Initialize parallax background
parallax_background = None

def initialize_parallax_background():
    """Initialize the parallax background system"""
    global parallax_background
    parallax_background = ParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
    return parallax_background

def load_wall_images():
    """Load and scale wall block images"""
    wall_images = []
    if os.path.exists(WALLS_PATH):
        for filename in os.listdir(WALLS_PATH):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                try:
                    image_path = os.path.join(WALLS_PATH, filename)
                    image = pygame.image.load(image_path).convert_alpha()
                    image = pygame.transform.scale(image, (ACTUAL_BLOCK_SIZE, ACTUAL_BLOCK_SIZE))
                    wall_images.append(image)
                except pygame.error as e:
                    print(f"Error loading wall image {filename}: {e}")
    else:
        print(f"Walls directory not found: {WALLS_PATH}")
    return wall_images

def load_character_skins():
    """Load and scale character skin images"""
    character_skins = []
    if os.path.exists(CHARACTER_SKINS_PATH):
        for filename in os.listdir(CHARACTER_SKINS_PATH):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                try:
                    image_path = os.path.join(CHARACTER_SKINS_PATH, filename)
                    image = pygame.image.load(image_path).convert_alpha()
                    image = pygame.transform.scale(image, (ACTUAL_BLOCK_SIZE, ACTUAL_BLOCK_SIZE))
                    character_skins.append(image)
                except pygame.error as e:
                    print(f"Error loading character skin {filename}: {e}")
    else:
        print(f"Character skins directory not found: {CHARACTER_SKINS_PATH}")
    return character_skins

def load_bonus_image():
    """Load and scale bonus item image"""
    try:
        bonus_image = pygame.image.load(BONUS_IMAGE_PATH).convert_alpha()
        return pygame.transform.scale(bonus_image, (ACTUAL_BLOCK_SIZE, ACTUAL_BLOCK_SIZE))
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading bonus image: {e}")
        # Create fallback colored circle if image can't be loaded
        surface = pygame.Surface((ACTUAL_BLOCK_SIZE, ACTUAL_BLOCK_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(surface, CYAN, (ACTUAL_BLOCK_SIZE // 2, ACTUAL_BLOCK_SIZE // 2), ACTUAL_BLOCK_SIZE // 3)
        return surface

def get_powerup_distribution(level):
    """Calculate power-up distribution based on level difficulty"""
    if level <= 10:  # Early levels
        return {
            POWERUP_SPEED: 1,  # Reduced speed powerups
            POWERUP_EXTRA_TIME: 0,
            BONUS: random.randint(2, 3)  # Increased money powerups
        }
    elif level <= 50:  # Mid levels
        return {
            POWERUP_SPEED: 1,
            POWERUP_EXTRA_TIME: 1,
            BONUS: random.randint(2, 4)  # More money powerups
        }
    else:  # Advanced levels
        return {
            POWERUP_SPEED: 1 if random.random() < 0.3 else 0,
            POWERUP_EXTRA_TIME: 1 if random.random() < 0.2 else 0,
            BONUS: random.randint(1, 3)  # Guaranteed money powerups
        }

def generate_map(rows, cols, level):
    """Generate game map with guaranteed path and power-ups"""
    max_attempts = 10
    wall_images = load_wall_images()

    for _ in range(max_attempts):
        grid = [[0 for _ in range(cols)] for _ in range(rows)]

        # Determine start and end positions
        start_corner = random.choice(["top_left", "top_right", "bottom_left", "bottom_right"])
        if start_corner == "top_left":
            start_pos = (0, 0)
            end_pos = (cols - 1, rows - 1)
        elif start_corner == "top_right":
            start_pos = (cols - 1, 0)
            end_pos = (0, rows - 1)
        elif start_corner == "bottom_left":
            start_pos = (0, rows - 1)
            end_pos = (cols - 1, 0)
        else:  # bottom_right
            start_pos = (cols - 1, rows - 1)
            end_pos = (0, 0)

        # Clear start and end positions
        grid[start_pos[1]][start_pos[0]] = 0
        grid[end_pos[1]][end_pos[0]] = 0

        # Generate path from start to end
        x, y = start_pos
        while x != end_pos[0] or y != end_pos[1]:
            if x < end_pos[0]: x += 1
            elif x > end_pos[0]: x -= 1
            elif y < end_pos[1]: y += 1
            elif y > end_pos[1]: y -= 1
            if x < cols and y < rows:
                grid[y][x] = 0

        # Add random walls
        for y in range(rows):
            for x in range(cols):
                if grid[y][x] == 0 and (x, y) != start_pos and (x, y) != end_pos:
                    if random.random() < 0.3:
                        grid[y][x] = random.choice(wall_images) if wall_images else 1

        # Add power-ups
        powerups = []
        distribution = get_powerup_distribution(level)

        for powerup_type, count in distribution.items():
            for _ in range(count):
                pos = place_powerup(grid, powerups, start_pos, end_pos, rows, cols)
                if pos:
                    powerups.append((pos[0], pos[1], powerup_type))

        # Verify path exists
        if dijkstra(grid, start_pos, end_pos):
            map_width = cols * (BLOCK_SIZE + BLOCK_GAP) - BLOCK_GAP
            map_height = rows * (BLOCK_SIZE + BLOCK_GAP) - BLOCK_GAP
            map_background = pygame.Surface((map_width, map_height))
            map_background.fill(MAP_BACKGROUND_COLOR)
            return grid, powerups, start_pos, end_pos, map_background

    # Fallback to empty map if generation fails
    return [[0 for _ in range(cols)] for _ in range(rows)], [], (0, 0), (cols - 1, rows - 1), None

def place_powerup(grid, powerups, start_pos, end_pos, rows, cols):
    """Attempt to place a power-up in a valid position"""
    attempts = 0
    while attempts < 10:
        x = random.randint(0, cols - 1)
        y = random.randint(0, rows - 1)

        # Check if position is valid
        if (grid[y][x] == 0 and (x, y) != start_pos and (x, y) != end_pos and
                not any(px == x and py == y for px, py, _ in powerups) and
                dijkstra(grid, start_pos, (y, x))):
            return x, y
        attempts += 1
    return None

def dijkstra(grid, start, end):
    """Pathfinding algorithm to verify valid paths"""
    rows, cols = len(grid), len(grid[0])
    if not (0 <= start[0] < cols and 0 <= start[1] < rows and
            0 <= end[0] < cols and 0 <= end[1] < rows):
        return False

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    heap = [(0, start)]
    visited = set()

    while heap:
        cost, (x, y) = heapq.heappop(heap)
        if (x, y) == end:
            return True
        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < cols and 0 <= ny < rows and
                    grid[ny][nx] == 0 and (nx, ny) not in visited):
                heapq.heappush(heap, (cost + 1, (nx, ny)))
    return False

def draw_map(screen, grid, powerups, camera_x, camera_y, start_pos, end_pos,
             character_pos, character_image, bonus_image, map_background):
    """Draw the complete game map with all elements"""
    # Draw parallax background first
    if parallax_background:
        parallax_background.update(camera_x * 0.2)  # Slower camera movement for background
        parallax_background.draw(screen)
    else:
        screen.fill(BACKGROUND_COLOR)

    # Draw map background and border
    if map_background:
        screen.blit(map_background, (-camera_x + MAP_PADDING, -camera_y + MAP_PADDING))

    # Draw border
    map_width = len(grid[0]) * (BLOCK_SIZE + BLOCK_GAP) - BLOCK_GAP
    map_height = len(grid) * (BLOCK_SIZE + BLOCK_GAP) - BLOCK_GAP
    border_rect = pygame.Rect(
        -camera_x + MAP_PADDING - BLOCK_GAP,
        -camera_y + MAP_PADDING - BLOCK_GAP,
        map_width + 2 * BLOCK_GAP,
        map_height + 2 * BLOCK_GAP
    )
    pygame.draw.rect(screen, BORDER_COLOR, border_rect, BLOCK_PADDING)

    # Draw grid elements
    for y, row in enumerate(grid):
        for x, block in enumerate(row):
            screen_x = x * (BLOCK_SIZE + BLOCK_GAP) - camera_x + MAP_PADDING
            screen_y = y * (BLOCK_SIZE + BLOCK_GAP) - camera_y + MAP_PADDING

            if not is_visible_on_screen(screen_x, screen_y):
                continue

            # Draw appropriate block type
            draw_block(screen, block, screen_x, screen_y)

            # Draw doors
            if (x, y) == start_pos:
                screen.blit(door_a_image, (screen_x + BLOCK_PADDING, screen_y + BLOCK_PADDING))
            elif (x, y) == end_pos:
                screen.blit(door_b_image, (screen_x + BLOCK_PADDING, screen_y + BLOCK_PADDING))

    # Draw power-ups
    for x, y, type in powerups:
        screen_x = x * (BLOCK_SIZE + BLOCK_GAP) - camera_x + MAP_PADDING
        screen_y = y * (BLOCK_SIZE + BLOCK_GAP) - camera_y + MAP_PADDING

        if not is_visible_on_screen(screen_x, screen_y):
            continue

        draw_powerup(screen, type, screen_x, screen_y, bonus_image)

    # Draw character
    char_screen_x = (character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) -
                    camera_x + MAP_PADDING + BLOCK_PADDING)
    char_screen_y = (character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) -
                    camera_y + MAP_PADDING + BLOCK_PADDING)

    if is_visible_on_screen(char_screen_x, char_screen_y):
        screen.blit(character_image, (char_screen_x, char_screen_y))

def is_visible_on_screen(x, y):
    """Check if an element is visible within the screen bounds"""
    return -BLOCK_SIZE <= x < SCREEN_WIDTH and -BLOCK_SIZE <= y < SCREEN_HEIGHT

def draw_block(screen, block, x, y):
    """Draw a single block element"""
    if block == 0:  # Road
        pygame.draw.rect(screen, MAP_BACKGROUND_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))
    elif block == 1:  # Default wall
        pygame.draw.rect(screen, MAP_BACKGROUND_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))
    else:  # Wall with image
        screen.blit(block, (x + BLOCK_PADDING, y + BLOCK_PADDING))

def draw_powerup(screen, type, x, y, bonus_image):
    """Draw a power-up with appropriate visualization"""
    powerup_x = x + BLOCK_PADDING
    powerup_y = y + BLOCK_PADDING
    center_x = powerup_x + ACTUAL_BLOCK_SIZE // 2
    center_y = powerup_y + ACTUAL_BLOCK_SIZE // 2

    if type == POWERUP_SPEED:
        pygame.draw.circle(screen, YELLOW, (center_x, center_y), ACTUAL_BLOCK_SIZE // 3)
    elif type == POWERUP_EXTRA_TIME:
        pygame.draw.circle(screen, ORANGE, (center_x, center_y), ACTUAL_BLOCK_SIZE // 3)
    elif type == BONUS:
        screen.blit(bonus_image, (powerup_x, powerup_y))

def check_achievements(level, time_left, steps, coins_collected):
    """Check and return newly unlocked achievements"""
    achievements_unlocked = []
    for achievement, details in ACHIEVEMENTS.items():
        condition = details["condition"]
        try:
            condition_func = eval(f"lambda level, time_left, steps, coins_collected: {condition}")
            if condition_func(level, time_left, steps, coins_collected):
                achievements_unlocked.append(achievement)
        except Exception as e:
            print(f"Error evaluating achievement condition: {e}")
    return achievements_unlocked

def apply_weather_effects(weather, movement_cooldown):
    """Apply weather-based movement modifications"""
    if weather not in WEATHER:
        return movement_cooldown

    weather_data = WEATHER[weather]
    if weather == "rain":
        movement_cooldown *= weather_data.get("movement_penalty", 0.8)
    elif weather == "snow":
        movement_cooldown *= weather_data.get("movement_penalty", 0.5)
    return movement_cooldown
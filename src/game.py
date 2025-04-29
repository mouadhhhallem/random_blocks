import pygame
from settings import *
from game_logic import generate_map, draw_map, load_character_skins, load_bonus_image, check_achievements, apply_weather_effects

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

# Function to start the game loop
def start_game():
    global LEVEL, ROWS, COLS, SCORE, START_TIME, STEPS, COINS_COLLECTED, character_image, bonus_image, grid, powerups, start_pos, end_pos, map_background, camera_x, camera_y, move_cooldown, speed_boost, speed_boost_timer, current_weather, achievements_unlocked

    LEVEL = 1
    ROWS = 5
    COLS = 5
    SCORE = 0
    START_TIME = pygame.time.get_ticks()
    STEPS = 0
    COINS_COLLECTED = 0

    character_skins = load_character_skins()
    character_image = random.choice(character_skins) if character_skins else None
    bonus_image = load_bonus_image()

    grid, powerups, start_pos, end_pos, map_background = generate_map(ROWS, COLS, LEVEL)
    character_pos = list(start_pos)

    camera_x = 0
    camera_y = 0

    move_cooldown = 0
    DEFAULT_MOVE_COOLDOWN = 10
    SPEED_BOOST_COOLDOWN = 5

    speed_boost = False
    speed_boost_timer = 0
    SPEED_BOOST_DURATION = 5000

    current_weather = random.choice(list(WEATHER.keys()))
    achievements_unlocked = []

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)

        target_camera_x = character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_WIDTH // 2
        target_camera_y = character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_HEIGHT // 2
        camera_x += (target_camera_x - camera_x) * CAMERA_SMOOTHNESS
        camera_y += (target_camera_y - camera_y) * CAMERA_SMOOTHNESS

        draw_map(screen, grid, powerups, camera_x, camera_y, start_pos, end_pos, character_pos, character_image, bonus_image, map_background)

        level_text = font.render(f"Level: {LEVEL}", True, WHITE)
        screen.blit(level_text, (10, 10))
        score_text = font.render(f"Score: {SCORE}", True, WHITE)
        screen.blit(score_text, (10, 50))
        time_left = max(0, LEVEL_TIME - (pygame.time.get_ticks() - START_TIME) // 1000)
        timer_text = font.render(f"Time: {time_left}", True, WHITE)
        screen.blit(timer_text, (10, 90))

        weather_text = font.render(f"Weather: {current_weather.capitalize()}", True, WHITE)
        screen.blit(weather_text, (10, 130))
        achievements_text = font.render(f"Achievements: {', '.join(achievements_unlocked)}", True, WHITE)
        screen.blit(achievements_text, (10, 170))

        keys = pygame.key.get_pressed()
        if move_cooldown <= 0:
            if keys[pygame.K_UP] and character_pos[1] > 0 and grid[character_pos[1] - 1][character_pos[0]] == 0:
                character_pos[1] -= 1
                STEPS += 1
                move_cooldown = SPEED_BOOST_COOLDOWN if speed_boost else DEFAULT_MOVE_COOLDOWN
            if keys[pygame.K_DOWN] and character_pos[1] < ROWS - 1 and grid[character_pos[1] + 1][character_pos[0]] == 0:
                character_pos[1] += 1
                STEPS += 1
                move_cooldown = SPEED_BOOST_COOLDOWN if speed_boost else DEFAULT_MOVE_COOLDOWN
            if keys[pygame.K_LEFT] and character_pos[0] > 0 and grid[character_pos[1]][character_pos[0] - 1] == 0:
                character_pos[0] -= 1
                STEPS += 1
                move_cooldown = SPEED_BOOST_COOLDOWN if speed_boost else DEFAULT_MOVE_COOLDOWN
            if keys[pygame.K_RIGHT] and character_pos[0] < COLS - 1 and grid[character_pos[1]][character_pos[0] + 1] == 0:
                character_pos[0] += 1
                STEPS += 1
                move_cooldown = SPEED_BOOST_COOLDOWN if speed_boost else DEFAULT_MOVE_COOLDOWN
        else:
            move_cooldown -= 1

        move_cooldown = apply_weather_effects(current_weather, move_cooldown)

        new_achievements = check_achievements(LEVEL, time_left, STEPS, COINS_COLLECTED)
        for achievement in new_achievements:
            if achievement not in achievements_unlocked:
                achievements_unlocked.append(achievement)
                print(f"Achievement Unlocked: {achievement}")

        for powerup in powerups[:]:
            x, y, type = powerup
            if character_pos[0] == x and character_pos[1] == y:
                if type == POWERUP_SPEED:
                    speed_boost = True
                    speed_boost_timer = pygame.time.get_ticks() + SPEED_BOOST_DURATION
                elif type == POWERUP_EXTRA_TIME:
                    LEVEL_TIME += 5
                elif type == BONUS:
                    COINS_COLLECTED += 1
                    SCORE += 500
                powerups.remove(powerup)

        if speed_boost and pygame.time.get_ticks() > speed_boost_timer:
            speed_boost = False

        if character_pos[0] == end_pos[0] and character_pos[1] == end_pos[1]:
            LEVEL += 1
            remaining_time = max(0, LEVEL_TIME - (pygame.time.get_ticks() - START_TIME) // 1000)
            LEVEL_TIME = remaining_time + 2
            if LEVEL % 2 == 0:
                COLS += 1
            else:
                ROWS += 1
            grid, powerups, start_pos, end_pos, map_background = generate_map(ROWS, COLS, LEVEL)
            character_pos = list(start_pos)
            SCORE += 1000 // (pygame.time.get_ticks() - START_TIME)
            START_TIME = pygame.time.get_ticks()

        if time_left <= 0:
            show_score_popup()
            LEVEL = 1
            ROWS = 5
            COLS = 5
            SCORE = 0
            STEPS = 0
            COINS_COLLECTED = 0
            LEVEL_TIME = 15
            START_TIME = pygame.time.get_ticks()
            grid, powerups, start_pos, end_pos, map_background = generate_map(ROWS, COLS, LEVEL)
            character_pos = list(start_pos)
            character_image = random.choice(character_skins) if character_skins else None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# Function to display the score popup
def show_score_popup():
    popup_width = 600
    popup_height = 400
    popup_x = (SCREEN_WIDTH - popup_width) // 2
    popup_y = (SCREEN_HEIGHT - popup_height) // 2
    popup_alpha = 0

    final_score = calculate_score()
    save_top_score(final_score)

    try:
        with open(SCORES_FILE, "r") as file:
            top_score = int(file.read())
    except FileNotFoundError:
        top_score = 0

    animated_score = 0
    animation_step = 0
    animation_delay = 30
    animation_timer = 0

    reset_button = pygame.Rect(popup_x + 200, popup_y + 300, 200, 50)
    reset_button_color = (0, 128, 255)
    reset_text = font.render("Reset Game", True, WHITE)

    while popup_alpha < 255 or animation_step < 3:
        screen.fill(BACKGROUND_COLOR)
        draw_map(screen, grid, powerups, camera_x, camera_y, start_pos, end_pos, character_pos, character_image, bonus_image, map_background)

        popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        pygame.draw.rect(popup_surface, (0, 0, 0, popup_alpha), (0, 0, popup_width, popup_height), border_radius=20)
        screen.blit(popup_surface, (popup_x, popup_y))

        if animation_step == 0:
            animated_score = LEVEL * 2000
        elif animation_step == 1:
            animated_score += COINS_COLLECTED * 500
        elif animation_step == 2:
            animated_score -= STEPS * 2

        animated_score = max(animated_score, 100)

        score_text = large_font.render(f"Final Score: {animated_score}", True, WHITE)
        top_score_text = font.render(f"Top Score: {top_score}", True, WHITE)
        screen.blit(score_text, (popup_x + 50, popup_y + 100))
        screen.blit(top_score_text, (popup_x + 50, popup_y + 200))

        pygame.draw.rect(screen, reset_button_color, reset_button, border_radius=10)
        screen.blit(reset_text, (reset_button.x + 50, reset_button.y + 15))

        if popup_alpha < 255:
            popup_alpha += 5

        animation_timer += 1
        if animation_timer >= animation_delay:
            animation_step += 1
            animation_timer = 0

        pygame.display.flip()
        clock.tick(60)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button.collidepoint(event.pos):
                    waiting = False

# Function to calculate the score
def calculate_score():
    global SCORE, STEPS, COINS_COLLECTED, LEVEL
    SCORE = (LEVEL * 2000) + (COINS_COLLECTED * 500) - (STEPS * 2)
    return max(SCORE, 100)

# Function to save the top score
def save_top_score(score):
    try:
        with open(SCORES_FILE, "r") as file:
            top_score = int(file.read())
    except FileNotFoundError:
        top_score = 0
    if score > top_score:
        with open(SCORES_FILE, "w") as file:
            file.write(str(score))
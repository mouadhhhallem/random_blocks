import pygame
import random
import os
import time
import math
import sys
from settings import *
from game_logic import generate_map, draw_map, load_character_skins, load_bonus_image, check_achievements, apply_weather_effects
from score_manager import ScoreManager
from sound_manager import SoundManager
from modern_background import ModernBackground, EnhancedParallaxBackground
from particle_system import ParticleSystem
import menu

# Initialize Pygame
pygame.init()

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Blocks Game")

# Initialize managers
score_manager = ScoreManager()
sound_manager = SoundManager()

# Global variables
debug_mode = False  # Added debug_mode as a global variable

# Load custom fonts
def load_custom_fonts():
    fonts = {}
    try:
        # Try to load custom fonts if available
        fonts['title'] = pygame.font.Font(None, 92)
        fonts['heading'] = pygame.font.Font(None, 64)
        fonts['button'] = pygame.font.Font(None, 48)
        fonts['info'] = pygame.font.Font(None, 36)
        fonts['small'] = pygame.font.Font(None, 24)
    except:
        # Fallback to system fonts
        fonts['title'] = pygame.font.SysFont('arial', 92)
        fonts['heading'] = pygame.font.SysFont('arial', 64)
        fonts['button'] = pygame.font.SysFont('arial', 48)
        fonts['info'] = pygame.font.SysFont('arial', 36)
        fonts['small'] = pygame.font.SysFont('arial', 24)
    return fonts

# Add compatibility methods to SoundManager
def play_sound(self, sound_name):
    """Compatibility method to map generic sound names to specific methods"""
    if sound_name == "level_start" or sound_name == "menu_move":
        self.play_menu_theme()
    elif sound_name == "level_complete" or sound_name == "victory":
        self.play_victory()
    elif sound_name == "game_over":
        self.stop_music()
    elif sound_name == "pause":
        self.pause_music()
    elif sound_name == "unpause":
        self.unpause_music()
    # Other sounds are ignored silently

# Add compatibility methods to ScoreManager
def get_score(self):
    """Compatibility method to get current score"""
    # Use best score as current score
    best_scores = self.get_best_scores()
    return best_scores.get("all_time", 0)

def add_score(self, points):
    """Compatibility method to add score points"""
    # Store score in memory for this session
    if not hasattr(self, 'current_score'):
        self.current_score = 0
    self.current_score += points
    
    # Try to save score
    try:
        self.save_score(points, "Normal", 0)
    except Exception as e:
        print(f"Error saving score: {e}")

# Add compatibility methods to classes
SoundManager.play_sound = play_sound
ScoreManager.get_score = get_score
ScoreManager.add_score = add_score

class GameState:
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"  # New state for pause menu

# Modern animated button class
class AnimatedButton:
    def __init__(self, x, y, width, height, text, action=None, color_scheme="blue", icon=None):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.icon = icon
        
        # Color schemes
        self.schemes = {
            "blue": {
                "normal": (41, 128, 185),
                "hover": (52, 152, 219),
                "press": (31, 97, 141),
                "text": (255, 255, 255),
                "shadow": (26, 82, 118),
                "glow": (52, 152, 219, 100)
            },
            "green": {
                "normal": (39, 174, 96),
                "hover": (46, 204, 113),
                "press": (30, 132, 73),
                "text": (255, 255, 255),
                "shadow": (20, 90, 50),
                "glow": (46, 204, 113, 100)
            },
            "red": {
                "normal": (192, 57, 43),
                "hover": (231, 76, 60),
                "press": (146, 43, 33),
                "text": (255, 255, 255),
                "shadow": (100, 30, 22),
                "glow": (231, 76, 60, 100)
            },
            "purple": {
                "normal": (142, 68, 173),
                "hover": (155, 89, 182),
                "press": (108, 52, 131),
                "text": (255, 255, 255),
                "shadow": (74, 35, 90),
                "glow": (155, 89, 182, 100)
            },
            "dark": {
                "normal": (44, 62, 80),
                "hover": (52, 73, 94),
                "press": (33, 47, 61),
                "text": (255, 255, 255),
                "shadow": (20, 29, 38),
                "glow": (52, 73, 94, 100)
            }
        }
        
        self.color_scheme = self.schemes.get(color_scheme, self.schemes["blue"])
        self.fonts = load_custom_fonts()
        self.state = "normal"  # normal, hover, press
        
        # Animation properties
        self.hover_scale = 1.05
        self.press_scale = 0.95
        self.current_scale = 1.0
        self.target_scale = 1.0
        self.animation_speed = 0.2
        
        # Glow effect
        self.glow_radius = 0
        self.target_glow = 0
        self.max_glow = 20
        
        # Shadow offset
        self.shadow_offset = 4
        
        # Pulse animation
        self.pulse_time = 0
        self.pulse_duration = 0
        self.pulse_max = 30

    def update(self):
        # Update scale with smooth animation
        if self.current_scale != self.target_scale:
            self.current_scale += (self.target_scale - self.current_scale) * self.animation_speed
            
            # Update rectangle size based on scale
            width = int(self.original_rect.width * self.current_scale)
            height = int(self.original_rect.height * self.current_scale)
            self.rect.width = width
            self.rect.height = height
            self.rect.x = self.original_rect.x + (self.original_rect.width - width) // 2
            self.rect.y = self.original_rect.y + (self.original_rect.height - height) // 2
        
        # Update glow effect
        if self.glow_radius != self.target_glow:
            self.glow_radius += (self.target_glow - self.glow_radius) * self.animation_speed
        
        # Update pulse animation
        if self.pulse_duration > 0:
            self.pulse_time += 1
            if self.pulse_time >= self.pulse_duration:
                self.pulse_time = 0
                self.pulse_duration = 0

    def draw(self, surface):
        self.update()
        
        # Draw glow effect if hovered
        if self.glow_radius > 0:
            glow_surf = pygame.Surface((self.rect.width + self.max_glow*2, self.rect.height + self.max_glow*2), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surf, 
                self.color_scheme["glow"], 
                (self.max_glow, self.max_glow, self.rect.width, self.rect.height),
                border_radius=15
            )
            try:
                glow_surf = pygame.transform.gaussian_blur(glow_surf, self.glow_radius)
            except:
                # Fallback if gaussian_blur is not available
                pass
            surface.blit(glow_surf, (self.rect.x - self.max_glow, self.rect.y - self.max_glow))
        
        # Draw shadow
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_offset,
            self.rect.y + self.shadow_offset,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(
            surface, 
            self.color_scheme["shadow"], 
            shadow_rect,
            border_radius=15
        )
        
        # Draw button
        pygame.draw.rect(
            surface, 
            self.color_scheme[self.state], 
            self.rect,
            border_radius=15
        )
        
        # Add subtle gradient effect
        gradient = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for i in range(self.rect.height // 2):
            alpha = 100 - (i * 2)
            if alpha > 0:
                pygame.draw.rect(
                    gradient, 
                    (255, 255, 255, alpha), 
                    (0, i, self.rect.width, 2),
                    border_radius=15
                )
        surface.blit(gradient, self.rect.topleft)
        
        # Draw text with shadow for depth
        text_surface = self.fonts['button'].render(self.text, True, (0, 0, 0, 128))
        text_rect = text_surface.get_rect(center=(self.rect.center[0] + 2, self.rect.center[1] + 2))
        surface.blit(text_surface, text_rect)
        
        text_surface = self.fonts['button'].render(self.text, True, self.color_scheme["text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Draw icon if provided
        if self.icon:
            icon_rect = self.icon.get_rect(midleft=(self.rect.x + 20, self.rect.centery))
            surface.blit(self.icon, icon_rect)
        
        # Draw pulse effect if active
        if self.pulse_duration > 0:
            pulse_alpha = int(255 * (1 - abs(self.pulse_time / self.pulse_duration - 0.5) * 2))
            pulse_surf = pygame.Surface((self.rect.width + self.pulse_max*2, self.rect.height + self.pulse_max*2), pygame.SRCALPHA)
            pygame.draw.rect(
                pulse_surf, 
                (*self.color_scheme["hover"], pulse_alpha), 
                (0, 0, self.rect.width + self.pulse_max*2, self.rect.height + self.pulse_max*2),
                border_radius=20
            )
            surface.blit(pulse_surf, (self.rect.x - self.pulse_max, self.rect.y - self.pulse_max))

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        
        # Update state and animation targets based on hover state
        if hovered and self.state == "normal":
            self.state = "hover"
            self.target_scale = self.hover_scale
            self.target_glow = self.max_glow
        elif not hovered and self.state == "hover":
            self.state = "normal"
            self.target_scale = 1.0
            self.target_glow = 0
            
        return hovered
    
    def is_pressed(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = "press"
                self.target_scale = self.press_scale
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == "press":
                self.state = "hover" if self.rect.collidepoint(event.pos) else "normal"
                self.target_scale = self.hover_scale if self.state == "hover" else 1.0
                self.pulse_time = 0
                self.pulse_duration = 30
                return self.rect.collidepoint(event.pos)
        return False

# Modern panel class
class Panel:
    def __init__(self, x, y, width, height, color=(30, 30, 30, 200), border_radius=15, border_color=None, border_width=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.border_radius = border_radius
        self.border_color = border_color
        self.border_width = border_width
    
    def draw(self, surface):
        # Draw panel with alpha
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface, 
            self.color, 
            (0, 0, self.rect.width, self.rect.height),
            border_radius=self.border_radius
        )
        
        # Draw border if specified
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(
                panel_surface, 
                self.border_color, 
                (0, 0, self.rect.width, self.rect.height),
                width=self.border_width,
                border_radius=self.border_radius
            )
            
        surface.blit(panel_surface, self.rect.topleft)

# Modern progress bar class
class ProgressBar:
    def __init__(self, x, y, width, height, max_value, current_value=0, color_scheme="blue", label=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = current_value
        self.label = label
        self.fonts = load_custom_fonts()
        
        # Color schemes
        self.schemes = {
            "blue": {
                "bg": (41, 128, 185, 100),
                "fill": (52, 152, 219),
                "border": (26, 82, 118),
                "text": (255, 255, 255)
            },
            "green": {
                "bg": (39, 174, 96, 100),
                "fill": (46, 204, 113),
                "border": (20, 90, 50),
                "text": (255, 255, 255)
            },
            "red": {
                "bg": (192, 57, 43, 100),
                "fill": (231, 76, 60),
                "border": (100, 30, 22),
                "text": (255, 255, 255)
            },
            "purple": {
                "bg": (142, 68, 173, 100),
                "fill": (155, 89, 182),
                "border": (74, 35, 90),
                "text": (255, 255, 255)
            }
        }
        
        self.color_scheme = self.schemes.get(color_scheme, self.schemes["blue"])
        
        # Animation properties
        self.display_value = current_value
        self.animation_speed = 0.1
        
        # Pulse effect
        self.pulse_time = 0
        self.pulse_speed = 0.1
        
    def update(self, new_value):
        self.current_value = min(max(0, new_value), self.max_value)
        
    def draw(self, surface):
        # Animate the displayed value
        if self.display_value != self.current_value:
            self.display_value += (self.current_value - self.display_value) * self.animation_speed
        
        # Calculate fill width
        fill_width = int((self.display_value / self.max_value) * self.rect.width)
        
        # Update pulse effect
        self.pulse_time = (self.pulse_time + self.pulse_speed) % (2 * math.pi)
        pulse_factor = 0.05 * math.sin(self.pulse_time)
        
        # Draw background with alpha
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            bg_surface, 
            self.color_scheme["bg"], 
            (0, 0, self.rect.width, self.rect.height),
            border_radius=self.rect.height // 2
        )
        surface.blit(bg_surface, self.rect.topleft)
        
        # Draw fill with pulse effect
        if fill_width > 0:
            fill_height = self.rect.height * (1.0 + pulse_factor)
            fill_y = self.rect.y + (self.rect.height - fill_height) / 2
            
            pygame.draw.rect(
                surface, 
                self.color_scheme["fill"], 
                (self.rect.x, fill_y, fill_width, fill_height),
                border_radius=self.rect.height // 2
            )
        
        # Draw border
        pygame.draw.rect(
            surface, 
            self.color_scheme["border"], 
            self.rect,
            width=2,
            border_radius=self.rect.height // 2
        )
        
        # Draw label if provided
        if self.label:
            label_text = f"{self.label}: {int(self.display_value)}/{self.max_value}"
            text_surface = self.fonts['small'].render(label_text, True, self.color_scheme["text"])
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

# Modern info display class
class InfoDisplay:
    def __init__(self, x, y, icon, text, font, color=WHITE, icon_size=32, spacing=10):
        self.x = x
        self.y = y
        self.icon = icon
        self.text = text
        self.font = font
        self.color = color
        self.icon_size = icon_size
        self.spacing = spacing
        
        # Create icon surface
        self.icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        self.icon_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.icon_surface, self.color, (0, 0, icon_size, icon_size), border_radius=5)
        
    def update(self, new_text):
        self.text = new_text
        
    def draw(self, surface):
        # Draw icon
        surface.blit(self.icon_surface, (self.x, self.y))
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, (self.x + self.icon_size + self.spacing, self.y + (self.icon_size - text_surface.get_height()) // 2))

# Modern notification class
class Notification:
    def __init__(self, text, duration=3000, color_scheme="blue"):
        self.text = text
        self.duration = duration
        self.creation_time = pygame.time.get_ticks()
        self.fonts = load_custom_fonts()
        
        # Color schemes
        self.schemes = {
            "blue": (41, 128, 185),
            "green": (39, 174, 96),
            "red": (192, 57, 43),
            "purple": (142, 68, 173),
            "dark": (44, 62, 80)
        }
        
        self.color = self.schemes.get(color_scheme, self.schemes["blue"])
        
        # Animation properties
        self.alpha = 0
        self.target_alpha = 255
        self.animation_speed = 0.1
        
    def update(self):
        # Check if notification has expired
        current_time = pygame.time.get_ticks()
        time_passed = current_time - self.creation_time
        
        if time_passed > self.duration:
            self.target_alpha = 0
            
        # Update alpha with smooth animation
        if self.alpha != self.target_alpha:
            self.alpha += (self.target_alpha - self.alpha) * self.animation_speed
            
        # Return True if notification is still active
        return self.alpha > 1
        
    def draw(self, surface, x, y):
        # Create notification surface with alpha
        text_surface = self.fonts['info'].render(self.text, True, WHITE)
        padding = 20
        width = text_surface.get_width() + padding * 2
        height = text_surface.get_height() + padding
        
        notification_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(
            notification_surface, 
            (*self.color, int(self.alpha)), 
            (0, 0, width, height),
            border_radius=10
        )
        
        # Add subtle gradient
        for i in range(height // 2):
            alpha = int(50 * (1 - i / (height / 2)) * (self.alpha / 255))
            if alpha > 0:
                pygame.draw.rect(
                    notification_surface, 
                    (255, 255, 255, alpha), 
                    (0, i, width, 2),
                    border_radius=10
                )
        
        # Draw text with alpha
        text_surface.set_alpha(int(self.alpha))
        notification_surface.blit(text_surface, (padding, padding // 2))
        
        # Draw notification
        surface.blit(notification_surface, (x - width // 2, y))

# Game class
class Game:
    def __init__(self):
        # Initialize screen
        self.screen = screen
        
        # Initialize game state
        self.state = GameState.MENU
        
        # Initialize game variables
        self.level = 1
        self.rows = 5
        self.cols = 5
        self.score = 0
        self.steps = 0
        self.coins_collected = 0
        self.level_time = LEVEL_TIME
        self.start_time = pygame.time.get_ticks()
        
        # Initialize game elements
        self.grid = None
        self.powerups = None
        self.start_pos = None
        self.end_pos = None
        self.character_pos = None
        self.character_image = None
        self.bonus_image = None
        self.map_background = None
        
        # Initialize camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Initialize movement
        self.move_cooldown = 0
        self.default_move_cooldown = DEFAULT_MOVE_COOLDOWN
        self.speed_boost = False
        self.speed_boost_timer = 0
        
        # Initialize weather
        self.current_weather = random.choice(list(WEATHER.keys()))
        self.achievements_unlocked = []
        
        # Initialize notifications
        self.notifications = []
        
        # Load fonts
        self.fonts = load_custom_fonts()
        
        # Initialize modern background
        self.modern_background = ModernBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.enhanced_parallax = EnhancedParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Initialize particle system for visual effects
        self.particle_system = ParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Use menu module for particles
        self.particles = menu.particles
        self.overlay = menu.overlay
        
        # Initialize menu buttons
        self.setup_menu_buttons()
        
        # Initialize pause menu buttons
        self.setup_pause_buttons()
        
        # Initialize game
        self.setup_game()
        
        # Initialize clock
        self.clock = pygame.time.Clock()
        self.fps_values = []  # Store recent FPS values for smoothing
        
    def setup_menu_buttons(self):
        # Create menu buttons
        button_width = 300
        button_height = 70
        button_spacing = 20
        start_y = SCREEN_HEIGHT // 2 - 100
        
        self.start_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y,
            button_width, button_height,
            "Start Game",
            None,
            "green"
        )
        
        self.scores_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + button_height + button_spacing,
            button_width, button_height,
            "High Scores",
            None,
            "blue"
        )
        
        self.settings_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 2 * (button_height + button_spacing),
            button_width, button_height,
            "Settings",
            None,
            "purple"
        )
        
        self.exit_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 3 * (button_height + button_spacing),
            button_width, button_height,
            "Exit",
            None,
            "red"
        )
        
        self.menu_buttons = [self.start_btn, self.scores_btn, self.settings_btn, self.exit_btn]
    
    def setup_pause_buttons(self):
        # Create pause menu buttons
        button_width = 300
        button_height = 70
        button_spacing = 20
        start_y = SCREEN_HEIGHT // 2 - 150
        
        self.resume_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y,
            button_width, button_height,
            "Resume",
            None,
            "green"
        )
        
        self.restart_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + button_height + button_spacing,
            button_width, button_height,
            "Restart",
            None,
            "blue"
        )
        
        self.menu_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 2 * (button_height + button_spacing),
            button_width, button_height,
            "Main Menu",
            None,
            "purple"
        )
        
        self.exit_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 3 * (button_height + button_spacing),
            button_width, button_height,
            "Exit",
            None,
            "red"
        )
        
        self.pause_buttons = [self.resume_btn, self.restart_btn, self.menu_btn, self.exit_btn]

    def add_notification(self, text, duration=3000, color_scheme="blue"):
        self.notifications.append(Notification(text, duration, color_scheme))

    def run(self):
        running = True
        while running:
            # Calculate and smooth FPS
            current_fps = self.clock.get_fps()
            self.fps_values.append(current_fps)
            if len(self.fps_values) > 10:  # Keep only the last 10 values
                self.fps_values.pop(0)
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.event.clear()  # Clear any pending events
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                        sound_manager.play_sound("pause")
                    elif event.key == pygame.K_ESCAPE and self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                        sound_manager.play_sound("unpause")
                    # Debug mode toggle
                    elif event.key == pygame.K_F3:
                        global debug_mode
                        debug_mode = not debug_mode
                        self.add_notification(f"Debug mode: {'ON' if debug_mode else 'OFF'}", 2000, "purple")

                if self.state == GameState.MENU:
                    # Handle menu button clicks
                    for button in self.menu_buttons:
                        if button.is_pressed(event):
                            if button.text == "Start Game":
                                self.state = GameState.PLAYING
                                self.setup_game()
                                sound_manager.play_game_theme()
                                self.add_notification("Game Started! Good luck!", 3000, "green")
                            elif button.text == "High Scores":
                                # Use menu's high scores functionality
                                menu.display_high_scores()
                            elif button.text == "Settings":
                                # Use menu's settings functionality
                                menu.display_settings()
                            elif button.text == "Exit":
                                pygame.event.clear()  # Clear any pending events
                                pygame.quit()
                                sys.exit()

                elif self.state == GameState.PLAYING:
                    # Handle game input
                    if event.type == pygame.KEYDOWN:
                        if self.move_cooldown <= 0:
                            new_pos = list(self.character_pos)
                            
                            if event.key == pygame.K_UP or event.key == pygame.K_w:
                                new_pos[1] -= 1
                            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                                new_pos[1] += 1
                            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                                new_pos[0] -= 1
                            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                                new_pos[0] += 1
                            
                            # Check if move is valid - ensure we can't move through rocks (value 1)
                            if (0 <= new_pos[0] < self.cols and 
                                0 <= new_pos[1] < self.rows and 
                                self.grid[new_pos[1]][new_pos[0]] == 0):  # Only allow movement on empty spaces (0)
                                
                                self.character_pos = new_pos
                                self.steps += 1
                                self.move_cooldown = self.default_move_cooldown
                                
                                # Add movement particles
                                self.particle_system.add_movement_particles(
                                    self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING,
                                    self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING,
                                    10
                                )
                                
                                # Check for powerups
                                self.check_powerups()
                                
                                # Check if reached end
                                if self.character_pos[0] == self.end_pos[0] and self.character_pos[1] == self.end_pos[1]:
                                    self.level_complete()

                elif self.state == GameState.PAUSED:
                    # Handle pause menu button clicks
                    for button in self.pause_buttons:
                        if button.is_pressed(event):
                            if button.text == "Resume":
                                self.state = GameState.PLAYING
                                sound_manager.play_sound("unpause")
                            elif button.text == "Restart":
                                self.setup_game()
                                self.state = GameState.PLAYING
                                sound_manager.play_game_theme()
                                self.add_notification("Game Restarted!", 3000, "blue")
                            elif button.text == "Main Menu":
                                self.state = GameState.MENU
                                sound_manager.play_menu_theme()
                            elif button.text == "Exit":
                                pygame.event.clear()  # Clear any pending events
                                pygame.quit()
                                sys.exit()
            
            # Update game state
            if self.state == GameState.MENU:
                self.update_menu()
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.update_game()
                self.draw_game()
            elif self.state == GameState.PAUSED:
                self.draw_pause_menu()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            
            # Draw notifications on top of everything
            self.draw_notifications()
            
            # Draw debug info if enabled
            if debug_mode:
                self.draw_debug_info()
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
    
    def setup_game(self):
        # Reset game variables
        self.level = 1
        self.rows = 5
        self.cols = 5
        self.score = 0
        self.steps = 0
        self.coins_collected = 0
        self.level_time = LEVEL_TIME
        self.start_time = pygame.time.get_ticks()
        
        # Load character and bonus images
        character_skins = load_character_skins()
        self.character_image = random.choice(character_skins) if character_skins else None
        self.bonus_image = load_bonus_image()
        
        # Generate map
        self.grid, self.powerups, self.start_pos, self.end_pos, self.map_background = generate_map(self.rows, self.cols, self.level)
        self.character_pos = list(self.start_pos)
        
        # Reset camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Reset movement
        self.move_cooldown = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        
        # Reset weather
        self.current_weather = random.choice(list(WEATHER.keys()))
        self.achievements_unlocked = []
        
        # Play start sound
        sound_manager.play_sound("level_start")
    
    def check_powerups(self):
        for powerup in self.powerups[:]:
            x, y, type = powerup
            if self.character_pos[0] == x and self.character_pos[1] == y:
                if type == POWERUP_SPEED:
                    self.speed_boost = True
                    self.speed_boost_timer = pygame.time.get_ticks() + SPEED_BOOST_DURATION
                    self.add_notification("Speed Boost activated!", 2000, "blue")
                    
                    # Add speed boost particles
                    self.particle_system.add_effect_particles(
                        self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING,
                        self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING,
                        30, (0, 150, 255)
                    )
                    
                elif type == POWERUP_EXTRA_TIME:
                    self.level_time += 5
                    self.add_notification("+5 seconds added!", 2000, "green")
                    
                    # Add time boost particles
                    self.particle_system.add_effect_particles(
                        self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING,
                        self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING,
                        30, (0, 255, 100)
                    )
                    
                elif type == BONUS:
                    self.coins_collected += 1
                    self.score += 500
                    self.add_notification("+500 points!", 2000, "purple")
                    
                    # Add coin particles
                    self.particle_system.add_effect_particles(
                        self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING,
                        self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING,
                        30, (255, 215, 0)
                    )
                    
                self.powerups.remove(powerup)
                sound_manager.play_powerup()
    
    def level_complete(self):
        # Update level
        self.level += 1
        
        # Calculate remaining time bonus
        remaining_time = max(0, self.level_time - (pygame.time.get_ticks() - self.start_time) // 1000)
        time_bonus = remaining_time * 100
        self.score += time_bonus
        
        # Add level completion bonus
        level_bonus = self.level * 1000
        self.score += level_bonus
        
        # Update level time
        self.level_time = LEVEL_TIME + (self.level // 2)
        self.start_time = pygame.time.get_ticks()
        
        # Update grid size
        if self.level % 2 == 0:
            self.cols += 1
        else:
            self.rows += 1
        
        # Generate new map
        self.grid, self.powerups, self.start_pos, self.end_pos, self.map_background = generate_map(self.rows, self.cols, self.level)
        self.character_pos = list(self.start_pos)
        
        # Reset camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Reset movement
        self.move_cooldown = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        
        # Update weather
        self.current_weather = random.choice(list(WEATHER.keys()))
        
        # Show level completion notification
        self.add_notification(f"Level {self.level-1} Complete! +{time_bonus + level_bonus} points", 3000, "green")
        
        # Play victory sound
        sound_manager.play_sound("level_complete")
        
        # Add level completion particles
        for _ in range(50):
            self.particle_system.add_effect_particles(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                20, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
    
    def update_menu(self):
        # Update menu buttons
        for button in self.menu_buttons:
            button.is_hovered()
        
        # Update modern background
        self.modern_background.update()
        
        # Update particles
        for particle in self.particles:
            particle["y"] += particle["speed"]
            if particle["y"] > SCREEN_HEIGHT:
                particle["y"] = 0
                particle["x"] = random.randint(0, SCREEN_WIDTH)
        
        # Update notifications
        self.notifications = [n for n in self.notifications if n.update()]
    
    def update_game(self):
        # Update movement cooldown
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        
        # Update speed boost
        if self.speed_boost and pygame.time.get_ticks() > self.speed_boost_timer:
            self.speed_boost = False
            self.add_notification("Speed Boost ended", 2000, "blue")
        
        # Apply weather effects
        self.move_cooldown = apply_weather_effects(self.current_weather, self.move_cooldown)
        
        # Check for new achievements
        time_left = max(0, self.level_time - (pygame.time.get_ticks() - self.start_time) // 1000)
        new_achievements = check_achievements(self.level, time_left, self.steps, self.coins_collected)
        for achievement in new_achievements:
            if achievement not in self.achievements_unlocked:
                self.achievements_unlocked.append(achievement)
                self.add_notification(f"Achievement Unlocked: {achievement}", 3000, "purple")
        
        # Check for game over
        if time_left <= 0:
            self.state = GameState.GAME_OVER
            sound_manager.play_sound("game_over")
            
            # Save score
            score_manager.save_score(self.score, "Normal", self.level)
        
        # Update particle system
        self.particle_system.update()
        
        # Update notifications
        self.notifications = [n for n in self.notifications if n.update()]
        
        # Update enhanced parallax background
        self.enhanced_parallax.update(self.camera_x)

    def draw_game(self):
        # Update camera
        target_camera_x = self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_WIDTH // 2
        target_camera_y = self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_HEIGHT // 2
        self.camera_x += (target_camera_x - self.camera_x) * 0.1
        self.camera_y += (target_camera_y - self.camera_y) * 0.1
        
        # Draw enhanced parallax background
        self.enhanced_parallax.draw(self.screen)

        # Draw game elements
        draw_map(
            self.screen, self.grid, self.powerups, self.camera_x, self.camera_y,
            self.start_pos, self.end_pos, self.character_pos,
            self.character_image, self.bonus_image, self.map_background
        )
        
        # Draw particle effects
        self.particle_system.draw(self.screen)
        
        # Draw UI panel
        ui_panel = Panel(10, 10, 250, 180, (0, 0, 0, 150), border_radius=10, border_color=(255, 255, 255, 50), border_width=2)
        ui_panel.draw(self.screen)
        
        # Draw game info
        level_text = self.fonts['info'].render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (30, 20))
        
        score_text = self.fonts['info'].render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (30, 60))
        
        time_left = max(0, self.level_time - (pygame.time.get_ticks() - self.start_time) // 1000)
        timer_text = self.fonts['info'].render(f"Time: {time_left}", True, WHITE)
        self.screen.blit(timer_text, (30, 100))
        
        weather_text = self.fonts['info'].render(f"Weather: {self.current_weather.capitalize()}", True, WHITE)
        self.screen.blit(weather_text, (30, 140))
        
        # Draw time progress bar
        time_progress = ProgressBar(
            270, 20, 200, 30, 
            self.level_time, 
            time_left, 
            "green" if time_left > self.level_time // 2 else "red",
            "Time"
        )
        time_progress.draw(self.screen)
        
        # Draw speed boost indicator if active
        if self.speed_boost:
            boost_time_left = (self.speed_boost_timer - pygame.time.get_ticks()) // 1000
            boost_text = self.fonts['info'].render(f"Speed Boost: {boost_time_left}s", True, (0, 150, 255))
            self.screen.blit(boost_text, (270, 60))
            
            # Draw boost progress bar
            boost_progress = ProgressBar(
                270, 100, 200, 30, 
                SPEED_BOOST_DURATION // 1000, 
                boost_time_left, 
                "blue"
            )
            boost_progress.draw(self.screen)
        
        # Draw achievements if any
        if self.achievements_unlocked:
            achievements_text = self.fonts['small'].render(f"Achievements: {', '.join(self.achievements_unlocked)}", True, (255, 215, 0))
            self.screen.blit(achievements_text, (270, 140))
    
    def draw_menu(self):
        # Draw modern background instead of menu_background
        self.modern_background.update()
        self.modern_background.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                particle["size"]
            )
        
        # Draw title
        title_text = self.fonts['title'].render("Random Blocks Game", True, WHITE)
        title_shadow = self.fonts['title'].render("Random Blocks Game", True, BLACK)
        
        # Add shadow for depth
        self.screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + 4, 100 + 4))
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw buttons
        for button in self.menu_buttons:
            button.draw(self.screen)
        
        # Draw version info
        version_text = self.fonts['small'].render("Version 2.0", True, WHITE)
        self.screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 20, SCREEN_HEIGHT - version_text.get_height() - 20))
    
    def draw_pause_menu(self):
        # First draw the game in the background
        self.draw_game()
        
        # Draw overlay
        overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 150))
        self.screen.blit(overlay_surface, (0, 0))
        
        # Draw pause title
        pause_text = self.fonts['heading'].render("Game Paused", True, WHITE)
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 150))
        
        # Draw buttons
        for button in self.pause_buttons:
            button.draw(self.screen)
    
    def draw_game_over(self):
        # Draw background with alpha
        overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 200))
        self.screen.blit(overlay_surface, (0, 0))
        
        # Draw game over title
        game_over_text = self.fonts['title'].render("Game Over", True, (255, 50, 50))
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
        
        # Draw score
        score_text = self.fonts['heading'].render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        
        # Draw level reached
        level_text = self.fonts['info'].render(f"Level Reached: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 320))
        
        # Draw coins collected
        coins_text = self.fonts['info'].render(f"Coins Collected: {self.coins_collected}", True, WHITE)
        self.screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 360))
        
        # Draw steps taken
        steps_text = self.fonts['info'].render(f"Steps Taken: {self.steps}", True, WHITE)
        self.screen.blit(steps_text, (SCREEN_WIDTH // 2 - steps_text.get_width() // 2, 400))
        
        # Draw achievements
        if self.achievements_unlocked:
            achievements_text = self.fonts['info'].render(f"Achievements: {', '.join(self.achievements_unlocked)}", True, (255, 215, 0))
            self.screen.blit(achievements_text, (SCREEN_WIDTH // 2 - achievements_text.get_width() // 2, 440))
        
        # Draw restart button
        restart_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150,
            500,
            300, 70,
            "Play Again",
            None,
            "green"
        )
        restart_btn.draw(self.screen)
        
        # Draw menu button
        menu_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150,
            590,
            300, 70,
            "Main Menu",
            None,
            "blue"
        )
        menu_btn.draw(self.screen)
        
        # Handle button clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if restart_btn.is_pressed(event):
                self.setup_game()
                self.state = GameState.PLAYING
                sound_manager.play_game_theme()
            
            if menu_btn.is_pressed(event):
                self.state = GameState.MENU
                sound_manager.play_menu_theme()
    
    def draw_notifications(self):
        # Draw all active notifications
        y_offset = 50
        for notification in self.notifications:
            notification.draw(self.screen, SCREEN_WIDTH // 2, y_offset)
            y_offset += 60
    
    def draw_debug_info(self):
        # Calculate average FPS
        avg_fps = sum(self.fps_values) / len(self.fps_values) if self.fps_values else 0
        
        # Create debug panel
        debug_panel = Panel(SCREEN_WIDTH - 210, 10, 200, 120, (0, 0, 0, 180), border_radius=5)
        debug_panel.draw(self.screen)
        
        # Draw FPS
        fps_text = self.fonts['small'].render(f"FPS: {avg_fps:.1f}", True, WHITE)
        self.screen.blit(fps_text, (SCREEN_WIDTH - 200, 20))
        
        # Draw position
        pos_text = self.fonts['small'].render(f"Pos: {self.character_pos}", True, WHITE)
        self.screen.blit(pos_text, (SCREEN_WIDTH - 200, 50))
        
        # Draw grid size
        grid_text = self.fonts['small'].render(f"Grid: {self.rows}x{self.cols}", True, WHITE)
        self.screen.blit(grid_text, (SCREEN_WIDTH - 200, 80))
        
        # Draw camera position
        camera_text = self.fonts['small'].render(f"Camera: {int(self.camera_x)},{int(self.camera_y)}", True, WHITE)
        self.screen.blit(camera_text, (SCREEN_WIDTH - 200, 110))

# Create particle system class
class ParticleSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles = []
    
    def add_movement_particles(self, x, y, count=5):
        for _ in range(count):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'size': random.uniform(1, 3),
                'color': (255, 255, 255, random.randint(100, 200)),
                'life': random.randint(10, 30),
                'max_life': 30,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1)
            }
            self.particles.append(particle)
    
    def add_effect_particles(self, x, y, count=20, color=(255, 255, 255)):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            particle = {
                'x': x,
                'y': y,
                'size': random.uniform(2, 5),
                'color': (*color, random.randint(150, 255)),
                'life': random.randint(20, 60),
                'max_life': 60,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed
            }
            self.particles.append(particle)
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'][:3], min(particle['color'][3], alpha))
            
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface,
                color,
                (particle['size'], particle['size']),
                particle['size']
            )
            surface.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))

# Main function
def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

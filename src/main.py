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
import menu

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
                self.pulse_duration = 0
                self.pulse_time = 0

    def draw(self, surface):
        self.update()
        
        # Draw glow effect when hovered
        if self.glow_radius > 0:
            glow_surf = pygame.Surface((self.rect.width + self.max_glow*2, self.rect.height + self.max_glow*2), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surf, 
                self.color_scheme["glow"], 
                (self.max_glow, self.max_glow, self.rect.width, self.rect.height),
                border_radius=15
            )
            # Use try/except for gaussian_blur as it might not be available in all pygame versions
            try:
                glow_surf = pygame.transform.gaussian_blur(glow_surf, self.glow_radius)
            except AttributeError:
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
        
        # Calculate button color with pulse effect
        button_color = self.color_scheme[self.state]
        if self.pulse_duration > 0:
            pulse_factor = math.sin(math.pi * self.pulse_time / self.pulse_duration)
            button_color = tuple(
                min(255, int(c + (255 - c) * pulse_factor * 0.3))
                for c in button_color
            )
        
        # Draw button
        pygame.draw.rect(
            surface, 
            button_color, 
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
        
        # Draw icon if provided
        if self.icon:
            icon_size = min(self.rect.height - 20, 32)
            icon_rect = pygame.Rect(0, 0, icon_size, icon_size)
            icon_rect.centery = self.rect.centery
            icon_rect.x = self.rect.x + 15
            surface.blit(pygame.transform.scale(self.icon, (icon_size, icon_size)), icon_rect)
            text_x_offset = icon_size + 10
        else:
            text_x_offset = 0
        
        # Draw text with slight shadow for depth - ensure text is on top of button
        text_surface = self.fonts['button'].render(self.text, True, (0, 0, 0, 128))
        text_rect = text_surface.get_rect(center=(self.rect.center[0] + text_x_offset//2 + 2, self.rect.center[1] + 2))
        surface.blit(text_surface, text_rect)
        
        text_surface = self.fonts['button'].render(self.text, True, self.color_scheme["text"])
        text_rect = text_surface.get_rect(center=(self.rect.center[0] + text_x_offset//2, self.rect.center[1]))
        surface.blit(text_surface, text_rect)

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        
        # Update state and animation targets based on hover state
        if hovered and self.state == "normal":
            self.state = "hover"
            self.target_scale = self.hover_scale
            self.target_glow = self.max_glow
            # Start pulse effect
            self.pulse_duration = self.pulse_max
            self.pulse_time = 0
        elif not hovered and self.state == "hover":
            self.state = "normal"
            self.target_scale = 1.0
            self.target_glow = 0
            
        return hovered
    
    def is_pressed(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered():
            self.state = "press"
            self.target_scale = self.press_scale
            return True
        elif event.type == pygame.MOUSEBUTTONUP and self.state == "press":
            self.state = "hover" if self.is_hovered() else "normal"
            self.target_scale = self.hover_scale if self.is_hovered() else 1.0
            return self.is_hovered()
        return False

# UI Panel class for modern interface elements
class UIPanel:
    def __init__(self, x, y, width, height, color=(30, 30, 30, 200), border_radius=15, border_color=None, border_width=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.border_radius = border_radius
        self.border_color = border_color
        self.border_width = border_width
        self.elements = []
        
    def draw(self, surface):
        # Create panel surface with alpha
        panel_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, self.color, (0, 0, self.rect.width, self.rect.height), 
                         border_radius=self.border_radius)
        
        # Draw border if specified
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(panel_surf, self.border_color, (0, 0, self.rect.width, self.rect.height), 
                             width=self.border_width, border_radius=self.border_radius)
        
        # Draw panel to surface
        surface.blit(panel_surf, self.rect.topleft)
        
        # Draw all elements
        for element in self.elements:
            element.draw(panel_surf)

# Progress bar for modern UI
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
                "text": (255, 255, 255),
                "border": (26, 82, 118)
            },
            "green": {
                "bg": (39, 174, 96, 100),
                "fill": (46, 204, 113),
                "text": (255, 255, 255),
                "border": (20, 90, 50)
            },
            "red": {
                "bg": (192, 57, 43, 100),
                "fill": (231, 76, 60),
                "text": (255, 255, 255),
                "border": (100, 30, 22)
            },
            "orange": {
                "bg": (211, 84, 0, 100),
                "fill": (230, 126, 34),
                "text": (255, 255, 255),
                "border": (126, 49, 0)
            },
            "purple": {
                "bg": (142, 68, 173, 100),
                "fill": (155, 89, 182),
                "text": (255, 255, 255),
                "border": (74, 35, 90)
            }
        }
        
        self.color_scheme = self.schemes.get(color_scheme, self.schemes["blue"])
        
        # Animation properties
        self.target_value = current_value
        self.animation_speed = 0.1
        
    def update(self, new_value):
        self.target_value = min(new_value, self.max_value)
        
    def draw(self, surface):
        # Animate current value towards target
        if self.current_value != self.target_value:
            self.current_value += (self.target_value - self.current_value) * self.animation_speed
            if abs(self.current_value - self.target_value) < 0.1:
                self.current_value = self.target_value
        
        # Calculate fill width
        fill_width = int((self.current_value / self.max_value) * self.rect.width)
        
        # Draw background
        pygame.draw.rect(surface, self.color_scheme["bg"], self.rect, border_radius=self.rect.height//2)
        
        # Draw fill
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, self.color_scheme["fill"], fill_rect, border_radius=self.rect.height//2)
            
            # Add gradient effect to fill
            gradient = pygame.Surface((fill_width, self.rect.height), pygame.SRCALPHA)
            for i in range(self.rect.height // 2):
                alpha = 100 - (i * 4)
                if alpha > 0:
                    pygame.draw.rect(
                        gradient, 
                        (255, 255, 255, alpha), 
                        (0, i, fill_width, 2),
                        border_radius=self.rect.height//2
                    )
            surface.blit(gradient, self.rect.topleft)
        
        # Draw border
        pygame.draw.rect(surface, self.color_scheme["border"], self.rect, width=2, border_radius=self.rect.height//2)
        
        # Draw label if provided
        if self.label:
            label_text = self.fonts['small'].render(f"{self.label}: {int(self.current_value)}/{self.max_value}", True, self.color_scheme["text"])
            label_rect = label_text.get_rect(center=self.rect.center)
            surface.blit(label_text, label_rect)

# Icon with text for HUD elements
class IconText:
    def __init__(self, x, y, icon, text, font, color=WHITE, icon_size=32, spacing=10):
        self.x = x
        self.y = y
        self.icon = icon
        self.text = text
        self.font = font
        self.color = color
        self.icon_size = icon_size
        self.spacing = spacing
        
    def update(self, new_text):
        self.text = new_text
        
    def draw(self, surface):
        # Draw icon
        icon_rect = pygame.Rect(self.x, self.y, self.icon_size, self.icon_size)
        if isinstance(self.icon, pygame.Surface):
            surface.blit(pygame.transform.scale(self.icon, (self.icon_size, self.icon_size)), icon_rect)
        else:
            # Draw a fallback icon if image not provided
            pygame.draw.rect(surface, self.color, icon_rect)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(midleft=(self.x + self.icon_size + self.spacing, self.y + self.icon_size//2))
        surface.blit(text_surface, text_rect)

# Notification system for in-game alerts
class Notification:
    def __init__(self, text, duration=3000, color_scheme="blue"):
        self.text = text
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.fonts = load_custom_fonts()
        
        # Color schemes
        self.schemes = {
            "blue": (41, 128, 185),
            "green": (39, 174, 96),
            "red": (192, 57, 43),
            "orange": (230, 126, 34),
            "purple": (142, 68, 173)
        }
        
        self.color = self.schemes.get(color_scheme, self.schemes["blue"])
        
        # Animation properties
        self.alpha = 0
        self.target_alpha = 255
        self.animation_speed = 0.1
        
    def update(self):
        # Animate alpha
        if pygame.time.get_ticks() - self.start_time < 500:
            # Fade in
            self.alpha += (self.target_alpha - self.alpha) * self.animation_speed
        elif pygame.time.get_ticks() - self.start_time > self.duration - 500:
            # Fade out
            self.alpha -= self.alpha * self.animation_speed
        
        # Check if notification is expired
        return pygame.time.get_ticks() - self.start_time < self.duration
        
    def draw(self, surface, x, y):
        # Create notification surface with alpha
        text_surface = self.fonts['info'].render(self.text, True, WHITE)
        padding = 20
        width = text_surface.get_width() + padding * 2
        height = text_surface.get_height() + padding
        
        notif_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        notif_surf.fill((0, 0, 0, 0))
        
        # Draw background with alpha
        bg_color = (*self.color, int(self.alpha * 0.8))
        pygame.draw.rect(notif_surf, bg_color, (0, 0, width, height), border_radius=10)
        
        # Draw text with alpha
        text_surface.set_alpha(int(self.alpha))
        notif_surf.blit(text_surface, (padding, padding//2))
        
        # Draw to surface
        surface.blit(notif_surf, (x - width//2, y))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Random Blocks - Epic Edition")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.character_skins = load_character_skins()
        if not self.character_skins:
            fallback_char = pygame.Surface((ACTUAL_BLOCK_SIZE, ACTUAL_BLOCK_SIZE))
            fallback_char.fill(BLUE)
            self.character_skins = [fallback_char]
        self.current_character = None
        
        # Load fonts
        self.fonts = load_custom_fonts()
        
        # Initialize modern background
        self.modern_background = ModernBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.enhanced_parallax = EnhancedParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Use menu module for particles
        self.particles = menu.particles
        self.overlay = menu.overlay
        
        # Create icons for HUD
        self.icons = self.load_icons()
        
        # Notification system
        self.notifications = []
        
        # Create HUD panels
        self.create_hud_panels()
        
        self.create_buttons()
        self.setup_game()
        sound_manager.play_menu_theme()
        
        # Animation variables
        self.title_angle = 0

    def load_icons(self):
        icons = {}
        
        # Create fallback icons if images can't be loaded
        icons['level'] = self.create_icon_surface((41, 128, 185), "L")
        icons['score'] = self.create_icon_surface((39, 174, 96), "S")
        icons['time'] = self.create_icon_surface((192, 57, 43), "T")
        icons['coins'] = self.create_icon_surface((230, 126, 34), "C")
        icons['steps'] = self.create_icon_surface((142, 68, 173), "F")
        icons['speed'] = self.create_icon_surface((241, 196, 15), "B")
        
        return icons
    
    def create_icon_surface(self, color, letter=None):
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(icon, color, (16, 16), 16)
        
        if letter:
            font = pygame.font.SysFont('arial', 20, bold=True)
            text = font.render(letter, True, WHITE)
            text_rect = text.get_rect(center=(16, 16))
            icon.blit(text, text_rect)
            
        return icon

    def create_hud_panels(self):
        # Main HUD panel
        self.hud_panel = UIPanel(
            10, 10, 300, 180, 
            color=(20, 20, 20, 180), 
            border_radius=15,
            border_color=(41, 128, 185),
            border_width=2
        )
        
        # Mini-map panel (placeholder)
        self.minimap_panel = UIPanel(
            SCREEN_WIDTH - 210, 10, 200, 200,
            color=(20, 20, 20, 180),
            border_radius=15,
            border_color=(192, 57, 43),
            border_width=2
        )
        
        # Status effects panel
        self.status_panel = UIPanel(
            10, SCREEN_HEIGHT - 70, 300, 60,
            color=(20, 20, 20, 180),
            border_radius=15,
            border_color=(39, 174, 96),
            border_width=2
        )
        
        # Create time progress bar
        self.time_bar = ProgressBar(
            20, 140, 280, 20, 
            LEVEL_TIME, LEVEL_TIME,
            color_scheme="red",
            label="Time"
        )

    def setup_game(self):
        # Basic game variables
        self.level = 1
        self.rows = 5
        self.cols = 5
        self.score = 0
        self.steps = 0
        self.coins_collected = 0
        self.start_time = pygame.time.get_ticks()
        self.game_start_time = time.time()
        self.level_time = LEVEL_TIME
        
        # Update time bar
        self.time_bar.max_value = self.level_time
        self.time_bar.update(self.level_time)

        # Choose character only if starting a new game
        if self.current_character is None:
            self.current_character = random.randint(0, len(self.character_skins) - 1)
        self.character_image = self.character_skins[self.current_character]

        # Game elements
        self.bonus_image = load_bonus_image()
        self.grid, self.powerups, self.start_pos, self.end_pos, self.map_background = generate_map(self.rows, self.cols, self.level)
        self.character_pos = list(self.start_pos)

        # Camera and movement
        self.camera_x = 0
        self.camera_y = 0
        self.move_cooldown = 0
        self.speed_boost = False
        self.speed_boost_timer = 0

        # Game state
        self.current_weather = random.choice(list(WEATHER.keys()))
        self.achievements_unlocked = []
        
        # Add welcome notification
        self.add_notification(f"Welcome to Level {self.level}!", 3000, "blue")

    def create_buttons(self):
        # Create animated buttons with different color schemes and icons
        self.new_game_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150, 
            SCREEN_HEIGHT // 2 - 60, 
            300, 70, 
            "Start Game", 
            None,
            "green",
            self.icons.get('level')
        )
        
        self.high_scores_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150, 
            SCREEN_HEIGHT // 2 + 30, 
            300, 70, 
            "High Scores",
            None,
            "blue",
            self.icons.get('score')
        )
        
        self.settings_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150, 
            SCREEN_HEIGHT // 2 + 120, 
            300, 70, 
            "Settings",
            None,
            "purple",
            self.icons.get('time')
        )
        
        self.exit_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150, 
            SCREEN_HEIGHT // 2 + 210, 
            300, 70, 
            "Exit", 
            None,
            "red"
        )
        
        self.menu_buttons = [self.new_game_btn, self.high_scores_btn, self.settings_btn, self.exit_btn]
        
        # Pause menu buttons
        self.resume_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 - 90,
            300, 70,
            "Resume",
            None,
            "green"
        )
        
        self.restart_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2,
            300, 70,
            "Restart",
            None,
            "blue"
        )
        
        self.menu_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 + 90,
            300, 70,
            "Main Menu",
            None,
            "purple"
        )
        
        self.pause_buttons = [self.resume_btn, self.restart_btn, self.menu_btn, self.exit_btn]

    def add_notification(self, text, duration=3000, color_scheme="blue"):
        self.notifications.append(Notification(text, duration, color_scheme))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.event.clear()  # Clear any pending events
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_ESCAPE and self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING

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
                                
                                # Set move cooldown
                                if self.speed_boost:
                                    self.move_cooldown = SPEED_BOOST_COOLDOWN
                                else:
                                    self.move_cooldown = DEFAULT_MOVE_COOLDOWN
                                
                                # Check for powerups
                                for i, (x, y, powerup_type) in enumerate(self.powerups):
                                    if self.character_pos[0] == x and self.character_pos[1] == y:
                                        if powerup_type == POWERUP_SPEED:
                                            self.speed_boost = True
                                            self.speed_boost_timer = pygame.time.get_ticks() + SPEED_BOOST_DURATION
                                            self.add_notification("Speed Boost Activated!", 2000, "orange")
                                        elif powerup_type == POWERUP_EXTRA_TIME:
                                            self.level_time += 5  # Add 5 seconds
                                            self.add_notification("+5 Seconds Added!", 2000, "red")
                                        elif powerup_type == BONUS:
                                            self.coins_collected += 1
                                            self.score += 500
                                            self.add_notification("+500 Points!", 2000, "green")
                                        
                                        # Remove collected powerup
                                        self.powerups.pop(i)
                                        break
                                
                                # Check if reached end
                                if tuple(self.character_pos) == self.end_pos:
                                    self.score += 1000 * self.level
                                    self.add_notification(f"Level {self.level} Complete! +{1000 * self.level} Points", 3000, "blue")
                                    self.next_level()
                
                elif self.state == GameState.PAUSED:
                    # Handle pause menu button clicks
                    for button in self.pause_buttons:
                        if button.is_pressed(event):
                            if button.text == "Resume":
                                self.state = GameState.PLAYING
                            elif button.text == "Restart":
                                self.setup_game()
                                self.state = GameState.PLAYING
                            elif button.text == "Main Menu":
                                self.state = GameState.MENU
                            elif button.text == "Exit":
                                pygame.event.clear()  # Clear any pending events
                                pygame.quit()
                                sys.exit()

            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.update_game()
                self.draw_game()
            elif self.state == GameState.PAUSED:
                self.draw_pause_menu()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def draw_menu(self):
        # Draw modern background instead of menu_background
        self.modern_background.update()
        self.modern_background.draw(self.screen)
        
        # Update and draw particles
        for particle in self.particles:
            particle.update()
            particle.draw(self.screen)
        
        # Draw semi-transparent overlay for better text contrast
        self.screen.blit(self.overlay, (0, 0))
        
        # Draw animated title
        self.title_angle = (self.title_angle + 0.5) % 360
        title_scale = 1.0 + math.sin(math.radians(self.title_angle)) * 0.05
        
        title_text = self.fonts['title'].render("Random Blocks", True, WHITE)
        title_shadow = self.fonts['title'].render("Random Blocks", True, (0, 0, 0))
        
        # Create a pulsing glow effect
        glow_surf = pygame.Surface((title_text.get_width() + 40, title_text.get_height() + 40), pygame.SRCALPHA)
        glow_color = (52, 152, 219, 100 + int(math.sin(math.radians(self.title_angle)) * 50))
        glow_text = self.fonts['title'].render("Random Blocks", True, glow_color)
        glow_surf.blit(glow_text, (20, 20))
        # Use try/except for gaussian_blur as it might not be available in all pygame versions
        try:
            glow_surf = pygame.transform.gaussian_blur(glow_surf, 10)
        except AttributeError:
            # Fallback if gaussian_blur is not available
            pass
        
        # Scale and position title
        scaled_glow = pygame.transform.scale(
            glow_surf, 
            (int(glow_surf.get_width() * title_scale), int(glow_surf.get_height() * title_scale))
        )
        glow_rect = scaled_glow.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        scaled_shadow = pygame.transform.scale(
            title_shadow, 
            (int(title_shadow.get_width() * title_scale), int(title_shadow.get_height() * title_scale))
        )
        shadow_rect = scaled_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 5, 155))
        
        scaled_title = pygame.transform.scale(
            title_text, 
            (int(title_text.get_width() * title_scale), int(title_text.get_height() * title_scale))
        )
        title_rect = scaled_title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Draw title with effects
        self.screen.blit(scaled_glow, glow_rect)
        self.screen.blit(scaled_shadow, shadow_rect)
        self.screen.blit(scaled_title, title_rect)
        
        # Draw subtitle
        subtitle_text = self.fonts['button'].render("Epic Edition", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Update and draw buttons
        for button in self.menu_buttons:
            button.is_hovered()  # Update hover state
            button.draw(self.screen)
        
        # Draw version info
        version_text = self.fonts['small'].render("v2.0.0", True, (150, 150, 150))
        self.screen.blit(version_text, (20, SCREEN_HEIGHT - 40))
        
        # Draw copyright
        copyright_text = self.fonts['small'].render("© 2025 Random Blocks Studio", True, (150, 150, 150))
        copyright_rect = copyright_text.get_rect(right=SCREEN_WIDTH - 20, bottom=SCREEN_HEIGHT - 20)
        self.screen.blit(copyright_text, copyright_rect)

    def draw_pause_menu(self):
        # First draw the game in the background
        self.draw_game()
        
        # Add a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause menu panel
        pause_panel = UIPanel(
            SCREEN_WIDTH // 2 - 200, 
            SCREEN_HEIGHT // 2 - 250, 
            400, 500,
            color=(20, 20, 20, 230),
            border_radius=20,
            border_color=(41, 128, 185),
            border_width=3
        )
        pause_panel.draw(self.screen)
        
        # Draw pause title
        pause_title = self.fonts['heading'].render("PAUSED", True, WHITE)
        pause_title_rect = pause_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180))
        self.screen.blit(pause_title, pause_title_rect)
        
        # Draw decorative line
        pygame.draw.line(
            self.screen, 
            (41, 128, 185), 
            (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 140),
            (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 - 140),
            3
        )
        
        # Draw buttons
        for button in self.pause_buttons:
            button.is_hovered()  # Update hover state
            button.draw(self.screen)

    def update_game(self):
        # Handle player movement
        keys = pygame.key.get_pressed()
        if self.move_cooldown <= 0:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                if self.character_pos[1] > 0 and self.grid[self.character_pos[1] - 1][self.character_pos[0]] == 0:
                    self.character_pos[1] -= 1
                    self.steps += 1
                    self.move_cooldown = SPEED_BOOST_COOLDOWN if self.speed_boost else DEFAULT_MOVE_COOLDOWN
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if self.character_pos[1] < self.rows - 1 and self.grid[self.character_pos[1] + 1][self.character_pos[0]] == 0:
                    self.character_pos[1] += 1
                    self.steps += 1
                    self.move_cooldown = SPEED_BOOST_COOLDOWN if self.speed_boost else DEFAULT_MOVE_COOLDOWN
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if self.character_pos[0] > 0 and self.grid[self.character_pos[1]][self.character_pos[0] - 1] == 0:
                    self.character_pos[0] -= 1
                    self.steps += 1
                    self.move_cooldown = SPEED_BOOST_COOLDOWN if self.speed_boost else DEFAULT_MOVE_COOLDOWN
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if self.character_pos[0] < self.cols - 1 and self.grid[self.character_pos[1]][self.character_pos[0] + 1] == 0:
                    self.character_pos[0] += 1
                    self.steps += 1
                    self.move_cooldown = SPEED_BOOST_COOLDOWN if self.speed_boost else DEFAULT_MOVE_COOLDOWN
        else:
            self.move_cooldown -= 1

        # Check for powerup collection
        for i, (x, y, powerup_type) in enumerate(self.powerups):
            if self.character_pos[0] == x and self.character_pos[1] == y:
                if powerup_type == POWERUP_SPEED:
                    self.speed_boost = True
                    self.speed_boost_timer = pygame.time.get_ticks() + SPEED_BOOST_DURATION
                    self.add_notification("Speed Boost Activated!", 2000, "orange")
                elif powerup_type == POWERUP_EXTRA_TIME:
                    self.level_time += 5  # Add 5 seconds
                    self.add_notification("+5 Seconds Added!", 2000, "red")
                elif powerup_type == BONUS:
                    self.coins_collected += 1
                    self.score += 500
                    self.add_notification("+500 Points!", 2000, "green")
                self.powerups.pop(i)
                break

        # Update speed boost
        if self.speed_boost and pygame.time.get_ticks() > self.speed_boost_timer:
            self.speed_boost = False
            self.add_notification("Speed Boost Expired", 2000, "orange")

        # Check win condition
        if self.character_pos[0] == self.end_pos[0] and self.character_pos[1] == self.end_pos[1]:
            self.next_level()

        # Update time bar
        time_left = self.get_time_left()
        self.time_bar.update(time_left)
        
        # Check time
        if time_left <= 0:
            self.state = GameState.GAME_OVER
            self.show_score_popup()
            
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
        
        # Draw modern HUD
        self.draw_modern_hud()
        
        # Draw notifications
        for i, notification in enumerate(self.notifications):
            notification.draw(self.screen, SCREEN_WIDTH // 2, 100 + i * 60)

    def draw_modern_hud(self):
        # Draw main HUD panel
        self.hud_panel.draw(self.screen)
        
        # Draw HUD elements
        level_icon = IconText(30, 20, self.icons['level'], f"Level: {self.level}", self.fonts['info'])
        level_icon.draw(self.screen)
        
        score_icon = IconText(30, 60, self.icons['score'], f"Score: {self.score}", self.fonts['info'])
        score_icon.draw(self.screen)
        
        coins_icon = IconText(30, 100, self.icons['coins'], f"Coins: {self.coins_collected}", self.fonts['info'])
        coins_icon.draw(self.screen)
        
        # Draw time bar
        self.time_bar.draw(self.screen)
        
        # Draw minimap panel
        self.minimap_panel.draw(self.screen)
        
        # Draw minimap title
        minimap_title = self.fonts['small'].render("MINIMAP", True, WHITE)
        minimap_title_rect = minimap_title.get_rect(center=(SCREEN_WIDTH - 110, 25))
        self.screen.blit(minimap_title, minimap_title_rect)
        
        # Draw simple minimap representation
        minimap_scale = min(180 / self.cols, 160 / self.rows)
        minimap_width = self.cols * minimap_scale
        minimap_height = self.rows * minimap_scale
        minimap_x = SCREEN_WIDTH - 110 - minimap_width / 2
        minimap_y = 110 - minimap_height / 2
        
        # Draw grid cells
        for y in range(self.rows):
            for x in range(self.cols):
                cell_x = minimap_x + x * minimap_scale
                cell_y = minimap_y + y * minimap_scale
                cell_color = (60, 60, 60) if self.grid[y][x] != 0 else (20, 20, 20)
                
                # Highlight start and end positions
                if (x, y) == self.start_pos:
                    cell_color = (41, 128, 185)  # Blue for start
                elif (x, y) == self.end_pos:
                    cell_color = (39, 174, 96)  # Green for end
                
                pygame.draw.rect(
                    self.screen, 
                    cell_color, 
                    (cell_x, cell_y, minimap_scale, minimap_scale)
                )
        
        # Draw player position on minimap
        player_x = minimap_x + self.character_pos[0] * minimap_scale + minimap_scale / 2
        player_y = minimap_y + self.character_pos[1] * minimap_scale + minimap_scale / 2
        pygame.draw.circle(
            self.screen,
            (231, 76, 60),  # Red for player
            (player_x, player_y),
            minimap_scale / 2
        )
        
        # Draw status panel
        self.status_panel.draw(self.screen)
        
        # Draw status effects
        status_title = self.fonts['small'].render("STATUS EFFECTS", True, WHITE)
        status_title_rect = status_title.get_rect(midtop=(160, SCREEN_HEIGHT - 65))
        self.screen.blit(status_title, status_title_rect)
        
        # Draw speed boost status if active
        if self.speed_boost:
            boost_time = max(0, (self.speed_boost_timer - pygame.time.get_ticks()) // 1000)
            speed_icon = IconText(30, SCREEN_HEIGHT - 40, self.icons['speed'], f"Speed Boost: {boost_time}s", self.fonts['small'])
            speed_icon.draw(self.screen)
        else:
            no_effects = self.fonts['small'].render("No active effects", True, (150, 150, 150))
            no_effects_rect = no_effects.get_rect(center=(160, SCREEN_HEIGHT - 40))
            self.screen.blit(no_effects, no_effects_rect)
        
        # Draw weather indicator
        weather_text = self.fonts['small'].render(f"Weather: {self.current_weather.title()}", True, WHITE)
        weather_rect = weather_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(weather_text, weather_rect)
        
        # Draw steps counter
        steps_text = self.fonts['small'].render(f"Steps: {self.steps}", True, WHITE)
        steps_rect = steps_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 50))
        self.screen.blit(steps_text, steps_rect)
        
        # Draw controls hint
        controls_text = self.fonts['small'].render("ESC: Pause", True, (150, 150, 150))
        controls_rect = controls_text.get_rect(bottomleft=(320, SCREEN_HEIGHT - 20))
        self.screen.blit(controls_text, controls_rect)

    def get_time_left(self):
        return max(0, self.level_time - (pygame.time.get_ticks() - self.start_time) // 1000)

    def next_level(self):
        """Handle transition to next level"""
        self.level += 1

        # Reset time for new level
        self.level_time = LEVEL_TIME
        self.start_time = pygame.time.get_ticks()
        
        # Update time bar
        self.time_bar.max_value = self.level_time
        self.time_bar.update(self.level_time)

        # Increase maze size
        if self.level % 2 == 0:
            self.cols += 1
        else:
            self.rows += 1

        # Generate new level
        self.grid, self.powerups, self.start_pos, self.end_pos, self.map_background = generate_map(self.rows, self.cols, self.level)
        self.character_pos = list(self.start_pos)
        # Don't change character skin - keep the same one
        
        # Add level up notification
        self.add_notification(f"Level {self.level} Started!", 3000, "blue")

    def calculate_score(self):
        return (self.level * 2000) + (self.coins_collected * 500) - (self.steps * 2)

    def show_score_popup(self):
        # Calculate final score and statistics
        final_score = self.calculate_score()
        time_played = int(time.time() - self.game_start_time)
        score_manager.save_score(final_score, "Normal", time_played)
        best_scores = score_manager.get_best_scores()
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        # Create a panel for the game over screen
        panel_width = 700
        panel_height = 500
        panel = UIPanel(
            SCREEN_WIDTH // 2 - panel_width // 2,
            SCREEN_HEIGHT // 2 - panel_height // 2,
            panel_width, panel_height,
            color=(30, 30, 30, 230),
            border_radius=20,
            border_color=(192, 57, 43),
            border_width=3
        )
        
        # Add decorative header
        header = pygame.Surface((panel_width, 80), pygame.SRCALPHA)
        header.fill((192, 57, 43))
        
        # Draw game over title
        game_over_text = self.fonts['heading'].render("Game Over!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(panel_width // 2, 40))
        header.blit(game_over_text, game_over_rect)
        
        # Create buttons
        play_again_btn = AnimatedButton(
            SCREEN_WIDTH // 2 - 220, 
            SCREEN_HEIGHT // 2 + 180,
            200, 60,
            "Play Again",
            None,
            "green"
        )
        
        main_menu_btn = AnimatedButton(
            SCREEN_WIDTH // 2 + 20, 
            SCREEN_HEIGHT // 2 + 180,
            200, 60,
            "Main Menu",
            None,
            "blue"
        )
        
        waiting = True
        while waiting:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.event.clear()  # Clear any pending events
                    pygame.quit()
                    sys.exit()
                
                # Check if buttons are clicked
                if play_again_btn.is_pressed(event):
                    self.current_character = None  # Reset character only when starting completely new game
                    self.setup_game()
                    self.state = GameState.PLAYING
                    return True
                
                if main_menu_btn.is_pressed(event):
                    self.state = GameState.MENU
                    return True
            
            # Draw modern background
            self.modern_background.update()
            self.modern_background.draw(self.screen)
            
            # Update and draw particles
            for particle in self.particles:
                particle.update()
                particle.draw(self.screen)
            
            # Draw overlay
            self.screen.blit(overlay, (0, 0))
            
            # Draw panel
            panel.draw(self.screen)
            
            # Draw header
            self.screen.blit(header, (SCREEN_WIDTH // 2 - panel_width // 2, SCREEN_HEIGHT // 2 - panel_height // 2))
            
            # Draw score with decorative elements
            y_offset = SCREEN_HEIGHT // 2 - 120
            final_score_text = self.fonts['heading'].render(f"Final Score: {final_score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(final_score_text, final_score_rect)
            
            # Add decorative line
            pygame.draw.line(
                self.screen, 
                (192, 57, 43), 
                (SCREEN_WIDTH // 2 - 150, y_offset + 50), 
                (SCREEN_WIDTH // 2 + 150, y_offset + 50), 
                3
            )
            
            # Draw statistics
            y_offset += 80
            stats = [
                (f"Level Reached: {self.level}", WHITE),
                (f"Steps Taken: {self.steps}", WHITE),
                (f"Coins Collected: {self.coins_collected}", WHITE),
                (f"Time Played: {time_played // 60}m {time_played % 60}s", WHITE)
            ]
            
            for stat, color in stats:
                stat_text = self.fonts['info'].render(stat, True, color)
                stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(stat_text, stat_rect)
                y_offset += 40
            
            # Add decorative line
            pygame.draw.line(
                self.screen, 
                (192, 57, 43), 
                (SCREEN_WIDTH // 2 - 150, y_offset), 
                (SCREEN_WIDTH // 2 + 150, y_offset), 
                3
            )
            
            # Draw high scores
            y_offset += 30
            high_score_title = self.fonts['info'].render("High Scores", True, WHITE)
            high_score_rect = high_score_title.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(high_score_title, high_score_rect)
            
            y_offset += 30
            for period, score in list(best_scores.items())[:2]:  # Show only top 2 scores
                score_text = self.fonts['small'].render(f"{period.replace('_', ' ').title()}: {score}", True, WHITE)
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(score_text, score_rect)
                y_offset += 25
            
            # Update button hover states
            play_again_btn.is_hovered()
            main_menu_btn.is_hovered()
            
            # Draw buttons
            play_again_btn.draw(self.screen)
            main_menu_btn.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return True

if __name__ == "__main__":
    game = Game()
    game.run()

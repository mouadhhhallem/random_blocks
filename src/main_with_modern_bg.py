import pygame
import random
import math
import os
import sys
from settings import *
from game_logic import generate_map, draw_map, load_character_skins, load_bonus_image, check_achievements, apply_weather_effects
from score_manager import ScoreManager
from sound_manager import SoundManager
from modern_background import ModernBackground, EnhancedParallaxBackground
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
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.state == "press":
            was_pressed = self.rect.collidepoint(event.pos)
            self.state = "hover" if was_pressed else "normal"
            self.target_scale = self.hover_scale if was_pressed else 1.0
            return was_pressed
        return False
    
    def pulse(self, duration=30):
        self.pulse_time = 0
        self.pulse_duration = duration

def main():
    global debug_mode  # Use the global debug_mode variable
    
    # Game variables
    clock = pygame.time.Clock()
    current_state = GameState.MENU
    level = 1
    score = 0
    
    # Initialize modern background
    modern_background = ModernBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
    enhanced_parallax = EnhancedParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Load game assets
    try:
        character_skins = load_character_skins()
        character_skin = 0
        character_image = character_skins[character_skin]
    except Exception as e:
        print(f"Error loading character skins: {e}")
        # Create fallback character
        character_image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        character_image.fill(BLUE)
    
    try:
        bonus_image = load_bonus_image()
    except Exception as e:
        print(f"Error loading bonus image: {e}")
        # Create fallback bonus image
        bonus_image = pygame.Surface((BLOCK_SIZE // 2, BLOCK_SIZE // 2))
        bonus_image.fill(YELLOW)
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    debug_mode = not debug_mode
                    print(f"Debug mode: {'enabled' if debug_mode else 'disabled'}")
        
        # Update and render based on current state
        if current_state == GameState.MENU:
            # Show main menu
            menu_result = menu.show_main_menu(screen)
            if menu_result == "start":
                current_state = GameState.PLAYING
                # Start game logic here
                sound_manager.play_game_theme()
            elif menu_result == "quit":
                running = False
        
        elif current_state == GameState.PLAYING:
            # Game logic and rendering
            # This would be implemented based on your game's specific requirements
            
            # Update the modern background
            enhanced_parallax.update(0)  # Use camera position when available
            
            # Draw the modern background
            enhanced_parallax.draw(screen)
            
            # Draw game elements on top of the background
            # ...
            
            # Draw UI elements
            # ...
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

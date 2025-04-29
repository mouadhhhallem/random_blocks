import pygame
import os
import sys
import math
import random
from settings import *
from game import start_game

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Blocks Game - Main Menu")

# Load fonts
try:
    title_font = pygame.font.Font(None, 92)
    button_font = pygame.font.Font(None, 48)
    info_font = pygame.font.Font(None, 36)
except:
    title_font = pygame.font.SysFont('arial', 92)
    button_font = pygame.font.SysFont('arial', 48)
    info_font = pygame.font.SysFont('arial', 36)

# Create a dynamic color palette for award-winning UI
class ColorPalette:
    def __init__(self):
        # Base colors - vibrant and modern
        self.primary = (41, 128, 185)      # Blue
        self.secondary = (142, 68, 173)    # Purple
        self.accent1 = (39, 174, 96)       # Green
        self.accent2 = (231, 76, 60)       # Red
        self.accent3 = (241, 196, 15)      # Yellow
        self.dark = (30, 30, 30)           # Dark gray
        self.light = (236, 240, 241)       # Light gray
        
        # Dynamic color variations
        self.variations = {}
        self.generate_variations()
        
        # Color schemes for different UI elements
        self.schemes = {
            "blue": {
                "normal": self.primary,
                "hover": self.variations["primary_light"],
                "press": self.variations["primary_dark"],
                "text": self.light,
                "shadow": self.variations["primary_dark"],
                "glow": (*self.primary, 100)
            },
            "purple": {
                "normal": self.secondary,
                "hover": self.variations["secondary_light"],
                "press": self.variations["secondary_dark"],
                "text": self.light,
                "shadow": self.variations["secondary_dark"],
                "glow": (*self.secondary, 100)
            },
            "green": {
                "normal": self.accent1,
                "hover": self.variations["accent1_light"],
                "press": self.variations["accent1_dark"],
                "text": self.light,
                "shadow": self.variations["accent1_dark"],
                "glow": (*self.accent1, 100)
            },
            "red": {
                "normal": self.accent2,
                "hover": self.variations["accent2_light"],
                "press": self.variations["accent2_dark"],
                "text": self.light,
                "shadow": self.variations["accent2_dark"],
                "glow": (*self.accent2, 100)
            },
            "yellow": {
                "normal": self.accent3,
                "hover": self.variations["accent3_light"],
                "press": self.variations["accent3_dark"],
                "text": self.dark,
                "shadow": self.variations["accent3_dark"],
                "glow": (*self.accent3, 100)
            }
        }
        
        # Gradient colors for backgrounds
        self.gradient_start = (20, 40, 80)  # Deep blue
        self.gradient_end = (90, 120, 200)  # Light blue
        
        # Particle colors
        self.particle_colors = [
            (*self.variations["primary_light"], random.randint(50, 150)),
            (*self.variations["secondary_light"], random.randint(50, 150)),
            (*self.variations["accent1_light"], random.randint(50, 150)),
            (*self.variations["accent3_light"], random.randint(50, 150)),
            (255, 255, 255, random.randint(50, 150))
        ]
    
    def generate_variations(self):
        # Generate lighter and darker variations of base colors
        for name, color in [
            ("primary", self.primary),
            ("secondary", self.secondary),
            ("accent1", self.accent1),
            ("accent2", self.accent2),
            ("accent3", self.accent3)
        ]:
            # Lighter variation (more vibrant)
            self.variations[f"{name}_light"] = tuple(min(255, c + 30) for c in color)
            
            # Darker variation (more subdued)
            self.variations[f"{name}_dark"] = tuple(max(0, c - 30) for c in color)
            
            # Very light variation (for highlights)
            self.variations[f"{name}_very_light"] = tuple(min(255, c + 60) for c in color)
            
            # Very dark variation (for shadows)
            self.variations[f"{name}_very_dark"] = tuple(max(0, c - 60) for c in color)
    
    def get_random_particle_color(self):
        return random.choice(self.particle_colors)
    
    def get_gradient_color(self, position):
        # Generate a color at a specific position in the gradient (0.0 to 1.0)
        return tuple(
            int(self.gradient_start[i] + (self.gradient_end[i] - self.gradient_start[i]) * position)
            for i in range(3)
        )

# Create color palette
colors = ColorPalette()

# Load assets with error handling
def load_image(path, fallback_color=colors.gradient_start):
    try:
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        else:
            # Try alternative path format
            alt_path = path.replace("c:\\", "").replace("\\", "/")
            if os.path.exists(alt_path):
                return pygame.image.load(alt_path).convert_alpha()
            else:
                # Create fallback surface
                surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                surface.fill(fallback_color)
                return surface
    except:
        # Create fallback surface
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill(fallback_color)
        return surface

# Create a gradient background
menu_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
for y in range(SCREEN_HEIGHT):
    # Create a smooth gradient from dark blue to light blue
    position = y / SCREEN_HEIGHT
    color = colors.get_gradient_color(position)
    pygame.draw.line(menu_background, color, (0, y), (SCREEN_WIDTH, y))

# Add subtle pattern to background
for _ in range(300):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    radius = random.randint(1, 3)
    alpha = random.randint(10, 40)
    color = (*colors.light, alpha)
    pygame.draw.circle(menu_background, color, (x, y), radius)

# Create overlay for depth effect
overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 80))  # Semi-transparent black

# Particle system for background effects
class Particle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 4)
        self.speed = random.uniform(0.5, 2.0)
        self.color = colors.get_random_particle_color()
        self.angle = random.uniform(0, 2 * math.pi)

    def update(self):
        self.y += self.speed
        self.x += math.sin(self.angle) * 0.5
        
        # Reset if out of screen
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
        
        if self.x < 0 or self.x > SCREEN_WIDTH:
            self.angle = -self.angle

    def draw(self, surface):
        pygame.draw.circle(
            surface, 
            self.color, 
            (int(self.x), int(self.y)), 
            self.size
        )

# Create particles
particles = [Particle() for _ in range(100)]

# Modern animated button class
class AnimatedButton:
    def __init__(self, x, y, width, height, text, action=None, color_scheme="blue"):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        
        # Get color scheme from palette
        self.color_scheme = colors.schemes.get(color_scheme, colors.schemes["blue"])
        
        # Try to load font, fall back to system font if needed
        try:
            self.font = pygame.font.Font(None, 48)
        except:
            self.font = pygame.font.SysFont('arial', 48)
            
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
        
        # Draw text with slight shadow for depth
        text_surface = self.font.render(self.text, True, (0, 0, 0, 128))
        text_rect = text_surface.get_rect(center=(self.rect.center[0] + 2, self.rect.center[1] + 2))
        surface.blit(text_surface, text_rect)
        
        text_surface = self.font.render(self.text, True, self.color_scheme["text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

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
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered():
            self.state = "press"
            self.target_scale = self.press_scale
            return True
        elif event.type == pygame.MOUSEBUTTONUP and self.state == "press":
            self.state = "hover" if self.is_hovered() else "normal"
            self.target_scale = self.hover_scale if self.is_hovered() else 1.0
            return self.is_hovered()
        return False

# Create buttons
buttons = [
    AnimatedButton(
        SCREEN_WIDTH // 2 - 150, 
        SCREEN_HEIGHT // 2 - 60, 
        300, 70, 
        "Start Game", 
        None,
        "green"
    ),
    AnimatedButton(
        SCREEN_WIDTH // 2 - 150, 
        SCREEN_HEIGHT // 2 + 30, 
        300, 70, 
        "High Scores",
        None,
        "blue"
    ),
    AnimatedButton(
        SCREEN_WIDTH // 2 - 150, 
        SCREEN_HEIGHT // 2 + 120, 
        300, 70, 
        "Settings",
        None,
        "purple"
    ),
    AnimatedButton(
        SCREEN_WIDTH // 2 - 150, 
        SCREEN_HEIGHT // 2 + 210, 
        300, 70, 
        "Exit", 
        pygame.quit,
        "red"
    )
]

# High scores screen with modern UI
def display_high_scores():
    running = True
    back_button = AnimatedButton(
        SCREEN_WIDTH // 2 - 100, 
        SCREEN_HEIGHT - 100, 
        200, 60, 
        "Back",
        None,
        "blue"
    )
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    
    # Create a panel for scores
    panel = pygame.Surface((600, 500), pygame.SRCALPHA)
    panel.fill((30, 30, 30, 230))
    panel_rect = panel.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Add decorative elements to panel
    pygame.draw.rect(panel, colors.primary, (0, 0, 600, 70))
    pygame.draw.rect(panel, colors.variations["primary_dark"], (0, 70, 600, 10))
    
    # Add decorative pattern to panel
    for _ in range(50):
        x = random.randint(0, 600)
        y = random.randint(100, 500)
        size = random.randint(1, 3)
        alpha = random.randint(10, 40)
        color = (*colors.light, alpha)
        pygame.draw.circle(panel, color, (x, y), size)
    
    # Load scores
    try:
        with open(SCORES_FILE, "r") as file:
            top_score = int(file.read())
    except FileNotFoundError:
        top_score = 0
    except:
        top_score = 0
    
    # Render title
    title_text = title_font.render("High Scores", True, WHITE)
    title_rect = title_text.get_rect(center=(300, 35))
    panel.blit(title_text, title_rect)
    
    # Render scores with decorative elements
    score_text = button_font.render(f"Top Score: {top_score}", True, WHITE)
    score_rect = score_text.get_rect(center=(300, 150))
    panel.blit(score_text, score_rect)
    
    # Add decorative line
    pygame.draw.line(panel, colors.primary, (150, 200), (450, 200), 3)
    
    # Add some fictional stats for visual appeal
    stats = [
        ("Games Played", "42"),
        ("Total Time", "3h 27m"),
        ("Highest Level", "8"),
        ("Blocks Collected", "156")
    ]
    
    y_pos = 250
    for stat, value in stats:
        stat_text = info_font.render(f"{stat}:", True, (200, 200, 200))
        value_text = info_font.render(value, True, WHITE)
        panel.blit(stat_text, (150, y_pos))
        panel.blit(value_text, (450 - value_text.get_width(), y_pos))
        y_pos += 40
    
    # Add trophy icon
    trophy_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    trophy_color = colors.accent3
    # Draw trophy cup
    pygame.draw.rect(trophy_surface, trophy_color, (15, 10, 20, 25))
    pygame.draw.rect(trophy_surface, trophy_color, (10, 5, 30, 10))
    pygame.draw.rect(trophy_surface, trophy_color, (20, 35, 10, 10))
    panel.blit(trophy_surface, (270, 100))
    
    # Clear any pending events before entering the loop
    pygame.event.clear()
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if back_button.is_pressed(event):
                running = False
        
        # Draw background
        screen.blit(menu_background, (0, 0))
        
        # Update and draw particles
        for particle in particles:
            particle.update()
            particle.draw(screen)
        
        # Draw overlay
        screen.blit(overlay, (0, 0))
        
        # Draw panel
        screen.blit(panel, panel_rect.topleft)
        
        # Update button hover state
        back_button.is_hovered()
        
        # Draw back button
        back_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Return to menu
    return "menu"

# Settings menu with modern UI
def display_settings():
    running = True
    back_button = AnimatedButton(
        SCREEN_WIDTH // 2 - 100, 
        SCREEN_HEIGHT - 100, 
        200, 60, 
        "Back",
        None,
        "blue"
    )
    
    # Create sliders for settings
    class Slider:
        def __init__(self, x, y, width, height, min_val, max_val, initial, label):
            self.rect = pygame.Rect(x, y, width, height)
            self.handle_rect = pygame.Rect(0, 0, 20, height + 10)
            self.min_val = min_val
            self.max_val = max_val
            self.value = initial
            self.label = label
            self.dragging = False
            self.update_handle_position()
            self.active_color = colors.primary
            self.inactive_color = (60, 60, 60)
            self.handle_color = (230, 230, 230)
            self.handle_border = (200, 200, 200)
            self.pulse_time = 0
            self.pulse_duration = 0
        
        def update_handle_position(self):
            value_range = self.max_val - self.min_val
            position_range = self.rect.width - self.handle_rect.width
            relative_value = (self.value - self.min_val) / value_range
            self.handle_rect.x = self.rect.x + int(relative_value * position_range)
            self.handle_rect.y = self.rect.y - 5
        
        def draw(self, surface):
            # Draw track
            pygame.draw.rect(surface, self.inactive_color, self.rect, border_radius=5)
            
            # Calculate active color with pulse effect
            active_color = self.active_color
            if self.pulse_duration > 0:
                pulse_factor = math.sin(math.pi * self.pulse_time / self.pulse_duration)
                active_color = tuple(
                    int(c + (255 - c) * pulse_factor * 0.5)
                    for c in self.active_color
                )
                self.pulse_time += 1
                if self.pulse_time >= self.pulse_duration:
                    self.pulse_duration = 0
                    self.pulse_time = 0
            
            # Draw active part of track
            pygame.draw.rect(surface, active_color, 
                             (self.rect.x, self.rect.y, self.handle_rect.x - self.rect.x + 10, self.rect.height),
                             border_radius=5)
            
            # Draw handle
            pygame.draw.rect(surface, self.handle_color, self.handle_rect, border_radius=10)
            pygame.draw.rect(surface, self.handle_border, self.handle_rect, border_radius=10, width=2)
            
            # Draw label
            label_text = info_font.render(f"{self.label}: {int(self.value)}", True, WHITE)
            surface.blit(label_text, (self.rect.x, self.rect.y - 30))
        
        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.handle_rect.collidepoint(event.pos):
                    self.dragging = True
                    # Start pulse effect
                    self.pulse_duration = 30
                    self.pulse_time = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                # Calculate new value based on mouse position
                rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
                value_range = self.max_val - self.min_val
                position_range = self.rect.width - self.handle_rect.width
                self.value = self.min_val + (rel_x / position_range) * value_range
                self.value = max(self.min_val, min(self.max_val, self.value))
                self.update_handle_position()
    
    # Create toggle switch for settings
    class ToggleSwitch:
        def __init__(self, x, y, width, height, label, initial=False):
            self.rect = pygame.Rect(x, y, width, height)
            self.handle_rect = pygame.Rect(0, 0, height - 4, height - 4)
            self.label = label
            self.value = initial
            self.on_color = colors.accent1
            self.off_color = (60, 60, 60)
            self.handle_color = (230, 230, 230)
            self.handle_border = (200, 200, 200)
            self.animation_progress = 1.0 if initial else 0.0
            self.target_progress = 1.0 if initial else 0.0
            self.animation_speed = 0.2
            self.update_handle_position()
        
        def update_handle_position(self):
            # Smoothly animate between positions
            if self.animation_progress != self.target_progress:
                self.animation_progress += (self.target_progress - self.animation_progress) * self.animation_speed
            
            # Calculate handle position based on animation progress
            off_pos = self.rect.x + 2
            on_pos = self.rect.x + self.rect.width - self.handle_rect.width - 2
            self.handle_rect.x = off_pos + (on_pos - off_pos) * self.animation_progress
            self.handle_rect.y = self.rect.y + 2
        
        def draw(self, surface):
            self.update_handle_position()
            
            # Draw track with gradient based on state
            if self.animation_progress > 0:
                # Mix colors based on animation progress
                track_color = tuple(
                    int(off * (1 - self.animation_progress) + on * self.animation_progress)
                    for off, on in zip(self.off_color, self.on_color)
                )
            else:
                track_color = self.off_color
            
            pygame.draw.rect(surface, track_color, self.rect, border_radius=self.rect.height // 2)
            
            # Draw handle
            pygame.draw.rect(surface, self.handle_color, self.handle_rect, border_radius=self.handle_rect.height // 2)
            pygame.draw.rect(surface, self.handle_border, self.handle_rect, border_radius=self.handle_rect.height // 2, width=1)
            
            # Draw label
            label_text = info_font.render(f"{self.label}: {'On' if self.value else 'Off'}", True, WHITE)
            surface.blit(label_text, (self.rect.x, self.rect.y - 30))
        
        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.value = not self.value
                    self.target_progress = 1.0 if self.value else 0.0
                    return True
            return False
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    
    # Create a panel for settings
    panel = pygame.Surface((600, 500), pygame.SRCALPHA)
    panel.fill((30, 30, 30, 230))
    panel_rect = panel.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Add decorative elements to panel
    pygame.draw.rect(panel, colors.secondary, (0, 0, 600, 70))
    pygame.draw.rect(panel, colors.variations["secondary_dark"], (0, 70, 600, 10))
    
    # Add decorative pattern to panel
    for _ in range(50):
        x = random.randint(0, 600)
        y = random.randint(100, 500)
        size = random.randint(1, 3)
        alpha = random.randint(10, 40)
        color = (*colors.light, alpha)
        pygame.draw.circle(panel, color, (x, y), size)
    
    # Render title
    title_text = title_font.render("Settings", True, WHITE)
    title_rect = title_text.get_rect(center=(300, 35))
    panel.blit(title_text, title_rect)
    
    # Create settings controls
    sliders = [
        Slider(150, 150, 300, 10, 0, 100, 50, "Music Volume"),
        Slider(150, 230, 300, 10, 0, 100, 70, "Sound Effects"),
        Slider(150, 310, 300, 10, 1, 10, 5, "Difficulty")
    ]
    
    toggles = [
        ToggleSwitch(150, 380, 60, 30, "Fullscreen", False),
        ToggleSwitch(350, 380, 60, 30, "Particles", True)
    ]
    
    # Add settings icon
    settings_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    settings_color = colors.secondary
    # Draw gear icon
    pygame.draw.circle(settings_surface, settings_color, (25, 25), 15)
    pygame.draw.circle(settings_surface, (30, 30, 30), (25, 25), 8)
    for i in range(8):
        angle = i * math.pi / 4
        x1 = 25 + 12 * math.cos(angle)
        y1 = 25 + 12 * math.sin(angle)
        x2 = 25 + 20 * math.cos(angle)
        y2 = 25 + 20 * math.sin(angle)
        pygame.draw.line(settings_surface, settings_color, (x1, y1), (x2, y2), 4)
    panel.blit(settings_surface, (270, 90))
    
    # Clear any pending events before entering the loop
    pygame.event.clear()
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if back_button.is_pressed(event):
                running = False
            
            # Handle slider and toggle events
            for slider in sliders:
                slider.handle_event(event)
            for toggle in toggles:
                toggle.handle_event(event)
        
        # Draw background
        screen.blit(menu_background, (0, 0))
        
        # Update and draw particles
        for particle in particles:
            particle.update()
            particle.draw(screen)
        
        # Draw overlay
        screen.blit(overlay, (0, 0))
        
        # Draw panel
        screen.blit(panel, panel_rect.topleft)
        
        # Draw sliders and toggles
        for slider in sliders:
            slider.draw(panel)
        for toggle in toggles:
            toggle.draw(panel)
        
        # Update button hover state
        back_button.is_hovered()
        
        # Draw back button
        back_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Return to menu
    return "menu"

# Main menu loop
def main_menu():
    running = True
    while running:
        # Clear event queue before processing new events
        pygame.event.clear()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle button clicks
            for button in buttons:
                if button.is_pressed(event):
                    if button.text == "Start Game":
                        start_game()
                    elif button.text == "High Scores":
                        result = display_high_scores()
                        # Clear event queue after returning from submenu
                        pygame.event.clear()
                    elif button.text == "Settings":
                        result = display_settings()
                        # Clear event queue after returning from submenu
                        pygame.event.clear()
                    elif button.text == "Exit":
                        running = False
        
        # Draw background
        screen.blit(menu_background, (0, 0))
        
        # Update and draw particles
        for particle in particles:
            particle.update()
            particle.draw(screen)
        
        # Draw semi-transparent overlay for better text contrast
        screen.blit(overlay, (0, 0))
        
        # Draw animated title
        title_angle = pygame.time.get_ticks() / 20 % 360
        title_scale = 1.0 + math.sin(math.radians(title_angle)) * 0.05
        
        title_text = title_font.render("Random Blocks", True, WHITE)
        title_shadow = title_font.render("Random Blocks", True, (0, 0, 0))
        
        # Create a pulsing glow effect
        glow_surf = pygame.Surface((title_text.get_width() + 40, title_text.get_height() + 40), pygame.SRCALPHA)
        glow_color = (*colors.primary, 100 + int(math.sin(math.radians(title_angle)) * 50))
        glow_text = title_font.render("Random Blocks", True, glow_color)
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
        screen.blit(scaled_glow, glow_rect)
        screen.blit(scaled_shadow, shadow_rect)
        screen.blit(scaled_title, title_rect)
        
        # Draw subtitle
        subtitle_text = button_font.render("Game Edition", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Update and draw buttons
        for button in buttons:
            button.is_hovered()  # Update hover state
            button.draw(screen)
        
        # Draw version info
        version_text = info_font.render("v1.0.0", True, (150, 150, 150))
        screen.blit(version_text, (20, SCREEN_HEIGHT - 40))
        
        # Draw copyright
        copyright_text = info_font.render("© 2025 Random Blocks Studio", True, (150, 150, 150))
        copyright_rect = copyright_text.get_rect(right=SCREEN_WIDTH - 20, bottom=SCREEN_HEIGHT - 20)
        screen.blit(copyright_text, copyright_rect)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()

# Function to handle menu events for integration with main.py
def handle_menu_event(event):
    for button in buttons:
        if button.is_pressed(event):
            if button.text == "Start Game":
                return "start_game"
            elif button.text == "Exit":
                return "exit"
            elif button.text == "High Scores":
                result = display_high_scores()
                return result  # Will return "menu" when back button is pressed
            elif button.text == "Settings":
                result = display_settings()
                return result  # Will return "menu" when back button is pressed
    return None

import pygame
import random
import math
import os
from particle_system_fixed import ParticleSystem

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Taille de l'écran
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Taille des blocs
BLOCK_SIZE = 30
BLOCK_GAP = 2
MAP_PADDING = 50

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()

# Classe pour le fond parallaxe amélioré
class EnhancedParallaxBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layers = []
        self.initialize_layers()
        self.offset = 0
        
    def initialize_layers(self):
        # Couche 1 (la plus éloignée) - Étoiles lointaines
        layer1 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 2)
            alpha = random.randint(100, 200)
            color = (255, 255, 255, alpha)
            pygame.draw.circle(layer1, color, (x, y), size)
        self.layers.append({"surface": layer1, "speed": 0.1, "position": 0})
        
        # Couche 2 - Étoiles moyennes
        layer2 = pygame.Surface((self.width * 2, self.height), pygame.SRCALPHA)
        for _ in range(150):
            x = random.randint(0, self.width * 2)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            alpha = random.randint(150, 250)
            color = (255, 255, 255, alpha)
            pygame.draw.circle(layer2, color, (x, y), size)
        self.layers.append({"surface": layer2, "speed": 0.3, "position": 0})
        
        # Couche 3 - Nébuleuses colorées
        layer3 = pygame.Surface((self.width * 2, self.height), pygame.SRCALPHA)
        for _ in range(5):
            x = random.randint(0, self.width * 2)
            y = random.randint(0, self.height)
            size = random.randint(50, 150)
            alpha = random.randint(20, 40)
            color_choices = [
                (255, 100, 100, alpha),  # Rouge
                (100, 100, 255, alpha),  # Bleu
                (255, 100, 255, alpha),  # Violet
                (100, 255, 255, alpha),  # Cyan
            ]
            color = random.choice(color_choices)
            
            # Créer une surface pour la nébuleuse
            nebula = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            for i in range(20):
                offset_x = random.randint(-size//2, size//2)
                offset_y = random.randint(-size//2, size//2)
                radius = random.randint(size//4, size//2)
                pygame.draw.circle(nebula, color, (size + offset_x, size + offset_y), radius)
            
            layer3.blit(nebula, (x - size, y - size))
        self.layers.append({"surface": layer3, "speed": 0.5, "position": 0})
        
        # Couche 4 - Étoiles proches
        layer4 = pygame.Surface((self.width * 3, self.height), pygame.SRCALPHA)
        for _ in range(50):
            x = random.randint(0, self.width * 3)
            y = random.randint(0, self.height)
            size = random.randint(2, 4)
            color = (255, 255, 255)
            pygame.draw.circle(layer4, color, (x, y), size)
            
            # Ajouter un effet de lueur
            glow_size = size * 2
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            for radius in range(size, glow_size, 1):
                alpha = 150 - (radius - size) * (150 / (glow_size - size))
                pygame.draw.circle(glow_surface, (255, 255, 255, int(alpha)), (glow_size, glow_size), radius)
            
            layer4.blit(glow_surface, (x - glow_size, y - glow_size))
        self.layers.append({"surface": layer4, "speed": 0.8, "position": 0})
    
    def update(self, direction):
        self.offset += direction
        for layer in self.layers:
            layer["position"] = (layer["position"] + layer["speed"] * direction) % (layer["surface"].get_width())
    
    def draw(self, surface):
        for layer in self.layers:
            # Calculer les positions de dessin
            pos_x = int(-layer["position"])
            surface.blit(layer["surface"], (pos_x, 0))
            
            # Si nécessaire, dessiner une deuxième fois pour couvrir l'écran
            if pos_x + layer["surface"].get_width() < self.width:
                surface.blit(layer["surface"], (pos_x + layer["surface"].get_width(), 0))

# Classe pour les effets d'interface utilisateur
class UIEffects:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.animation_time = 0
        self.cached_surfaces = {}
        
    def update(self):
        self.animation_time += 1
        if self.animation_time > 1000:
            self.animation_time = 0
            
    def create_gradient_button(self, width, height, color1, color2, border_radius=10):
        key = f"gradient_button_{width}_{height}_{color1}_{color2}_{border_radius}"
        
        if key in self.cached_surfaces:
            return self.cached_surfaces[key]
            
        button = pygame.Surface((width, height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, width, height)
        
        # Créer le dégradé
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(button, (r, g, b), (0, y), (width, y))
            
        # Appliquer le masque arrondi
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), rect, border_radius=border_radius)
        
        # Combiner le dégradé et le masque
        result = pygame.Surface((width, height), pygame.SRCALPHA)
        result.blit(button, (0, 0))
        result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Ajouter une bordure
        pygame.draw.rect(result, (255, 255, 255, 100), rect, width=2, border_radius=border_radius)
        
        self.cached_surfaces[key] = result
        return result
        
    def create_glass_panel(self, width, height, bg_color=(0, 0, 0, 150), border_color=(255, 255, 255, 50), border_width=1):
        key = f"glass_panel_{width}_{height}_{bg_color}_{border_color}_{border_width}"
        
        if key in self.cached_surfaces:
            return self.cached_surfaces[key]
            
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, width, height)
        
        # Fond semi-transparent
        pygame.draw.rect(panel, bg_color, rect, border_radius=10)
        
        # Effet de brillance en haut
        highlight = pygame.Surface((width, height // 4), pygame.SRCALPHA)
        for y in range(height // 4):
            alpha = 50 - (y * 2)
            if alpha > 0:
                pygame.draw.line(highlight, (255, 255, 255, alpha), (0, y), (width, y))
        panel.blit(highlight, (0, 0))
        
        # Bordure
        pygame.draw.rect(panel, border_color, rect, width=border_width, border_radius=10)
        
        self.cached_surfaces[key] = panel
        return panel
        
    def create_neon_text(self, text, font, text_color, glow_color, glow_radius=5):
        key = f"neon_text_{text}_{font.get_height()}_{text_color}_{glow_color}_{glow_radius}"
        
        if key in self.cached_surfaces:
            return self.cached_surfaces[key]
            
        # Rendu du texte
        text_surface = font.render(text, True, text_color)
        width, height = text_surface.get_size()
        
        # Créer une surface plus grande pour accueillir la lueur
        result = pygame.Surface((width + glow_radius * 2, height + glow_radius * 2), pygame.SRCALPHA)
        
        # Créer la lueur
        glow_surface = pygame.Surface((width + glow_radius * 2, height + glow_radius * 2), pygame.SRCALPHA)
        for i in range(1, glow_radius + 1):
            alpha = 200 - (i * 20)
            if alpha < 0:
                alpha = 0
            glow = font.render(text, True, (*glow_color, alpha))
            for offset_x in range(-i, i + 1, max(1, i // 2)):
                for offset_y in range(-i, i + 1, max(1, i // 2)):
                    glow_surface.blit(glow, (glow_radius + offset_x, glow_radius + offset_y))
        
        # Combiner la lueur et le texte
        result.blit(glow_surface, (0, 0))
        result.blit(text_surface, (glow_radius, glow_radius))
        
        self.cached_surfaces[key] = result
        return result
        
    def create_animated_icon(self, icon_type, size, color):
        animation_frame = (self.animation_time // 5) % 8
        key = f"animated_icon_{icon_type}_{size}_{color}_{animation_frame}"
        
        if key in self.cached_surfaces:
            return self.cached_surfaces[key]
            
        icon = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if icon_type == "gear":
            # Dessiner une roue dentée qui tourne
            center = size // 2
            outer_radius = size // 2 - 2
            inner_radius = size // 4
            teeth = 8
            
            # Rotation basée sur le temps d'animation
            rotation = self.animation_time * 2
            
            for i in range(teeth):
                angle1 = math.radians(i * (360 / teeth) + rotation)
                angle2 = math.radians((i + 0.5) * (360 / teeth) + rotation)
                angle3 = math.radians((i + 1) * (360 / teeth) + rotation)
                
                x1 = center + int(math.cos(angle1) * outer_radius)
                y1 = center + int(math.sin(angle1) * outer_radius)
                
                x2 = center + int(math.cos(angle2) * (outer_radius + 5))
                y2 = center + int(math.sin(angle2) * (outer_radius + 5))
                
                x3 = center + int(math.cos(angle3) * outer_radius)
                y3 = center + int(math.sin(angle3) * outer_radius)
                
                pygame.draw.polygon(icon, color, [(center, center), (x1, y1), (x2, y2), (x3, y3)])
            
            pygame.draw.circle(icon, color, (center, center), inner_radius)
            
        elif icon_type == "star":
            # Dessiner une étoile qui pulse
            center = size // 2
            points = 5
            inner_radius = size // 4
            outer_radius = size // 2 - 2
            
            # Pulsation basée sur le temps d'animation
            pulse = math.sin(self.animation_time * 0.1) * 0.2 + 0.8
            adjusted_outer_radius = int(outer_radius * pulse)
            
            star_points = []
            for i in range(points * 2):
                angle = math.radians(i * (360 / (points * 2)))
                radius = adjusted_outer_radius if i % 2 == 0 else inner_radius
                x = center + int(math.cos(angle) * radius)
                y = center + int(math.sin(angle) * radius)
                star_points.append((x, y))
                
            pygame.draw.polygon(icon, color, star_points)
            
        elif icon_type == "pulse":
            # Dessiner un cercle qui pulse
            center = size // 2
            max_radius = size // 2 - 2
            
            # Calculer le rayon actuel basé sur l'animation
            current_radius = int(max_radius * (0.5 + 0.5 * math.sin(self.animation_time * 0.1)))
            
            pygame.draw.circle(icon, color, (center, center), current_radius)
            
            # Ajouter des cercles concentriques
            for i in range(3):
                radius = current_radius - (i + 1) * 5
                if radius > 0:
                    alpha = 255 - i * 70
                    if alpha < 0:
                        alpha = 0
                    pygame.draw.circle(icon, (*color[:3], alpha), (center, center), radius, 1)
        
        self.cached_surfaces[key] = icon
        return icon
        
    def create_progress_bar(self, width, height, progress, color_scheme="blue"):
        key = f"progress_bar_{width}_{height}_{progress}_{color_scheme}"
        
        if key in self.cached_surfaces:
            return self.cached_surfaces[key]
            
        bar = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Définir les couleurs en fonction du schéma
        if color_scheme == "blue":
            bg_color = (30, 30, 80, 150)
            border_color = (100, 100, 255, 200)
            fill_color1 = (50, 100, 255)
            fill_color2 = (100, 200, 255)
        elif color_scheme == "green":
            bg_color = (30, 80, 30, 150)
            border_color = (100, 255, 100, 200)
            fill_color1 = (50, 255, 100)
            fill_color2 = (100, 255, 200)
        elif color_scheme == "red":
            bg_color = (80, 30, 30, 150)
            border_color = (255, 100, 100, 200)
            fill_color1 = (255, 50, 50)
            fill_color2 = (255, 100, 100)
        else:  # Default
            bg_color = (50, 50, 50, 150)
            border_color = (200, 200, 200, 200)
            fill_color1 = (150, 150, 150)
            fill_color2 = (200, 200, 200)
            
        # Dessiner le fond
        pygame.draw.rect(bar, bg_color, (0, 0, width, height), border_radius=height//2)
        
        # Dessiner la barre de progression
        if progress > 0:
            fill_width = int(width * progress)
            fill_rect = pygame.Rect(0, 0, fill_width, height)
            
            # Créer un dégradé pour le remplissage
            for x in range(fill_width):
                ratio = x / width
                r = int(fill_color1[0] * (1 - ratio) + fill_color2[0] * ratio)
                g = int(fill_color1[1] * (1 - ratio) + fill_color2[1] * ratio)
                b = int(fill_color1[2] * (1 - ratio) + fill_color2[2] * ratio)
                pygame.draw.line(bar, (r, g, b), (x, 0), (x, height))
                
            # Appliquer le masque arrondi
            mask = pygame.Surface((fill_width, height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, fill_width, height), border_radius=height//2)
            
            # Dessiner des particules animées dans la barre
            particle_offset = (self.animation_time // 2) % width
            for i in range(5):
                particle_x = (particle_offset + i * width // 5) % fill_width
                pygame.draw.circle(mask, (255, 255, 255, 150), (particle_x, height // 2), height // 4)
        
        # Dessiner la bordure
        pygame.draw.rect(bar, border_color, (0, 0, width, height), width=2, border_radius=height//2)
        
        self.cached_surfaces[key] = bar
        return bar
        
    def create_tooltip(self, text, font, width=200, height=None):
        # Calculer la hauteur en fonction du texte
        if height is None:
            text_lines = self._wrap_text(text, font, width - 20)
            height = len(text_lines) * (font.get_height() + 2) + 20
            
        key = f"tooltip_{text}_{width}_{height}"
        
        if key in self.cached_surfaces:
            return self.cached_surfaces[key]
            
        tooltip = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fond semi-transparent
        pygame.draw.rect(tooltip, (10, 10, 10, 220), (0, 0, width, height), border_radius=5)
        
        # Bordure
        pygame.draw.rect(tooltip, (200, 200, 200, 100), (0, 0, width, height), width=1, border_radius=5)
        
        # Effet de brillance en haut
        highlight = pygame.Surface((width - 4, 10), pygame.SRCALPHA)
        for y in range(10):
            alpha = 30 - (y * 3)
            if alpha > 0:
                pygame.draw.line(highlight, (255, 255, 255, alpha), (0, y), (width - 4, y))
        tooltip.blit(highlight, (2, 2))
        
        # Rendu du texte
        text_lines = self._wrap_text(text, font, width - 20)
        for i, line in enumerate(text_lines):
            text_surface = font.render(line, True, (220, 220, 220))
            tooltip.blit(text_surface, (10, 10 + i * (font.get_height() + 2)))
            
        self.cached_surfaces[key] = tooltip
        return tooltip
        
    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Tester si l'ajout du mot dépasse la largeur maximale
            test_line = ' '.join(current_line + [word])
            test_width, _ = font.size(test_line)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Si la ligne actuelle n'est pas vide, l'ajouter aux lignes
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Si le mot seul est trop long, le couper
                    lines.append(word)
                    current_line = []
                    
        # Ajouter la dernière ligne
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def create_minimap(self, width, height, player_pos, grid, visible_area=None):
        key = f"minimap_{width}_{height}_{player_pos}_{visible_area}"
        
        # Ne pas mettre en cache la minimap car elle change constamment
        minimap = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fond semi-transparent
        pygame.draw.rect(minimap, (0, 0, 0, 150), (0, 0, width, height), border_radius=5)
        
        # Bordure
        pygame.draw.rect(minimap, (100, 100, 255, 200), (0, 0, width, height), width=1, border_radius=5)
        
        # Calculer l'échelle
        grid_width = len(grid[0]) if grid and grid[0] else 0
        grid_height = len(grid) if grid else 0
        
        if grid_width > 0 and grid_height > 0:
            cell_width = (width - 10) / grid_width
            cell_height = (height - 10) / grid_height
            
            # Dessiner la grille
            for y in range(grid_height):
                for x in range(grid_width):
                    cell_x = 5 + x * cell_width
                    cell_y = 5 + y * cell_height
                    
                    if grid[y][x] == 1:  # Mur
                        pygame.draw.rect(minimap, (100, 100, 100), 
                                        (cell_x, cell_y, cell_width, cell_height))
                    elif grid[y][x] == 2:  # Fin
                        pygame.draw.rect(minimap, (0, 255, 0), 
                                        (cell_x, cell_y, cell_width, cell_height))
                    elif grid[y][x] == 3:  # Power-up
                        pygame.draw.rect(minimap, (255, 255, 0), 
                                        (cell_x, cell_y, cell_width, cell_height))
            
            # Dessiner la zone visible si spécifiée
            if visible_area:
                x, y, w, h = visible_area
                vis_x = 5 + x * cell_width
                vis_y = 5 + y * cell_height
                vis_w = w * cell_width
                vis_h = h * cell_height
                pygame.draw.rect(minimap, (255, 255, 255, 50), 
                                (vis_x, vis_y, vis_w, vis_h), width=1)
            
            # Dessiner la position du joueur
            if player_pos:
                player_x = 5 + player_pos[0] * cell_width + cell_width / 2
                player_y = 5 + player_pos[1] * cell_height + cell_height / 2
                
                # Effet de pulsation
                pulse = math.sin(self.animation_time * 0.1) * 0.2 + 0.8
                player_radius = max(3, min(cell_width, cell_height) / 2 * pulse)
                
                # Dessiner un cercle avec une lueur
                glow_radius = player_radius * 1.5
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                for r in range(int(player_radius), int(glow_radius), 1):
                    alpha = 150 - (r - player_radius) * (150 / (glow_radius - player_radius))
                    pygame.draw.circle(glow_surface, (255, 100, 100, int(alpha)), 
                                    (glow_radius, glow_radius), r)
                
                minimap.blit(glow_surface, 
                            (player_x - glow_radius, player_y - glow_radius))
                pygame.draw.circle(minimap, (255, 0, 0), 
                                (player_x, player_y), player_radius)
        
        return minimap

# Classe principale du jeu
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Labyrinthe Amélioré")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        self.state = "menu"
        self.level = 1
        self.score = 0
        self.steps = 0
        self.time_start = 0
        self.time_elapsed = 0
        
        self.grid = []
        self.rows = 0
        self.cols = 0
        self.character_pos = [0, 0]
        self.start_pos = [0, 0]
        self.end_pos = [0, 0]
        
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        
        self.move_cooldown = 0
        self.default_move_cooldown = 10
        
        self.menu_buttons = []
        self.pause_buttons = []
        
        self.notifications = []
        self.show_minimap = False
        self.minimap_toggle_time = 0
        
        self.active_tooltip = None
        self.tooltip_timer = 0
        
        self.achievements_popup = None
        self.achievements_timer = 0
        
        self.ui_animation_time = 0
        
        # Nouveaux attributs pour les optimisations
        self.frame_counter = 0
        self.fps_values = []
        self.last_fps_update = 0
        self.fps_update_interval = 500
        self.fps_display = "FPS: 0.0"
        
        # Initialiser les systèmes
        self.particle_system = ParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.parallax_background = EnhancedParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui_effects = UIEffects(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Charger les sons
        self.load_sounds()
        
        # Configurer le jeu
        self.setup_game()
        
    def load_sounds(self):
        self.sounds = {}
        try:
            self.sounds["move"] = pygame.mixer.Sound("move.wav")
            self.sounds["win"] = pygame.mixer.Sound("win.wav")
            self.sounds["menu"] = pygame.mixer.Sound("menu.wav")
            self.sounds["button"] = pygame.mixer.Sound("button.wav")
            self.sounds["powerup"] = pygame.mixer.Sound("powerup.wav")
            self.sounds["pause"] = pygame.mixer.Sound("pause.wav")
            self.sounds["unpause"] = pygame.mixer.Sound("unpause.wav")
        except:
            print("Certains sons n'ont pas pu être chargés.")
            
    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def setup_game(self):
        self.create_menu_buttons()
        self.create_pause_buttons()
        
    def create_menu_buttons(self):
        button_width = 200
        button_height = 50
        button_y = SCREEN_HEIGHT // 2
        button_spacing = 70
        
        self.menu_buttons = [
            {
                "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y, button_width, button_height),
                "text": "Jouer",
                "action": self.start_game,
                "hover": False,
                "color1": (41, 128, 185),
                "color2": (52, 152, 219)
            },
            {
                "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y + button_spacing, button_width, button_height),
                "text": "Meilleurs scores",
                "action": self.show_high_scores,
                "hover": False,
                "color1": (41, 128, 185),
                "color2": (52, 152, 219)
            },
            {
                "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y + button_spacing * 2, button_width, button_height),
                "text": "Paramètres",
                "action": self.show_settings,
                "hover": False,
                "color1": (41, 128, 185),
                "color2": (52, 152, 219)
            },
            {
                "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y + button_spacing * 3, button_width, button_height),
                "text": "Quitter",
                "action": self.quit_game,
                "hover": False,
                "color1": (192, 57, 43),
                "color2": (231, 76, 60)
            }
        ]
        
    def create_pause_buttons(self):
        button_width = 200
        button_height = 50
        button_y = SCREEN_HEIGHT // 2
        button_spacing = 70
        
        self.pause_buttons = [
            {
                "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y, button_width, button_height),
                "text": "Continuer",
                "action": self.resume_game,
                "hover": False,
                "color1": (41, 128, 185),
                "color2": (52, 152, 219)
            },
            {
                "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y + button_spacing, button_width, button_height),
                "text": "Menu principal",
                "action": self.return_to_menu,
                "hover": False,
                "color1": (192, 57, 43),
                "color2": (231, 76, 60)
            }
        ]
        
    def generate_level(self):
        self.rows = 10 + self.level
        self.cols = 10 + self.level
        
        # Initialiser la grille avec des murs
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Générer un labyrinthe en utilisant l'algorithme de Prim
        # Commencer par définir tous les espaces comme des murs
        for y in range(self.rows):
            for x in range(self.cols):
                self.grid[y][x] = 1
                
        # Choisir une cellule de départ aléatoire (doit être impaire)
        start_x = random.randint(0, self.cols // 2) * 2
        start_y = random.randint(0, self.rows // 2) * 2
        
        if start_x >= self.cols:
            start_x = self.cols - 2
        if start_y >= self.rows:
            start_y = self.rows - 2
            
        self.grid[start_y][start_x] = 0
        walls = []
        
        # Ajouter les murs adjacents à la liste
        if start_x > 0:
            walls.append((start_x - 1, start_y))
        if start_x < self.cols - 2:
            walls.append((start_x + 1, start_y))
        if start_y > 0:
            walls.append((start_x, start_y - 1))
        if start_y < self.rows - 2:
            walls.append((start_x, start_y + 1))
            
        # Tant qu'il y a des murs dans la liste
        while walls:
            # Choisir un mur au hasard
            wall_x, wall_y = random.choice(walls)
            walls.remove((wall_x, wall_y))
            
            # Vérifier si ce mur sépare deux cellules dont l'une est déjà un passage
            if wall_x % 2 == 0 and wall_y % 2 == 1:
                # Mur vertical
                if wall_x > 0 and wall_x < self.cols - 1:
                    if self.grid[wall_y][wall_x - 1] == 0 and self.grid[wall_y][wall_x + 1] == 1:
                        # Créer un passage
                        self.grid[wall_y][wall_x] = 0
                        self.grid[wall_y][wall_x + 1] = 0
                        
                        # Ajouter les nouveaux murs adjacents
                        if wall_x + 2 < self.cols:
                            walls.append((wall_x + 2, wall_y))
                        if wall_y > 0:
                            walls.append((wall_x + 1, wall_y - 1))
                        if wall_y < self.rows - 1:
                            walls.append((wall_x + 1, wall_y + 1))
                            
                    elif self.grid[wall_y][wall_x - 1] == 1 and self.grid[wall_y][wall_x + 1] == 0:
                        # Créer un passage
                        self.grid[wall_y][wall_x] = 0
                        self.grid[wall_y][wall_x - 1] = 0
                        
                        # Ajouter les nouveaux murs adjacents
                        if wall_x - 2 >= 0:
                            walls.append((wall_x - 2, wall_y))
                        if wall_y > 0:
                            walls.append((wall_x - 1, wall_y - 1))
                        if wall_y < self.rows - 1:
                            walls.append((wall_x - 1, wall_y + 1))
                            
            elif wall_x % 2 == 1 and wall_y % 2 == 0:
                # Mur horizontal
                if wall_y > 0 and wall_y < self.rows - 1:
                    if self.grid[wall_y - 1][wall_x] == 0 and self.grid[wall_y + 1][wall_x] == 1:
                        # Créer un passage
                        self.grid[wall_y][wall_x] = 0
                        self.grid[wall_y + 1][wall_x] = 0
                        
                        # Ajouter les nouveaux murs adjacents
                        if wall_y + 2 < self.rows:
                            walls.append((wall_x, wall_y + 2))
                        if wall_x > 0:
                            walls.append((wall_x - 1, wall_y + 1))
                        if wall_x < self.cols - 1:
                            walls.append((wall_x + 1, wall_y + 1))
                            
                    elif self.grid[wall_y - 1][wall_x] == 1 and self.grid[wall_y + 1][wall_x] == 0:
                        # Créer un passage
                        self.grid[wall_y][wall_x] = 0
                        self.grid[wall_y - 1][wall_x] = 0
                        
                        # Ajouter les nouveaux murs adjacents
                        if wall_y - 2 >= 0:
                            walls.append((wall_x, wall_y - 2))
                        if wall_x > 0:
                            walls.append((wall_x - 1, wall_y - 1))
                        if wall_x < self.cols - 1:
                            walls.append((wall_x + 1, wall_y - 1))
                            
        # Placer le point de départ et le point d'arrivée
        # Trouver un espace vide pour le départ
        empty_cells = []
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] == 0:
                    empty_cells.append((x, y))
                    
        if empty_cells:
            # Choisir un point de départ aléatoire
            self.start_pos = random.choice(empty_cells)
            empty_cells.remove(self.start_pos)
            
            # Choisir un point d'arrivée aléatoire (le plus éloigné possible du départ)
            max_distance = 0
            self.end_pos = self.start_pos
            
            for cell in empty_cells:
                distance = abs(cell[0] - self.start_pos[0]) + abs(cell[1] - self.start_pos[1])
                if distance > max_distance:
                    max_distance = distance
                    self.end_pos = cell
                    
            # Marquer le point d'arrivée dans la grille
            self.grid[self.end_pos[1]][self.end_pos[0]] = 2
            
            # Placer quelques power-ups
            power_up_count = min(3, len(empty_cells) // 10)
            for _ in range(power_up_count):
                if empty_cells:
                    power_up_pos = random.choice(empty_cells)
                    empty_cells.remove(power_up_pos)
                    self.grid[power_up_pos[1]][power_up_pos[0]] = 3
                    
        # Initialiser la position du personnage
        self.character_pos = list(self.start_pos)
        
        # Initialiser la caméra
        self.camera_x = self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_WIDTH // 2 + BLOCK_SIZE // 2
        self.camera_y = self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_HEIGHT // 2 + BLOCK_SIZE // 2
        self.target_camera_x = self.camera_x
        self.target_camera_y = self.camera_y
        
        # Réinitialiser les compteurs
        self.steps = 0
        self.time_start = pygame.time.get_ticks()
        self.time_elapsed = 0
        
    def start_game(self):
        self.state = "playing"
        self.level = 1
        self.score = 0
        self.generate_level()
        self.play_sound("menu")
        
    def resume_game(self):
        self.state = "playing"
        self.play_sound("unpause")
        
    def show_high_scores(self):
        self.state = "high_scores"
        self.play_sound("menu")
        
    def show_settings(self):
        self.state = "settings"
        self.play_sound("menu")
        
    def return_to_menu(self):
        self.state = "menu"
        self.play_sound("menu")
        
    def quit_game(self):
        pygame.quit()
        sys.exit()
        
    def level_complete(self):
        self.play_sound("win")
        
        # Calculer le score
        time_bonus = max(0, 1000 - self.time_elapsed // 1000)
        step_penalty = min(500, self.steps * 10)
        level_score = 1000 + time_bonus - step_penalty
        
        self.score += level_score
        
        # Afficher une notification
        self.add_notification(f"Niveau {self.level} terminé! Score: {level_score}", 3000, "green")
        
        # Afficher un popup d'accomplissement
        self.show_achievement(f"Niveau {self.level} terminé!", f"Score: {level_score} points", "star")
        
        # Passer au niveau suivant
        self.level += 1
        self.generate_level()
        
    def check_powerups(self):
        if self.grid[self.character_pos[1]][self.character_pos[0]] == 3:
            self.play_sound("powerup")
            self.grid[self.character_pos[1]][self.character_pos[0]] = 0
            
            # Ajouter des points
            self.score += 100
            
            # Afficher une notification
            self.add_notification("Power-up collecté! +100 points", 2000, "yellow")
            
            # Ajouter des particules
            self.particle_system.add_explosion_particles(
                self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING + BLOCK_SIZE // 2,
                self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING + BLOCK_SIZE // 2,
                30,
                [(255, 255, 0), (255, 200, 0), (255, 150, 0)]
            )
            
    def add_notification(self, text, duration=3000, color_scheme="blue"):
        self.notifications.append({
            "text": text,
            "duration": duration,
            "start_time": pygame.time.get_ticks(),
            "color_scheme": color_scheme
        })
        
    def show_achievement(self, title, description, icon_type="star"):
        self.achievements_popup = {
            "title": title,
            "description": description,
            "icon_type": icon_type,
            "start_time": pygame.time.get_ticks(),
            "duration": 5000
        }
        self.achievements_timer = pygame.time.get_ticks()
        
    def show_tooltip(self, text, x, y, width=200):
        self.active_tooltip = {
            "text": text,
            "x": x,
            "y": y,
            "width": width
        }
        self.tooltip_timer = pygame.time.get_ticks()
        
    def hide_tooltip(self):
        self.active_tooltip = None
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                
            elif event.type == pygame.KEYDOWN:
                if self.state == "playing":
                    self.handle_game_events(event)
                elif self.state == "paused":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "playing"
                        self.play_sound("unpause")
                elif self.state == "menu" or self.state == "high_scores" or self.state == "settings":
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "high_scores" or self.state == "settings":
                            self.state = "menu"
                            self.play_sound("menu")
                            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    if self.state == "menu":
                        self.handle_menu_click(event.pos)
                    elif self.state == "paused":
                        self.handle_pause_click(event.pos)
                    elif self.state == "high_scores" or self.state == "settings":
                        # Vérifier si le bouton retour est cliqué
                        back_button_rect = pygame.Rect(20, 20, 100, 40)
                        if back_button_rect.collidepoint(event.pos):
                            self.state = "menu"
                            self.play_sound("menu")
                            
            elif event.type == pygame.MOUSEMOTION:
                if self.state == "menu":
                    self.handle_menu_hover(event.pos)
                elif self.state == "paused":
                    self.handle_pause_hover(event.pos)
                    
    def handle_game_events(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = "paused"
            self.play_sound("pause")
        elif event.key == pygame.K_m:
            if pygame.time.get_ticks() - self.minimap_toggle_time > 500:
                self.show_minimap = not self.show_minimap
                self.minimap_toggle_time = pygame.time.get_ticks()
                self.add_notification(f"Minimap: {'ON' if self.show_minimap else 'OFF'}", 2000, "blue")
                
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
                
            # Vérifier si la nouvelle position est valide
            if (0 <= new_pos[0] < self.cols and 
                0 <= new_pos[1] < self.rows and 
                self.grid[new_pos[1]][new_pos[0]] != 1):  # Pas un mur
                
                self.character_pos = new_pos
                self.steps += 1
                self.move_cooldown = self.default_move_cooldown
                self.play_sound("move")
                
                # Mettre à jour la caméra
                self.target_camera_x = self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_WIDTH // 2 + BLOCK_SIZE // 2
                self.target_camera_y = self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_HEIGHT // 2 + BLOCK_SIZE // 2
                
                # Ajouter des particules de mouvement
                self.particle_system.add_movement_particles(
                    self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING + BLOCK_SIZE // 2,
                    self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING + BLOCK_SIZE // 2,
                    5
                )
                
                # Vérifier les power-ups
                self.check_powerups()
                
                # Vérifier si on a atteint la fin
                if self.character_pos[0] == self.end_pos[0] and self.character_pos[1] == self.end_pos[1]:
                    self.level_complete()
                    
    def handle_menu_click(self, pos):
        for button in self.menu_buttons:
            if button["rect"].collidepoint(pos):
                self.play_sound("button")
                button["action"]()
                break
                
    def handle_pause_click(self, pos):
        for button in self.pause_buttons:
            if button["rect"].collidepoint(pos):
                self.play_sound("button")
                button["action"]()
                break
                
    def handle_menu_hover(self, pos):
        for button in self.menu_buttons:
            button["hover"] = button["rect"].collidepoint(pos)
            
    def handle_pause_hover(self, pos):
        for button in self.pause_buttons:
            button["hover"] = button["rect"].collidepoint(pos)
            
    def update_menu(self):
        # Mettre à jour le fond parallaxe
        self.parallax_background.update(0.5)
        
        # Mettre à jour les particules
        for i in range(len(self.particle_system.particles)):
            if i % 3 == self.frame_counter % 3:  # Optimisation: mettre à jour seulement 1/3 des particules par frame
                particle = self.particle_system.particles[i]
                particle.update()
                
        # Ajouter de nouvelles particules aléatoirement
        if random.random() < 0.1:
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.particle_system.add_particles(x, y, 3)
            
        # Mettre à jour les effets d'interface
        self.ui_effects.update()
        self.ui_animation_time += 1
        
    def update_game(self):
        # Mettre à jour le temps écoulé
        self.time_elapsed = pygame.time.get_ticks() - self.time_start
        
        # Mettre à jour le cooldown de mouvement
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            
        # Mettre à jour la caméra avec un effet de lissage
        self.camera_x += (self.target_camera_x - self.camera_x) * 0.1
        self.camera_y += (self.target_camera_y - self.camera_y) * 0.1
        
        # Mettre à jour le fond parallaxe
        camera_dx = self.target_camera_x - self.camera_x
        self.parallax_background.update(camera_dx * 0.01)
        
        # Mettre à jour les particules
        self.particle_system.update()
        
        # Mettre à jour les effets d'interface
        self.ui_effects.update()
        self.ui_animation_time += 1
        
    def draw_menu(self):
        # Dessiner le fond
        self.screen.fill(BLACK)
        self.parallax_background.draw(self.screen)
        
        # Dessiner les particules
        self.particle_system.draw(self.screen)
        
        # Dessiner le titre
        title_font = pygame.font.SysFont("Arial", 48)
        title_text = self.ui_effects.create_neon_text("Labyrinthe Amélioré", title_font, WHITE, (0, 100, 255), 10)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Dessiner les boutons
        for button in self.menu_buttons:
            # Créer le bouton avec un effet de survol
            if button["hover"]:
                # Couleurs plus vives pour l'effet de survol
                color1 = tuple(min(255, c + 30) for c in button["color1"])
                color2 = tuple(min(255, c + 30) for c in button["color2"])
                button_surface = self.ui_effects.create_gradient_button(
                    button["rect"].width, button["rect"].height, color1, color2)
            else:
                button_surface = self.ui_effects.create_gradient_button(
                    button["rect"].width, button["rect"].height, button["color1"], button["color2"])
                
            self.screen.blit(button_surface, button["rect"].topleft)
            
            # Dessiner le texte du bouton
            text_surface = self.font.render(button["text"], True, WHITE)
            text_x = button["rect"].centerx - text_surface.get_width() // 2
            text_y = button["rect"].centery - text_surface.get_height() // 2
            self.screen.blit(text_surface, (text_x, text_y))
            
        # Dessiner la version
        version_text = self.small_font.render("Version 2.0", True, (150, 150, 150))
        self.screen.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 10, SCREEN_HEIGHT - version_text.get_height() - 10))
        
    def draw_game(self):
        # Dessiner le fond
        self.screen.fill(BLACK)
        self.parallax_background.draw(self.screen)
        
        # Dessiner la grille
        self.draw_map()
        
        # Dessiner les particules
        self.particle_system.draw(self.screen)
        
        # Dessiner l'interface
        self.draw_game_ui()
        
        # Dessiner la minimap si activée
        if self.show_minimap:
            self.draw_minimap()
            
    def draw_map(self):
        # Calculer les limites visibles de la grille
        min_col = max(0, int(self.camera_x / (BLOCK_SIZE + BLOCK_GAP)) - 1)
        max_col = min(self.cols, min_col + SCREEN_WIDTH // (BLOCK_SIZE + BLOCK_GAP) + 2)
        min_row = max(0, int(self.camera_y / (BLOCK_SIZE + BLOCK_GAP)) - 1)
        max_row = min(self.rows, min_row + SCREEN_HEIGHT // (BLOCK_SIZE + BLOCK_GAP) + 2)
        
        # Dessiner seulement les cellules visibles
        for y in range(min_row, max_row):
            for x in range(min_col, max_col):
                cell_x = x * (BLOCK_SIZE + BLOCK_GAP) - int(self.camera_x) + MAP_PADDING
                cell_y = y * (BLOCK_SIZE + BLOCK_GAP) - int(self.camera_y) + MAP_PADDING
                
                if self.grid[y][x] == 1:  # Mur
                    wall_color = (100, 100, 100)
                    
                    # Créer un effet de profondeur
                    pygame.draw.rect(self.screen, (50, 50, 50), 
                                    (cell_x + 2, cell_y + 2, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, wall_color, 
                                    (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE))
                    
                    # Ajouter un effet de bord
                    pygame.draw.line(self.screen, (150, 150, 150), 
                                    (cell_x, cell_y), (cell_x + BLOCK_SIZE, cell_y))
                    pygame.draw.line(self.screen, (150, 150, 150), 
                                    (cell_x, cell_y), (cell_x, cell_y + BLOCK_SIZE))
                    pygame.draw.line(self.screen, (50, 50, 50), 
                                    (cell_x + BLOCK_SIZE, cell_y), (cell_x + BLOCK_SIZE, cell_y + BLOCK_SIZE))
                    pygame.draw.line(self.screen, (50, 50, 50), 
                                    (cell_x, cell_y + BLOCK_SIZE), (cell_x + BLOCK_SIZE, cell_y + BLOCK_SIZE))
                    
                elif self.grid[y][x] == 2:  # Fin
                    # Dessiner un portail animé
                    center_x = cell_x + BLOCK_SIZE // 2
                    center_y = cell_y + BLOCK_SIZE // 2
                    
                    # Animation de pulsation
                    pulse = math.sin(self.ui_animation_time * 0.1) * 0.2 + 0.8
                    radius = int(BLOCK_SIZE // 2 * pulse)
                    
                    # Dessiner plusieurs cercles concentriques
                    for i in range(3):
                        r = radius - i * 3
                        if r > 0:
                            color = (0, 255 - i * 50, 0)
                            pygame.draw.circle(self.screen, color, (center_x, center_y), r)
                            
                    # Ajouter un effet de lueur
                    glow_surface = pygame.Surface((BLOCK_SIZE * 2, BLOCK_SIZE * 2), pygame.SRCALPHA)
                    for r in range(radius, radius + 10):
                        alpha = 100 - (r - radius) * 10
                        if alpha > 0:
                            pygame.draw.circle(glow_surface, (0, 255, 0, alpha), 
                                            (BLOCK_SIZE, BLOCK_SIZE), r)
                    
                    self.screen.blit(glow_surface, 
                                    (center_x - BLOCK_SIZE, center_y - BLOCK_SIZE))
                    
                elif self.grid[y][x] == 3:  # Power-up
                    # Dessiner un power-up animé
                    center_x = cell_x + BLOCK_SIZE // 2
                    center_y = cell_y + BLOCK_SIZE // 2
                    
                    # Animation de rotation
                    angle = self.ui_animation_time * 5
                    size = BLOCK_SIZE // 3
                    
                    # Dessiner une étoile
                    points = []
                    for i in range(5):
                        # Point extérieur
                        a = math.radians(angle + i * 72)
                        x = center_x + math.cos(a) * size
                        y = center_y + math.sin(a) * size
                        points.append((x, y))
                        
                        # Point intérieur
                        a = math.radians(angle + i * 72 + 36)
                        x = center_x + math.cos(a) * (size // 2)
                        y = center_y + math.sin(a) * (size // 2)
                        points.append((x, y))
                        
                    pygame.draw.polygon(self.screen, YELLOW, points)
                    
                    # Ajouter un effet de lueur
                    glow_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                    for r in range(size, size + 5):
                        alpha = 100 - (r - size) * 20
                        if alpha > 0:
                            pygame.draw.circle(glow_surface, (255, 255, 0, alpha), 
                                            (BLOCK_SIZE // 2, BLOCK_SIZE // 2), r)
                    
                    self.screen.blit(glow_surface, 
                                    (center_x - BLOCK_SIZE // 2, center_y - BLOCK_SIZE // 2))
                    
        # Dessiner le personnage
        char_x = self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - int(self.camera_x) + MAP_PADDING
        char_y = self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - int(self.camera_y) + MAP_PADDING
        
        # Dessiner un personnage plus élaboré
        center_x = char_x + BLOCK_SIZE // 2
        center_y = char_y + BLOCK_SIZE // 2
        radius = BLOCK_SIZE // 3
        
        # Corps principal
        pygame.draw.circle(self.screen, (255, 100, 100), (center_x, center_y), radius)
        
        # Yeux
        eye_offset = radius // 3
        eye_size = radius // 4
        pygame.draw.circle(self.screen, WHITE, (center_x - eye_offset, center_y - eye_offset), eye_size)
        pygame.draw.circle(self.screen, WHITE, (center_x + eye_offset, center_y - eye_offset), eye_size)
        
        # Pupilles
        pupil_size = eye_size // 2
        pygame.draw.circle(self.screen, BLACK, (center_x - eye_offset, center_y - eye_offset), pupil_size)
        pygame.draw.circle(self.screen, BLACK, (center_x + eye_offset, center_y - eye_offset), pupil_size)
        
        # Bouche
        mouth_y = center_y + eye_offset
        pygame.draw.arc(self.screen, BLACK, 
                        (center_x - radius // 2, mouth_y - radius // 2, radius, radius // 2),
                        0, math.pi, 2)
        
        # Ajouter un effet de lueur
        glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        for r in range(radius, radius * 2):
            alpha = 100 - (r - radius) * (100 // radius)
            if alpha > 0:
                pygame.draw.circle(glow_surface, (255, 100, 100, alpha), 
                                (radius * 2, radius * 2), r)
        
        self.screen.blit(glow_surface, 
                        (center_x - radius * 2, center_y - radius * 2))
        
    def draw_game_ui(self):
        # Créer un panneau pour les informations
        panel = self.ui_effects.create_glass_panel(SCREEN_WIDTH - 20, 60, (0, 0, 0, 150), (100, 100, 255, 100), 2)
        self.screen.blit(panel, (10, 10))
        
        # Afficher le niveau
        level_text = self.ui_effects.create_neon_text(f"Niveau: {self.level}", self.font, WHITE, (0, 100, 255), 3)
        self.screen.blit(level_text, (20, 20))
        
        # Afficher le score
        score_text = self.ui_effects.create_neon_text(f"Score: {self.score}", self.font, WHITE, (0, 100, 255), 3)
        self.screen.blit(score_text, (150, 20))
        
        # Afficher le temps
        minutes = self.time_elapsed // 60000
        seconds = (self.time_elapsed % 60000) // 1000
        time_text = self.ui_effects.create_neon_text(f"Temps: {minutes:02}:{seconds:02}", self.font, WHITE, (0, 100, 255), 3)
        self.screen.blit(time_text, (300, 20))
        
        # Afficher les pas
        steps_text = self.ui_effects.create_neon_text(f"Pas: {self.steps}", self.font, WHITE, (0, 100, 255), 3)
        self.screen.blit(steps_text, (450, 20))
        
        # Afficher le FPS
        fps_text = self.small_font.render(self.fps_display, True, (150, 150, 150))
        self.screen.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 20, 25))
        
        # Afficher les notifications
        self.draw_notifications()
        
    def draw_minimap(self):
        # Créer la minimap
        minimap_width = 200
        minimap_height = 150
        
        # Calculer la zone visible
        visible_width = SCREEN_WIDTH // (BLOCK_SIZE + BLOCK_GAP)
        visible_height = SCREEN_HEIGHT // (BLOCK_SIZE + BLOCK_GAP)
        visible_x = int(self.camera_x / (BLOCK_SIZE + BLOCK_GAP))
        visible_y = int(self.camera_y / (BLOCK_SIZE + BLOCK_GAP))
        
        minimap = self.ui_effects.create_minimap(
            minimap_width, minimap_height, 
            self.character_pos, self.grid,
            (visible_x, visible_y, visible_width, visible_height)
        )
        
        # Positionner la minimap dans le coin inférieur droit
        self.screen.blit(minimap, (SCREEN_WIDTH - minimap_width - 20, SCREEN_HEIGHT - minimap_height - 20))
        
    def draw_pause_menu(self):
        # Assombrir l'écran de jeu
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Créer un panneau pour le menu de pause
        panel_width = 300
        panel_height = 250
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        panel = self.ui_effects.create_glass_panel(panel_width, panel_height, (0, 0, 0, 200), (100, 100, 255, 150), 2)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Titre du menu de pause
        title_text = self.ui_effects.create_neon_text("Pause", pygame.font.SysFont("Arial", 36), WHITE, (0, 100, 255), 5)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, panel_y + 20))
        
        # Dessiner les boutons
        for button in self.pause_buttons:
            # Créer le bouton avec un effet de survol
            if button["hover"]:
                # Couleurs plus vives pour l'effet de survol
                color1 = tuple(min(255, c + 30) for c in button["color1"])
                color2 = tuple(min(255, c + 30) for c in button["color2"])
                button_surface = self.ui_effects.create_gradient_button(
                    button["rect"].width, button["rect"].height, color1, color2)
            else:
                button_surface = self.ui_effects.create_gradient_button(
                    button["rect"].width, button["rect"].height, button["color1"], button["color2"])
                
            self.screen.blit(button_surface, button["rect"].topleft)
            
            # Dessiner le texte du bouton
            text_surface = self.font.render(button["text"], True, WHITE)
            text_x = button["rect"].centerx - text_surface.get_width() // 2
            text_y = button["rect"].centery - text_surface.get_height() // 2
            self.screen.blit(text_surface, (text_x, text_y))
            
    def draw_high_scores(self):
        # Dessiner le fond
        self.screen.fill(BLACK)
        self.parallax_background.draw(self.screen)
        
        # Dessiner les particules
        self.particle_system.draw(self.screen)
        
        # Créer un panneau pour les scores
        panel_width = 500
        panel_height = 400
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        panel = self.ui_effects.create_glass_panel(panel_width, panel_height, (0, 0, 0, 200), (100, 100, 255, 150), 2)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Titre
        title_text = self.ui_effects.create_neon_text("Meilleurs Scores", pygame.font.SysFont("Arial", 36), WHITE, (0, 100, 255), 5)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, panel_y + 20))
        
        # Charger les scores depuis le fichier
        scores = []
        try:
            with open("scores.txt", "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 2:
                        name = parts[0]
                        score = int(parts[1])
                        scores.append((name, score))
        except:
            scores = [("Joueur 1", 5000), ("Joueur 2", 4500), ("Joueur 3", 4000)]
            
        # Trier les scores
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Afficher les scores
        y_offset = panel_y + 80
        for i, (name, score) in enumerate(scores[:10]):
            # Créer un effet différent pour le top 3
            if i < 3:
                color_schemes = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]  # Or, Argent, Bronze
                text = self.ui_effects.create_neon_text(f"{i+1}. {name}", self.font, WHITE, color_schemes[i], 3)
                score_text = self.ui_effects.create_neon_text(f"{score}", self.font, WHITE, color_schemes[i], 3)
            else:
                text = self.font.render(f"{i+1}. {name}", True, WHITE)
                score_text = self.font.render(f"{score}", True, WHITE)
                
            self.screen.blit(text, (panel_x + 30, y_offset))
            self.screen.blit(score_text, (panel_x + panel_width - 30 - score_text.get_width(), y_offset))
            
            y_offset += 30
            
        # Bouton retour
        back_button = self.ui_effects.create_gradient_button(100, 40, (41, 128, 185), (52, 152, 219))
        self.screen.blit(back_button, (20, 20))
        
        back_text = self.font.render("Retour", True, WHITE)
        self.screen.blit(back_text, (20 + 50 - back_text.get_width() // 2, 20 + 20 - back_text.get_height() // 2))
        
    def draw_settings(self):
        # Dessiner le fond
        self.screen.fill(BLACK)
        self.parallax_background.draw(self.screen)
        
        # Dessiner les particules
        self.particle_system.draw(self.screen)
        
        # Créer un panneau pour les paramètres
        panel_width = 500
        panel_height = 400
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        panel = self.ui_effects.create_glass_panel(panel_width, panel_height, (0, 0, 0, 200), (100, 100, 255, 150), 2)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Titre
        title_text = self.ui_effects.create_neon_text("Paramètres", pygame.font.SysFont("Arial", 36), WHITE, (0, 100, 255), 5)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, panel_y + 20))
        
        # Options de paramètres (factices pour l'instant)
        options = [
            "Musique: ON",
            "Effets sonores: ON",
            "Plein écran: OFF",
            "Difficulté: Normale",
            "Langue: Français"
        ]
        
        y_offset = panel_y + 80
        for option in options:
            option_text = self.font.render(option, True, WHITE)
            self.screen.blit(option_text, (panel_x + 30, y_offset))
            
            # Dessiner un bouton de bascule
            toggle_width = 60
            toggle_height = 30
            toggle_x = panel_x + panel_width - 30 - toggle_width
            toggle_y = y_offset
            
            # Fond du bouton
            pygame.draw.rect(self.screen, (50, 50, 50), 
                            (toggle_x, toggle_y, toggle_width, toggle_height), 
                            border_radius=toggle_height // 2)
            
            # État du bouton (ON/OFF)
            if "ON" in option:
                # Bouton activé
                pygame.draw.rect(self.screen, (52, 152, 219), 
                                (toggle_x, toggle_y, toggle_width, toggle_height), 
                                border_radius=toggle_height // 2)
                
                # Cercle de l'interrupteur
                pygame.draw.circle(self.screen, WHITE, 
                                (toggle_x + toggle_width - toggle_height // 2, toggle_y + toggle_height // 2), 
                                toggle_height // 2 - 2)
            else:
                # Cercle de l'interrupteur
                pygame.draw.circle(self.screen, WHITE, 
                                (toggle_x + toggle_height // 2, toggle_y + toggle_height // 2), 
                                toggle_height // 2 - 2)
                
            y_offset += 50
            
        # Bouton retour
        back_button = self.ui_effects.create_gradient_button(100, 40, (41, 128, 185), (52, 152, 219))
        self.screen.blit(back_button, (20, 20))
        
        back_text = self.font.render("Retour", True, WHITE)
        self.screen.blit(back_text, (20 + 50 - back_text.get_width() // 2, 20 + 20 - back_text.get_height() // 2))
        
    def draw_notifications(self):
        current_time = pygame.time.get_ticks()
        y_offset = 80
        
        # Mettre à jour et dessiner les notifications
        for notification in self.notifications[:]:
            elapsed = current_time - notification["start_time"]
            
            if elapsed > notification["duration"]:
                self.notifications.remove(notification)
                continue
                
            # Calculer l'opacité en fonction du temps écoulé
            if elapsed < 500:  # Apparition
                alpha = elapsed / 500
            elif elapsed > notification["duration"] - 500:  # Disparition
                alpha = (notification["duration"] - elapsed) / 500
            else:  # Pleine opacité
                alpha = 1.0
                
            # Créer le texte de la notification
            color_scheme = notification["color_scheme"]
            
            if color_scheme == "blue":
                glow_color = (0, 100, 255)
            elif color_scheme == "green":
                glow_color = (0, 255, 100)
            elif color_scheme == "red":
                glow_color = (255, 50, 50)
            elif color_scheme == "yellow":
                glow_color = (255, 255, 0)
            else:
                glow_color = (100, 100, 255)
                
            text_surface = self.ui_effects.create_neon_text(notification["text"], self.font, WHITE, glow_color, 3)
            
            # Appliquer l'opacité
            text_surface.set_alpha(int(255 * alpha))
            
            # Centrer et dessiner la notification
            x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
            self.screen.blit(text_surface, (x, y_offset))
            
            y_offset += text_surface.get_height() + 10
            
    def draw_achievement_popup(self):
        if not self.achievements_popup:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.achievements_popup["start_time"]
        
        if elapsed > self.achievements_popup["duration"]:
            self.achievements_popup = None
            return
            
        # Calculer l'opacité et la position en fonction du temps écoulé
        if elapsed < 500:  # Apparition
            alpha = elapsed / 500
            offset_y = (1 - alpha) * 100
        elif elapsed > self.achievements_popup["duration"] - 500:  # Disparition
            alpha = (self.achievements_popup["duration"] - elapsed) / 500
            offset_y = 0
        else:  # Pleine opacité
            alpha = 1.0
            offset_y = 0
            
        # Créer le panneau de l'accomplissement
        panel_width = 300
        panel_height = 100
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = 100 + offset_y
        
        panel = self.ui_effects.create_glass_panel(panel_width, panel_height, (0, 0, 0, int(200 * alpha)), (255, 215, 0, int(200 * alpha)), 2)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Dessiner l'icône
        icon_type = self.achievements_popup["icon_type"]
        icon = self.ui_effects.create_animated_icon(icon_type, 50, (255, 215, 0))
        icon.set_alpha(int(255 * alpha))
        self.screen.blit(icon, (panel_x + 25, panel_y + panel_height // 2 - 25))
        
        # Dessiner le titre
        title_font = pygame.font.SysFont("Arial", 24)
        title_text = title_font.render(self.achievements_popup["title"], True, (255, 215, 0))
        title_text.set_alpha(int(255 * alpha))
        self.screen.blit(title_text, (panel_x + 90, panel_y + 20))
        
        # Dessiner la description
        desc_font = pygame.font.SysFont("Arial", 18)
        desc_text = desc_font.render(self.achievements_popup["description"], True, WHITE)
        desc_text.set_alpha(int(255 * alpha))
        self.screen.blit(desc_text, (panel_x + 90, panel_y + 50))
        
    def draw_tooltip(self):
        if not self.active_tooltip:
            return
            
        # Créer le tooltip
        tooltip = self.ui_effects.create_tooltip(
            self.active_tooltip["text"], 
            self.small_font, 
            self.active_tooltip["width"]
        )
        
        # Positionner le tooltip
        x = self.active_tooltip["x"]
        y = self.active_tooltip["y"]
        
        # Ajuster la position pour qu'il reste dans l'écran
        if x + tooltip.get_width() > SCREEN_WIDTH:
            x = SCREEN_WIDTH - tooltip.get_width() - 5
        if y + tooltip.get_height() > SCREEN_HEIGHT:
            y = SCREEN_HEIGHT - tooltip.get_height() - 5
            
        self.screen.blit(tooltip, (x, y))
        
    def draw_debug_info(self):
        debug_info = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"Particules: {self.particle_system.get_particle_count()}",
            f"Position: {self.character_pos}",
            f"Caméra: ({int(self.camera_x)}, {int(self.camera_y)})",
            f"État: {self.state}"
        ]
        
        # Créer un panneau pour les infos de débogage
        panel_width = 200
        panel_height = len(debug_info) * 20 + 10
        panel = self.ui_effects.create_glass_panel(panel_width, panel_height, (0, 0, 0, 150), (255, 255, 255, 50), 1)
        self.screen.blit(panel, (5, 5))
        
        # Afficher les infos
        for i, info in enumerate(debug_info):
            text = self.small_font.render(info, True, WHITE)
            self.screen.blit(text, (10, 10 + i * 20))
            
    def run(self):
        # Variable pour le mode débogage
        global debug_mode
        debug_mode = False
        
        running = True
        while running:
            # Calculer et lisser le FPS
            current_time = pygame.time.get_ticks()
            current_fps = self.clock.get_fps()
            
            # Mettre à jour les valeurs FPS pour le lissage
            self.fps_values.append(current_fps)
            if len(self.fps_values) > 10:
                self.fps_values.pop(0)
                
            # Mettre à jour l'affichage FPS moins fréquemment
            if current_time - self.last_fps_update > self.fps_update_interval:
                avg_fps = sum(self.fps_values) / len(self.fps_values) if self.fps_values else 0
                self.fps_display = f"FPS: {avg_fps:.1f}"
                self.last_fps_update = current_time
                
            # Gérer les événements
            self.handle_events()
            
            # Mettre à jour l'état du jeu
            if self.state == "menu":
                self.update_menu()
                self.draw_menu()
            elif self.state == "playing":
                self.update_game()
                self.draw_game()
            elif self.state == "paused":
                self.draw_pause_menu()
            elif self.state == "high_scores":
                self.draw_high_scores()
            elif self.state == "settings":
                self.draw_settings()
                
            # Dessiner les notifications au-dessus de tout
            self.draw_notifications()
            
            # Dessiner la popup de succès si active
            if self.achievements_popup:
                self.draw_achievement_popup()
                
            # Dessiner l'infobulle active si présente
            if self.active_tooltip:
                self.draw_tooltip()
                
            # Dessiner les infos de débogage si activées
            if debug_mode:
                self.draw_debug_info()
                
            # Mettre à jour l'affichage
            pygame.display.flip()
            
            # Limiter la fréquence d'images
            self.clock.tick(60)
            
            # Incrémenter le compteur de frames
            self.frame_counter += 1
            if self.frame_counter > 1000:
                self.frame_counter = 0

# Fonction principale
def main():
    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()

import pygame
import random
import math
import sys
from ui_enhancements import UIEffects
from modern_background_optimized import EnhancedParallaxBackground
from particle_system_optimized import ParticleSystem
from settings import *
from game_logic import generate_map, draw_map, load_character_skins, load_bonus_image, check_achievements, apply_weather_effects
from score_manager import ScoreManager
from sound_manager import SoundManager
import menu

# Initialize Pygame
pygame.init()

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Blocks Game")

# Initialize managers
score_manager = ScoreManager()
sound_manager = SoundManager()
ui_effects = UIEffects(SCREEN_WIDTH, SCREEN_HEIGHT)

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
    elif sound_name == "powerup":
        # Ajout d'un son pour les power-ups
        self.play_victory()
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
        self.achievements_popup = None
        self.achievement_popup_time = 0
        
        # Load fonts
        self.fonts = load_custom_fonts()
        
        # Initialize enhanced parallax background
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
        
        # Optimisations
        self.last_fps_update = 0
        self.fps_update_interval = 500  # Mettre à jour l'affichage FPS toutes les 500ms
        self.fps_display = "FPS: 0.0"
        self.ui_elements_cache = {}
        
        # Tooltips
        self.active_tooltip = None
        self.tooltip_timer = 0
        
        # Minimap
        self.show_minimap = True
        self.minimap_toggle_time = 0
        
        # UI animations
        self.ui_animation_time = 0
        
    def setup_menu_buttons(self):
        # Create menu buttons with enhanced UI
        button_width = 300
        button_height = 70
        button_spacing = 20
        start_y = SCREEN_HEIGHT // 2 - 100
        
        # Utiliser des couleurs différentes pour chaque bouton
        self.start_btn = {
            "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height),
            "text": "Start Game",
            "color_scheme": "green",
            "hover": False,
            "pressed": False,
            "action": self.start_game
        }
        
        self.scores_btn = {
            "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height),
            "text": "High Scores",
            "color_scheme": "blue",
            "hover": False,
            "pressed": False,
            "action": self.show_high_scores
        }
        
        self.settings_btn = {
            "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height),
            "text": "Settings",
            "color_scheme": "purple",
            "hover": False,
            "pressed": False,
            "action": self.show_settings
        }
        
        self.exit_btn = {
            "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + button_spacing), button_width, button_height),
            "text": "Exit",
            "color_scheme": "red",
            "hover": False,
            "pressed": False,
            "action": self.exit_game
        }
        
        self.menu_buttons = [self.start_btn, self.scores_btn, self.settings_btn, self.exit_btn]
    
    def setup_pause_buttons(self):
        # Create pause menu buttons with enhanced UI
        button_width = 300
        button_height = 70
        button_spacing = 20
        start_y = SCREEN_HEIGHT // 2 - 150
        
        self.resume_btn = {
            "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height),
            "text": "Resume",
            "color_scheme": "green",
            "hover": False,
            "pressed": False,
            "action": self.resume_game
        }
        
        self.restart_btn = {
            "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height),
            "text": "Restart",
            "color_scheme": "blue",
            "hover": False,
            "pressed": False,
            "action": self.restart_game
        }
        
        self.menu_btn = {
            "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height),
            "text": "Main Menu",
            "color_scheme": "purple",
            "hover": False,
            "pressed": False,
            "action": self.return_to_menu
        }
        
        self.exit_btn = {
            "rect": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + button_spacing), button_width, button_height),
            "text": "Exit",
            "color_scheme": "red",
            "hover": False,
            "pressed": False,
            "action": self.exit_game
        }
        
        self.pause_buttons = [self.resume_btn, self.restart_btn, self.menu_btn, self.exit_btn]

    def add_notification(self, text, duration=3000, color_scheme="blue"):
        # Limiter le nombre de notifications
        if len(self.notifications) >= 5:
            self.notifications.pop(0)
        self.notifications.append({
            "text": text,
            "duration": duration,
            "color_scheme": color_scheme,
            "creation_time": pygame.time.get_ticks(),
            "alpha": 0,
            "target_alpha": 255,
            "surface": None
        })

    def show_achievement_popup(self, title, description):
        self.achievements_popup = {
            "title": title,
            "description": description,
            "creation_time": pygame.time.get_ticks(),
            "duration": 5000,
            "surface": None,
            "alpha": 0,
            "target_alpha": 255
        }
        self.achievement_popup_time = pygame.time.get_ticks()

    def start_game(self):
        self.state = GameState.PLAYING
        self.setup_game()
        sound_manager.play_game_theme()
        self.add_notification("Game Started! Good luck!", 3000, "green")

    def show_high_scores(self):
        # Utiliser la fonctionnalité des meilleurs scores du menu
        menu.display_high_scores()

    def show_settings(self):
        # Utiliser la fonctionnalité des paramètres du menu
        menu.display_settings()

    def exit_game(self):
        pygame.event.clear()  # Effacer les événements en attente
        pygame.quit()
        sys.exit()

    def resume_game(self):
        self.state = GameState.PLAYING
        sound_manager.play_sound("unpause")

    def restart_game(self):
        self.setup_game()
        self.state = GameState.PLAYING
        sound_manager.play_game_theme()
        self.add_notification("Game Restarted!", 3000, "blue")

    def return_to_menu(self):
        self.state = GameState.MENU
        sound_manager.play_menu_theme()

    def run(self):
        running = True
        while running:
            # Calculer et lisser le FPS
            current_time = pygame.time.get_ticks()
            current_fps = self.clock.get_fps()
            
            # Mettre à jour les valeurs FPS pour le lissage
            self.fps_values.append(current_fps)
            if len(self.fps_values) > 10:  # Garder seulement les 10 dernières valeurs
                self.fps_values.pop(0)
                
            # Mettre à jour l'affichage FPS moins fréquemment
            if current_time - self.last_fps_update > self.fps_update_interval:
                avg_fps = sum(self.fps_values) / len(self.fps_values) if self.fps_values else 0
                self.fps_display = f"FPS: {avg_fps:.1f}"
                self.last_fps_update = current_time
            
            # Mettre à jour les effets d'interface utilisateur
            ui_effects.update()
            self.ui_animation_time += 1
            
            # Traiter les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.event.clear()  # Effacer les événements en attente
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                        sound_manager.play_sound("pause")
                    elif event.key == pygame.K_ESCAPE and self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                        sound_manager.play_sound("unpause")
                    # Mode debug toggle
                    elif event.key == pygame.K_F3:
                        global debug_mode
                        debug_mode = not debug_mode
                        self.add_notification(f"Debug mode: {'ON' if debug_mode else 'OFF'}", 2000, "purple")
                    # Toggle minimap
                    elif event.key == pygame.K_m and self.state == GameState.PLAYING:
                        if pygame.time.get_ticks() - self.minimap_toggle_time > 500:  # Éviter les doubles clics
                            self.show_minimap = not self.show_minimap
                            self.minimap_toggle_time = pygame.time.get_ticks()
                            self.add_notification(f"Minimap: {'ON' if self.show_minimap else 'OFF'}", 2000, "blue")

                if self.state == GameState.MENU:
                    self.handle_menu_events(event)
                elif self.state == GameState.PLAYING:
                    self.handle_game_events(event)
                elif self.state == GameState.PAUSED:
                    self.handle_pause_events(event)
                elif self.state == GameState.GAME_OVER:
                    self.handle_game_over_events(event)
            
            # Mettre à jour l'état du jeu
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
    
    def handle_menu_events(self, event):
        # Gérer les événements du menu
        mouse_pos = pygame.mouse.get_pos()
        
        # Mettre à jour l'état de survol des boutons
        for button in self.menu_buttons:
            button["hover"] = button["rect"].collidepoint(mouse_pos)
            
            # Vérifier les clics
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button["hover"]:
                    button["pressed"] = True
                    
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if button["pressed"] and button["hover"]:
                    # Exécuter l'action du bouton
                    button["action"]()
                    sound_manager.play_sound("menu_move")
                button["pressed"] = False
                
        # Vérifier si une infobulle doit être affichée
        self.check_tooltips(mouse_pos)
    
    def handle_game_events(self, event):
        # Gérer les entrées du jeu
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
                
                # Vérifier si le mouvement est valide - s'assurer qu'on ne peut pas traverser les rochers (valeur 1)
                if (0 <= new_pos[0] < self.cols and 
                    0 <= new_pos[1] < self.rows and 
                    self.grid[new_pos[1]][new_pos[0]] == 0):  # Autoriser le mouvement uniquement sur les espaces vides (0)
                    
                    self.character_pos = new_pos
                    self.steps += 1
                    self.move_cooldown = self.default_move_cooldown
                    
                    # Ajouter des particules de mouvement
                    self.particle_system.add_movement_particles(
                        self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING,
                        self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING,
                        5  # Réduire le nombre de particules
                    )
                    
                    # Vérifier les power-ups
                    self.check_powerups()
                    
                    # Vérifier si on a atteint la fin
                    if self.character_pos[0] == self.end_pos[0] and self.character_pos[1] == self.end_pos[1]:
                        self.level_complete()
    
    def handle_pause_events(self, event):
        # Gérer les événements du menu de pause
        mouse_pos = pygame.mouse.get_pos()
        
        # Mettre à jour l'état de survol des boutons
        for button in self.pause_buttons:
            button["hover"] = button["rect"].collidepoint(mouse_pos)
            
            # Vérifier les clics
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button["hover"]:
                    button["pressed"] = True
                    
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if button["pressed"] and button["hover"]:
                    # Exécuter l'action du bouton
                    button["action"]()
                    sound_manager.play_sound("menu_move")
                button["pressed"] = False
    
    def handle_game_over_events(self, event):
        # Gérer les événements de l'écran de fin de partie
        mouse_pos = pygame.mouse.get_pos()
        
        # Définir les boutons de l'écran de fin de partie
        restart_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 500, 300, 70)
        menu_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 590, 300, 70)
        
        # Vérifier les clics
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if restart_btn_rect.collidepoint(mouse_pos):
                self.restart_game()
            elif menu_btn_rect.collidepoint(mouse_pos):
                self.return_to_menu()
    
    def check_tooltips(self, mouse_pos):
        # Vérifier si le curseur est sur un élément qui nécessite une infobulle
        for button in self.menu_buttons:
            if button["hover"]:
                if self.tooltip_timer == 0:
                    self.tooltip_timer = pygame.time.get_ticks()
                elif pygame.time.get_ticks() - self.tooltip_timer > 500:  # Afficher après 500ms de survol
                    tooltip_text = ""
                    if button["text"] == "Start Game":
                        tooltip_text = "Commencer une nouvelle partie"
                    elif button["text"] == "High Scores":
                        tooltip_text = "Voir les meilleurs scores"
                    elif button["text"] == "Settings":
                        tooltip_text = "Modifier les paramètres du jeu"
                    elif button["text"] == "Exit":
                        tooltip_text = "Quitter le jeu"
                    
                    if tooltip_text:
                        self.active_tooltip = {
                            "text": tooltip_text,
                            "pos": (mouse_pos[0], mouse_pos[1] + 30)
                        }
                    return
        
        # Si on arrive ici, aucun élément n'est survolé
        self.tooltip_timer = 0
        self.active_tooltip = None
    
    def setup_game(self):
        # Réinitialiser les variables du jeu
        self.level = 1
        self.rows = 5
        self.cols = 5
        self.score = 0
        self.steps = 0
        self.coins_collected = 0
        self.level_time = LEVEL_TIME
        self.start_time = pygame.time.get_ticks()
        
        # Charger les images du personnage et des bonus
        character_skins = load_character_skins()
        self.character_image = random.choice(character_skins) if character_skins else None
        self.bonus_image = load_bonus_image()
        
        # Générer la carte
        self.grid, self.powerups, self.start_pos, self.end_pos, self.map_background = generate_map(self.rows, self.cols, self.level)
        self.character_pos = list(self.start_pos)
        
        # Réinitialiser la caméra
        self.camera_x = 0
        self.camera_y = 0
        
        # Réinitialiser le mouvement
        self.move_cooldown = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        
        # Réinitialiser la météo
        self.current_weather = random.choice(list(WEATHER.keys()))
        self.achievements_unlocked = []
        
        # Jouer le son de démarrage
        sound_manager.play_sound("level_start")
        
        # Réinitialiser les caches
        self.ui_elements_cache = {}
    
    def check_powerups(self):
        for powerup in self.powerups[:]:
            x, y, type = powerup
            if self.character_pos[0] == x and self.character_pos[1] == y:
                if type == POWERUP_SPEED:
                    self.speed_boost = True
                    self.speed_boost_timer = pygame.time.get_ticks() + SPEED_BOOST_DURATION
                    self.add_notification("Speed Boost activated!", 2000, "blue")
                    
                    # Ajouter des particules de boost de vitesse
                    self.particle_system.add_effect_particles(
                        self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING,
                        self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING,
                        15, (0, 150, 255)  # Réduire le nombre de particules
                    )
                    
                elif type == POWERUP_EXTRA_TIME:
                    self.level_time += 5
                    self.add_notification("+5 seconds added!", 2000, "green")
                    
                    # Ajouter des particules de boost de temps
                    self.particle_system.add_effect_particles(
                        self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING,
                        self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING,
                        15, (0, 255, 100)  # Réduire le nombre de particules
                    )
                    
                elif type == BONUS:
                    self.coins_collected += 1
                    self.score += 500
                    self.add_notification("+500 points!", 2000, "purple")
                    
                    # Ajouter des particules de pièce
                    self.particle_system.add_effect_particles(
                        self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_x + MAP_PADDING,
                        self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - self.camera_y + MAP_PADDING,
                        15, (255, 215, 0)  # Réduire le nombre de particules
                    )
                    
                self.powerups.remove(powerup)
                sound_manager.play_sound("powerup")
    
    def level_complete(self):
        # Mettre à jour le niveau
        self.level += 1
        
        # Calculer le bonus de temps restant
        remaining_time = max(0, self.level_time - (pygame.time.get_ticks() - self.start_time) // 1000)
        time_bonus = remaining_time * 100
        self.score += time_bonus
        
        # Ajouter un bonus de complétion de niveau
        level_bonus = self.level * 1000
        self.score += level_bonus
        
        # Mettre à jour le temps du niveau
        self.level_time = LEVEL_TIME + (self.level // 2)
        self.start_time = pygame.time.get_ticks()
        
        # Mettre à jour la taille de la grille
        if self.level % 2 == 0:
            self.cols += 1
        else:
            self.rows += 1
        
        # Générer une nouvelle carte
        self.grid, self.powerups, self.start_pos, self.end_pos, self.map_background = generate_map(self.rows, self.cols, self.level)
        self.character_pos = list(self.start_pos)
        
        # Réinitialiser la caméra
        self.camera_x = 0
        self.camera_y = 0
        
        # Réinitialiser le mouvement
        self.move_cooldown = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        
        # Mettre à jour la météo
        self.current_weather = random.choice(list(WEATHER.keys()))
        
        # Afficher la notification de complétion de niveau
        self.add_notification(f"Level {self.level-1} Complete! +{time_bonus + level_bonus} points", 3000, "green")
        
        # Afficher la popup de succès
        self.show_achievement_popup(f"Level {self.level-1} Complete!", f"You earned {time_bonus + level_bonus} points!")
        
        # Jouer le son de victoire
        sound_manager.play_sound("level_complete")
        
        # Ajouter des particules de complétion de niveau
        for _ in range(25):  # Réduire le nombre de particules
            self.particle_system.add_effect_particles(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                10, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
            
        # Réinitialiser les caches
        self.ui_elements_cache = {}
    
    def update_menu(self):
        # Mettre à jour les particules (optimisé)
        for i, particle in enumerate(self.particles):
            # Mettre à jour seulement une partie des particules à chaque frame
            if i % 3 == self.ui_animation_time % 3:
                particle["y"] += particle["speed"]
                if particle["y"] > SCREEN_HEIGHT:
                    particle["y"] = 0
                    particle["x"] = random.randint(0, SCREEN_WIDTH)
        
        # Mettre à jour les notifications
        self.update_notifications()
    
    def update_game(self):
        # Mettre à jour le cooldown de mouvement
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        
        # Mettre à jour le boost de vitesse
        if self.speed_boost and pygame.time.get_ticks() > self.speed_boost_timer:
            self.speed_boost = False
            self.add_notification("Speed Boost ended", 2000, "blue")
        
        # Appliquer les effets météo
        self.move_cooldown = apply_weather_effects(self.current_weather, self.move_cooldown)
        
        # Vérifier les nouveaux succès
        time_left = max(0, self.level_time - (pygame.time.get_ticks() - self.start_time) // 1000)
        new_achievements = check_achievements(self.level, time_left, self.steps, self.coins_collected)
        for achievement in new_achievements:
            if achievement not in self.achievements_unlocked:
                self.achievements_unlocked.append(achievement)
                self.add_notification(f"Achievement Unlocked: {achievement}", 3000, "purple")
                self.show_achievement_popup("Achievement Unlocked!", achievement)
        
        # Vérifier la fin de partie
        if time_left <= 0:
            self.state = GameState.GAME_OVER
            sound_manager.play_sound("game_over")
            
            # Sauvegarder le score
            score_manager.save_score(self.score, "Normal", self.level)
        
        # Mettre à jour le système de particules
        self.particle_system.update()
        
        # Mettre à jour les notifications
        self.update_notifications()
        
        # Mettre à jour le fond parallaxe amélioré
        self.enhanced_parallax.update(self.camera_x)

    def update_notifications(self):
        # Mettre à jour toutes les notifications
        current_time = pygame.time.get_ticks()
        
        # Mettre à jour les notifications
        i = 0
        while i < len(self.notifications):
            notification = self.notifications[i]
            time_passed = current_time - notification["creation_time"]
            
            # Vérifier si la notification a expiré
            if time_passed > notification["duration"]:
                notification["target_alpha"] = 0
            
            # Mettre à jour l'alpha avec une animation fluide
            if notification["alpha"] != notification["target_alpha"]:
                notification["alpha"] += (notification["target_alpha"] - notification["alpha"]) * 0.1
                notification["surface"] = None  # Réinitialiser la surface pour la recréer
            
            # Supprimer la notification si elle est complètement transparente
            if notification["alpha"] < 1 and notification["target_alpha"] == 0:
                self.notifications.pop(i)
            else:
                i += 1
        
        # Mettre à jour la popup de succès
        if self.achievements_popup:
            time_passed = current_time - self.achievements_popup["creation_time"]
            
            # Vérifier si la popup a expiré
            if time_passed > self.achievements_popup["duration"]:
                self.achievements_popup["target_alpha"] = 0
            
            # Mettre à jour l'alpha avec une animation fluide
            if self.achievements_popup["alpha"] != self.achievements_popup["target_alpha"]:
                self.achievements_popup["alpha"] += (self.achievements_popup["target_alpha"] - self.achievements_popup["alpha"]) * 0.1
                self.achievements_popup["surface"] = None  # Réinitialiser la surface pour la recréer
            
            # Supprimer la popup si elle est complètement transparente
            if self.achievements_popup["alpha"] < 1 and self.achievements_popup["target_alpha"] == 0:
                self.achievements_popup = None

    def draw_menu(self):
        # Dessiner l'arrière-plan animé
        menu_bg = ui_effects.create_animated_background(SCREEN_WIDTH, SCREEN_HEIGHT, "blue")
        self.screen.blit(menu_bg, (0, 0))
        
        # Dessiner les particules
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                particle["size"]
            )
        
        # Dessiner le titre avec effet néon
        title_text = ui_effects.create_neon_text(
            "Random Blocks Game",
            self.fonts['title'],
            (255, 255, 255),
            (41, 128, 185),
            10
        )
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Dessiner les boutons
        for button in self.menu_buttons:
            # Créer le bouton avec dégradé
            color1 = ui_effects.colors[button["color_scheme"]]
            color2 = ui_effects.colors[f"light_{button['color_scheme']}"]
            
            button_surface = ui_effects.create_gradient_button(
                button["rect"].width,
                button["rect"].height,
                color1,
                color2
            )
            
            # Ajouter le texte
            text_surface = self.fonts['button'].render(button["text"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(button["rect"].width // 2, button["rect"].height // 2))
            button_surface.blit(text_surface, text_rect)
            
            # Ajouter un effet de survol
            if button["hover"]:
                hover_effect, hover_pos = ui_effects.create_button_hover_effect(button["rect"], (255, 255, 255, 30))
                self.screen.blit(hover_effect, hover_pos)
                
                # Effet de pression
                if button["pressed"]:
                    button_surface.set_alpha(200)
            
            self.screen.blit(button_surface, button["rect"].topleft)
        
        # Dessiner les informations de version
        version_panel = ui_effects.create_glass_panel(150, 40, (0, 0, 0, 100))
        self.screen.blit(version_panel, (SCREEN_WIDTH - 170, SCREEN_HEIGHT - 60))
        
        version_text = self.fonts['small'].render("Version 2.0", True, (255, 255, 255))
        self.screen.blit(version_text, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 50))
    
    def draw_game(self):
        # Mettre à jour la caméra
        target_camera_x = self.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_WIDTH // 2
        target_camera_y = self.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - SCREEN_HEIGHT // 2
        self.camera_x += (target_camera_x - self.camera_x) * 0.1
        self.camera_y += (target_camera_y - self.camera_y) * 0.1
        
        # Dessiner le fond parallaxe amélioré
        self.enhanced_parallax.draw(self.screen)

        # Dessiner les éléments du jeu
        draw_map(
            self.screen, self.grid, self.powerups, self.camera_x, self.camera_y,
            self.start_pos, self.end_pos, self.character_pos,
            self.character_image, self.bonus_image, self.map_background
        )
        
        # Dessiner les effets de particules
        self.particle_system.draw(self.screen)
        
        # Dessiner l'interface utilisateur
        self.draw_game_ui()
        
        # Dessiner la mini-carte si activée
        if self.show_minimap:
            self.draw_minimap()
    
    def draw_game_ui(self):
        # Dessiner le panneau d'interface utilisateur
        ui_panel = ui_effects.create_glass_panel(250, 180, (0, 0, 0, 150), (255, 255, 255, 50), 2)
        self.screen.blit(ui_panel, (10, 10))
        
        # Dessiner les informations du jeu avec des icônes animées
        # Niveau
        level_icon = ui_effects.create_animated_icon("star", 24, (255, 215, 0))
        self.screen.blit(level_icon, (20, 20))
        level_text = self.fonts['info'].render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (50, 20))
        
        # Score
        score_icon = ui_effects.create_animated_icon("coin", 24, (255, 215, 0))
        self.screen.blit(score_icon, (20, 60))
        score_text = self.fonts['info'].render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (50, 60))
        
        # Temps
        time_icon = ui_effects.create_animated_icon("clock", 24, (255, 255, 255))
        self.screen.blit(time_icon, (20, 100))
        time_left = max(0, self.level_time - (pygame.time.get_ticks() - self.start_time) // 1000)
        time_text = self.fonts['info'].render(f"Time: {time_left}", True, (255, 255, 255))
        self.screen.blit(time_text, (50, 100))
        
        # Météo
        weather_text = self.fonts['info'].render(f"Weather: {self.current_weather.capitalize()}", True, (255, 255, 255))
        self.screen.blit(weather_text, (20, 140))
        
        # Dessiner la barre de progression du temps avec effet amélioré
        time_progress = ui_effects.create_progress_bar(
            200, 30, 
            time_left / self.level_time, 
            "green" if time_left > self.level_time // 2 else "red"
        )
        self.screen.blit(time_progress, (270, 20))
        
        # Texte de la barre de progression
        time_label = self.fonts['small'].render(f"Time: {time_left}/{self.level_time}", True, (255, 255, 255))
        self.screen.blit(time_label, (270 + (200 - time_label.get_width()) // 2, 20 + (30 - time_label.get_height()) // 2))
        
        # Dessiner l'indicateur de boost de vitesse si actif
        if self.speed_boost:
            boost_panel = ui_effects.create_glass_panel(200, 70, (0, 0, 150, 100), (0, 150, 255, 150), 2)
            self.screen.blit(boost_panel, (270, 60))
            
            boost_time_left = (self.speed_boost_timer - pygame.time.get_ticks()) // 1000
            boost_text = self.fonts['info'].render(f"Speed Boost: {boost_time_left}s", True, (255, 255, 255))
            self.screen.blit(boost_text, (280, 70))
            
            # Dessiner la barre de progression du boost
            boost_progress = ui_effects.create_progress_bar(
                180, 20, 
                boost_time_left / (SPEED_BOOST_DURATION // 1000), 
                "blue"
            )
            self.screen.blit(boost_progress, (280, 100))
        
        # Dessiner les succès si présents
        if self.achievements_unlocked:
            achievements_panel = ui_effects.create_glass_panel(
                SCREEN_WIDTH - 300, 40, 
                (0, 0, 0, 100), 
                (255, 215, 0, 150), 
                1
            )
            self.screen.blit(achievements_panel, (280, 140))
            
            achievements_text = self.fonts['small'].render(
                f"Achievements: {', '.join(self.achievements_unlocked)}", 
                True, 
                (255, 215, 0)
            )
            self.screen.blit(achievements_text, (290, 150))
    
    def draw_minimap(self):
        # Dessiner la mini-carte
        minimap_size = 150
        minimap = ui_effects.create_minimap(
            minimap_size, minimap_size,
            self.character_pos,
            self.grid,
            self.start_pos,
            self.end_pos,
            "blue"
        )
        self.screen.blit(minimap, (SCREEN_WIDTH - minimap_size - 20, 20))
    
    def draw_pause_menu(self):
        # D'abord dessiner le jeu en arrière-plan
        self.draw_game()
        
        # Dessiner la superposition
        overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 150))
        self.screen.blit(overlay_surface, (0, 0))
        
        # Dessiner le panneau de pause
        pause_panel = ui_effects.create_glass_panel(
            400, 450, 
            (0, 0, 0, 200), 
            (255, 255, 255, 100), 
            2,
            20
        )
        self.screen.blit(pause_panel, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 225))
        
        # Dessiner le titre de pause avec effet néon
        pause_text = ui_effects.create_neon_text(
            "Game Paused",
            self.fonts['heading'],
            (255, 255, 255),
            (100, 100, 255),
            8
        )
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 150))
        
        # Dessiner les boutons
        for button in self.pause_buttons:
            # Créer le bouton avec dégradé
            color1 = ui_effects.colors[button["color_scheme"]]
            color2 = ui_effects.colors[f"light_{button['color_scheme']}"]
            
            button_surface = ui_effects.create_gradient_button(
                button["rect"].width,
                button["rect"].height,
                color1,
                color2
            )
            
            # Ajouter le texte
            text_surface = self.fonts['button'].render(button["text"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(button["rect"].width // 2, button["rect"].height // 2))
            button_surface.blit(text_surface, text_rect)
            
            # Ajouter un effet de survol
            if button["hover"]:
                hover_effect, hover_pos = ui_effects.create_button_hover_effect(button["rect"], (255, 255, 255, 30))
                self.screen.blit(hover_effect, hover_pos)
                
                # Effet de pression
                if button["pressed"]:
                    button_surface.set_alpha(200)
            
            self.screen.blit(button_surface, button["rect"].topleft)
    
    def draw_game_over(self):
        # Dessiner l'arrière-plan avec alpha
        overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 200))
        self.screen.blit(overlay_surface, (0, 0))
        
        # Dessiner le panneau de fin de partie
        game_over_panel = ui_effects.create_glass_panel(
            500, 500, 
            (0, 0, 0, 200), 
            (255, 50, 50, 150), 
            2,
            20
        )
        self.screen.blit(game_over_panel, (SCREEN_WIDTH // 2 - 250, 100))
        
        # Dessiner le titre de fin de partie avec effet néon
        game_over_text = ui_effects.create_neon_text(
            "Game Over",
            self.fonts['title'],
            (255, 50, 50),
            (255, 0, 0),
            10
        )
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
        
        # Dessiner le score avec effet néon
        score_text = ui_effects.create_neon_text(
            f"Final Score: {self.score}",
            self.fonts['heading'],
            (255, 255, 255),
            (255, 215, 0),
            5
        )
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        
        # Dessiner les statistiques
        stats_y = 320
        stats_spacing = 40
        
        # Niveau atteint
        level_text = self.fonts['info'].render(f"Level Reached: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, stats_y))
        
        # Pièces collectées
        coins_text = self.fonts['info'].render(f"Coins Collected: {self.coins_collected}", True, (255, 255, 255))
        self.screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, stats_y + stats_spacing))
        
        # Pas effectués
        steps_text = self.fonts['info'].render(f"Steps Taken: {self.steps}", True, (255, 255, 255))
        self.screen.blit(steps_text, (SCREEN_WIDTH // 2 - steps_text.get_width() // 2, stats_y + 2 * stats_spacing))
        
        # Dessiner les succès
        if self.achievements_unlocked:
            achievements_text = self.fonts['info'].render(f"Achievements: {', '.join(self.achievements_unlocked)}", True, (255, 215, 0))
            self.screen.blit(achievements_text, (SCREEN_WIDTH // 2 - achievements_text.get_width() // 2, stats_y + 3 * stats_spacing))
        
        # Dessiner les boutons
        restart_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 500, 300, 70)
        menu_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 590, 300, 70)
        
        # Bouton de redémarrage
        restart_btn_surface = ui_effects.create_gradient_button(
            300, 70,
            ui_effects.colors["green"],
            ui_effects.colors["light_green"]
        )
        restart_text = self.fonts['button'].render("Play Again", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=(150, 35))
        restart_btn_surface.blit(restart_text, restart_text_rect)
        self.screen.blit(restart_btn_surface, restart_btn_rect.topleft)
        
        # Bouton de menu
        menu_btn_surface = ui_effects.create_gradient_button(
            300, 70,
            ui_effects.colors["blue"],
            ui_effects.colors["light_blue"]
        )
        menu_text = self.fonts['button'].render("Main Menu", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=(150, 35))
        menu_btn_surface.blit(menu_text, menu_text_rect)
        self.screen.blit(menu_btn_surface, menu_btn_rect.topleft)
        
        # Ajouter des effets de particules
        for _ in range(5):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.particle_system.add_effect_particles(
                x, y, 10, 
                (random.randint(200, 255), random.randint(0, 100), random.randint(0, 100))
            )
    
    def draw_notifications(self):
        # Dessiner toutes les notifications actives
        y_offset = 50
        for notification in self.notifications:
            # Créer ou récupérer la surface de notification
            if notification["surface"] is None or notification["alpha"] != int(notification["alpha"]):
                notification["surface"] = ui_effects.create_notification(
                    notification["text"],
                    self.fonts['info'],
                    notification["color_scheme"]
                )
                notification["surface"].set_alpha(int(notification["alpha"]))
            
            # Dessiner la notification
            self.screen.blit(
                notification["surface"], 
                (SCREEN_WIDTH // 2 - notification["surface"].get_width() // 2, y_offset)
            )
            y_offset += notification["surface"].get_height() + 10
    
    def draw_achievement_popup(self):
        # Dessiner la popup de succès si active
        if not self.achievements_popup:
            return
            
        # Créer ou récupérer la surface de popup
        if self.achievements_popup["surface"] is None or self.achievements_popup["alpha"] != int(self.achievements_popup["alpha"]):
            self.achievements_popup["surface"] = ui_effects.create_achievement_popup(
                self.achievements_popup["title"],
                self.achievements_popup["description"],
                self.fonts['info'],
                self.fonts['small'],
                "star",
                "gold"
            )
            self.achievements_popup["surface"].set_alpha(int(self.achievements_popup["alpha"]))
        
        # Dessiner la popup
        popup_x = SCREEN_WIDTH // 2 - self.achievements_popup["surface"].get_width() // 2
        popup_y = SCREEN_HEIGHT - self.achievements_popup["surface"].get_height() - 50
        
        # Animation de rebond
        time_passed = pygame.time.get_ticks() - self.achievements_popup["creation_time"]
        if time_passed < 500:
            # Animation d'entrée
            progress = time_passed / 500
            popup_y = SCREEN_HEIGHT + (popup_y - SCREEN_HEIGHT) * progress
        
        self.screen.blit(self.achievements_popup["surface"], (popup_x, popup_y))
    
    def draw_tooltip(self):
        # Dessiner l'infobulle active
        if not self.active_tooltip:
            return
            
        tooltip_surface = ui_effects.create_tooltip(
            self.active_tooltip["text"],
            self.fonts['small']
        )
        
        # Positionner l'infobulle
        tooltip_x = self.active_tooltip["pos"][0] - tooltip_surface.get_width() // 2
        tooltip_y = self.active_tooltip["pos"][1]
        
        # S'assurer que l'infobulle reste dans l'écran
        tooltip_x = max(10, min(SCREEN_WIDTH - tooltip_surface.get_width() - 10, tooltip_x))
        tooltip_y = max(10, min(SCREEN_HEIGHT - tooltip_surface.get_height() - 10, tooltip_y))
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_debug_info(self):
        # Créer le panneau de débogage
        debug_panel = ui_effects.create_glass_panel(210, 120, (0, 0, 0, 180), (255, 255, 255, 50), 1, 5)
        self.screen.blit(debug_panel, (SCREEN_WIDTH - 220, 10))
        
        # Dessiner le FPS (utiliser la valeur mise en cache)
        fps_text = self.fonts['small'].render(self.fps_display, True, (255, 255, 255))
        self.screen.blit(fps_text, (SCREEN_WIDTH - 200, 20))
        
        # Dessiner la position
        pos_text = self.fonts['small'].render(f"Pos: {self.character_pos}", True, (255, 255, 255))
        self.screen.blit(pos_text, (SCREEN_WIDTH - 200, 50))
        
        # Dessiner la taille de la grille
        grid_text = self.fonts['small'].render(f"Grid: {self.rows}x{self.cols}", True, (255, 255, 255))
        self.screen.blit(grid_text, (SCREEN_WIDTH - 200, 80))
        
        # Dessiner la position de la caméra
        camera_text = self.fonts['small'].render(f"Camera: {int(self.camera_x)},{int(self.camera_y)}", True, (255, 255, 255))
        self.screen.blit(camera_text, (SCREEN_WIDTH - 200, 110))

# Fonction principale
def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

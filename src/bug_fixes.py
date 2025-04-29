import pygame
import sys
import os

# Classe pour gérer la navigation entre les menus
class MenuNavigationManager:
    def __init__(self):
        self.menu_history = []
        self.current_menu = None
        self.transition_active = False
        self.transition_progress = 0
        self.transition_direction = 1  # 1 pour avant, -1 pour arrière
        self.transition_speed = 0.1
        self.transition_target = None
        
    def navigate_to(self, menu_name):
        """Naviguer vers un nouveau menu en ajoutant une transition fluide"""
        if self.current_menu:
            self.menu_history.append(self.current_menu)
        
        self.transition_active = True
        self.transition_progress = 0
        self.transition_direction = 1
        self.transition_target = menu_name
        
    def go_back(self):
        """Retourner au menu précédent avec une transition fluide"""
        if self.menu_history:
            self.transition_active = True
            self.transition_progress = 0
            self.transition_direction = -1
            self.transition_target = self.menu_history.pop()
            return True
        return False
        
    def update_transition(self):
        """Mettre à jour l'animation de transition"""
        if self.transition_active:
            self.transition_progress += self.transition_speed
            
            if self.transition_progress >= 1:
                self.transition_active = False
                self.current_menu = self.transition_target
                self.transition_progress = 0
                
        return self.transition_active, self.transition_progress, self.transition_direction
        
    def get_current_menu(self):
        """Obtenir le menu actuel"""
        return self.current_menu
        
    def clear_history(self):
        """Effacer l'historique de navigation"""
        self.menu_history = []

# Classe pour gérer les événements de manière plus robuste
class EventManager:
    def __init__(self):
        self.event_handlers = {}
        self.global_handlers = []
        
    def register_handler(self, event_type, handler, context=None):
        """Enregistrer un gestionnaire d'événements pour un type spécifique"""
        if context:
            key = (event_type, context)
        else:
            key = event_type
            
        if key not in self.event_handlers:
            self.event_handlers[key] = []
        self.event_handlers[key].append(handler)
        
    def register_global_handler(self, handler):
        """Enregistrer un gestionnaire global qui reçoit tous les événements"""
        self.global_handlers.append(handler)
        
    def process_events(self, context=None):
        """Traiter tous les événements en attente"""
        for event in pygame.event.get():
            # Traiter les gestionnaires globaux
            for handler in self.global_handlers:
                if handler(event):
                    break
                    
            # Traiter les gestionnaires spécifiques au contexte
            if context and (event.type, context) in self.event_handlers:
                for handler in self.event_handlers[(event.type, context)]:
                    if handler(event):
                        break
                        
            # Traiter les gestionnaires spécifiques au type
            if event.type in self.event_handlers:
                for handler in self.event_handlers[event.type]:
                    if handler(event):
                        break

# Classe pour gérer les ressources du jeu (images, sons, etc.)
class ResourceManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.cached_surfaces = {}
        
    def load_image(self, name, path, convert_alpha=True):
        """Charger une image et la stocker dans le cache"""
        try:
            if convert_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
            self.images[name] = image
            return image
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image {path}: {e}")
            # Créer une surface de remplacement
            surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(surface, (255, 0, 255), (0, 0, 64, 64), 1)
            pygame.draw.line(surface, (255, 0, 255), (0, 0), (64, 64), 1)
            pygame.draw.line(surface, (255, 0, 255), (0, 64), (64, 0), 1)
            self.images[name] = surface
            return surface
            
    def get_image(self, name):
        """Récupérer une image du cache"""
        return self.images.get(name)
        
    def load_sound(self, name, path):
        """Charger un son et le stocker dans le cache"""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"Erreur lors du chargement du son {path}: {e}")
            return None
            
    def get_sound(self, name):
        """Récupérer un son du cache"""
        return self.sounds.get(name)
        
    def load_font(self, name, path, size):
        """Charger une police et la stocker dans le cache"""
        try:
            if os.path.exists(path):
                font = pygame.font.Font(path, size)
            else:
                font = pygame.font.SysFont(path, size)
            self.fonts[(name, size)] = font
            return font
        except pygame.error as e:
            print(f"Erreur lors du chargement de la police {path}: {e}")
            font = pygame.font.SysFont('arial', size)
            self.fonts[(name, size)] = font
            return font
            
    def get_font(self, name, size):
        """Récupérer une police du cache"""
        if (name, size) in self.fonts:
            return self.fonts[(name, size)]
        else:
            # Essayer de charger la police système
            return self.load_font(name, name, size)
            
    def cache_surface(self, key, surface):
        """Stocker une surface dans le cache"""
        self.cached_surfaces[key] = surface
        
    def get_cached_surface(self, key):
        """Récupérer une surface du cache"""
        return self.cached_surfaces.get(key)
        
    def clear_cache(self):
        """Vider le cache de surfaces"""
        self.cached_surfaces.clear()

# Classe pour gérer les collisions de manière plus précise
class CollisionManager:
    def __init__(self):
        self.collision_groups = {}
        
    def register_object(self, obj, group_name):
        """Enregistrer un objet dans un groupe de collision"""
        if group_name not in self.collision_groups:
            self.collision_groups[group_name] = []
        self.collision_groups[group_name].append(obj)
        
    def unregister_object(self, obj, group_name):
        """Retirer un objet d'un groupe de collision"""
        if group_name in self.collision_groups:
            if obj in self.collision_groups[group_name]:
                self.collision_groups[group_name].remove(obj)
                
    def check_collision(self, obj, group_name):
        """Vérifier si un objet est en collision avec un groupe"""
        if group_name not in self.collision_groups:
            return []
            
        collisions = []
        for other in self.collision_groups[group_name]:
            if obj != other and self._objects_collide(obj, other):
                collisions.append(other)
                
        return collisions
        
    def _objects_collide(self, obj1, obj2):
        """Vérifier si deux objets sont en collision"""
        # Vérifier si les objets ont une méthode get_rect
        if hasattr(obj1, 'get_rect') and hasattr(obj2, 'get_rect'):
            return obj1.get_rect().colliderect(obj2.get_rect())
        # Vérifier si les objets ont un attribut rect
        elif hasattr(obj1, 'rect') and hasattr(obj2, 'rect'):
            return obj1.rect.colliderect(obj2.rect)
        # Vérifier si les objets sont des Rect
        elif isinstance(obj1, pygame.Rect) and isinstance(obj2, pygame.Rect):
            return obj1.colliderect(obj2)
        return False
        
    def clear_group(self, group_name):
        """Vider un groupe de collision"""
        if group_name in self.collision_groups:
            self.collision_groups[group_name] = []

# Classe pour gérer les erreurs et les exceptions
class ErrorHandler:
    def __init__(self):
        self.error_log = []
        self.max_log_size = 100
        
    def log_error(self, error_type, message, details=None):
        """Enregistrer une erreur dans le journal"""
        error = {
            'type': error_type,
            'message': message,
            'details': details,
            'time': pygame.time.get_ticks()
        }
        self.error_log.append(error)
        
        # Limiter la taille du journal
        if len(self.error_log) > self.max_log_size:
            self.error_log.pop(0)
            
        print(f"ERREUR [{error_type}]: {message}")
        if details:
            print(f"Détails: {details}")
            
    def get_recent_errors(self, count=10):
        """Récupérer les erreurs récentes"""
        return self.error_log[-count:] if len(self.error_log) > 0 else []
        
    def clear_log(self):
        """Vider le journal des erreurs"""
        self.error_log = []

# Fonction pour corriger les problèmes de navigation entre les menus
def fix_menu_navigation(game_instance):
    """
    Corrige les problèmes de navigation entre les menus en utilisant
    le gestionnaire de navigation des menus.
    """
    # Vérifier si le gestionnaire de navigation existe déjà
    if not hasattr(game_instance, 'menu_nav'):
        game_instance.menu_nav = MenuNavigationManager()
        
    # Remplacer les méthodes de navigation existantes
    original_start_game = game_instance.start_game
    original_show_high_scores = game_instance.show_high_scores
    original_show_settings = game_instance.show_settings
    original_return_to_menu = game_instance.return_to_menu
    
    def safe_start_game():
        try:
            game_instance.menu_nav.navigate_to('playing')
            original_start_game()
        except Exception as e:
            if hasattr(game_instance, 'error_handler'):
                game_instance.error_handler.log_error('Navigation', 'Erreur lors du démarrage du jeu', str(e))
            else:
                print(f"Erreur lors du démarrage du jeu: {e}")
    
    def safe_show_high_scores():
        try:
            game_instance.menu_nav.navigate_to('high_scores')
            original_show_high_scores()
        except Exception as e:
            if hasattr(game_instance, 'error_handler'):
                game_instance.error_handler.log_error('Navigation', 'Erreur lors de l\'affichage des scores', str(e))
            else:
                print(f"Erreur lors de l'affichage des scores: {e}")
    
    def safe_show_settings():
        try:
            game_instance.menu_nav.navigate_to('settings')
            original_show_settings()
        except Exception as e:
            if hasattr(game_instance, 'error_handler'):
                game_instance.error_handler.log_error('Navigation', 'Erreur lors de l\'affichage des paramètres', str(e))
            else:
                print(f"Erreur lors de l'affichage des paramètres: {e}")
    
    def safe_return_to_menu():
        try:
            game_instance.menu_nav.navigate_to('menu')
            game_instance.menu_nav.clear_history()
            original_return_to_menu()
        except Exception as e:
            if hasattr(game_instance, 'error_handler'):
                game_instance.error_handler.log_error('Navigation', 'Erreur lors du retour au menu', str(e))
            else:
                print(f"Erreur lors du retour au menu: {e}")
    
    # Remplacer les méthodes originales par les versions sécurisées
    game_instance.start_game = safe_start_game
    game_instance.show_high_scores = safe_show_high_scores
    game_instance.show_settings = safe_show_settings
    game_instance.return_to_menu = safe_return_to_menu
    
    # Ajouter une méthode pour gérer le bouton retour
    def handle_back_button():
        if game_instance.menu_nav.go_back():
            # Déterminer l'état en fonction du menu cible
            current_menu = game_instance.menu_nav.get_current_menu()
            if current_menu == 'menu':
                game_instance.state = 'menu'
            elif current_menu == 'playing':
                game_instance.state = 'playing'
            elif current_menu == 'high_scores':
                original_show_high_scores()
            elif current_menu == 'settings':
                original_show_settings()
    
    game_instance.handle_back_button = handle_back_button
    
    return game_instance

# Fonction pour corriger les problèmes de collision
def fix_collision_issues(game_instance):
    """
    Corrige les problèmes potentiels de collision en utilisant
    le gestionnaire de collisions.
    """
    # Vérifier si le gestionnaire de collisions existe déjà
    if not hasattr(game_instance, 'collision_manager'):
        game_instance.collision_manager = CollisionManager()
        
    # Remplacer la méthode de vérification des mouvements
    original_handle_game_events = game_instance.handle_game_events
    
    def enhanced_handle_game_events(event):
        if event.type == pygame.KEYDOWN:
            if game_instance.move_cooldown <= 0:
                new_pos = list(game_instance.character_pos)
                
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    new_pos[1] -= 1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    new_pos[1] += 1
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    new_pos[0] -= 1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    new_pos[0] += 1
                
                # Vérification améliorée des limites de la carte
                if (0 <= new_pos[0] < game_instance.cols and 
                    0 <= new_pos[1] < game_instance.rows):
                    
                    # Vérification améliorée des collisions
                    if game_instance.grid[new_pos[1]][new_pos[0]] == 0:  # Espace vide
                        game_instance.character_pos = new_pos
                        game_instance.steps += 1
                        game_instance.move_cooldown = game_instance.default_move_cooldown
                        
                        # Ajouter des particules de mouvement
                        game_instance.particle_system.add_movement_particles(
                            game_instance.character_pos[0] * (BLOCK_SIZE + BLOCK_GAP) - game_instance.camera_x + MAP_PADDING,
                            game_instance.character_pos[1] * (BLOCK_SIZE + BLOCK_GAP) - game_instance.camera_y + MAP_PADDING,
                            5
                        )
                        
                        # Vérifier les power-ups
                        game_instance.check_powerups()
                        
                        # Vérifier si on a atteint la fin
                        if game_instance.character_pos[0] == game_instance.end_pos[0] and game_instance.character_pos[1] == game_instance.end_pos[1]:
                            game_instance.level_complete()
        
        # Appeler la méthode originale pour les autres événements
        return original_handle_game_events(event)
    
    # Remplacer la méthode originale par la version améliorée
    game_instance.handle_game_events = enhanced_handle_game_events
    
    return game_instance

# Fonction pour corriger les erreurs dans la gestion des événements
def fix_event_handling(game_instance):
    """
    Corrige les erreurs dans la gestion des événements en utilisant
    le gestionnaire d'événements.
    """
    # Vérifier si le gestionnaire d'événements existe déjà
    if not hasattr(game_instance, 'event_manager'):
        game_instance.event_manager = EventManager()
        
    # Vérifier si le gestionnaire d'erreurs existe déjà
    if not hasattr(game_instance, 'error_handler'):
        game_instance.error_handler = ErrorHandler()
        
    # Enregistrer un gestionnaire global pour les événements de fermeture
    def handle_quit_event(event):
        if event.type == pygame.QUIT:
            pygame.event.clear()
            pygame.quit()
            sys.exit()
        return False
    
    game_instance.event_manager.register_global_handler(handle_quit_event)
    
    # Enregistrer des gestionnaires pour les événements de clavier
    def handle_keyboard_event(event):
        if event.type == pygame.KEYDOWN:
            # Gérer la touche Échap
            if event.key == pygame.K_ESCAPE:
                if game_instance.state == 'playing':
                    game_instance.state = 'paused'
                    if hasattr(game_instance, 'sound_manager'):
                        game_instance.sound_manager.play_sound("pause")
                    return True
                elif game_instance.state == 'paused':
                    game_instance.state = 'playing'
                    if hasattr(game_instance, 'sound_manager'):
                        game_instance.sound_manager.play_sound("unpause")
                    return True
            
            # Gérer la touche F3 (mode debug)
            elif event.key == pygame.K_F3:
                global debug_mode
                debug_mode = not debug_mode
                game_instance.add_notification(f"Debug mode: {'ON' if debug_mode else 'OFF'}", 2000, "purple")
                return True
                
            # Gérer la touche M (mini-carte)
            elif event.key == pygame.K_m and game_instance.state == 'playing':
                if pygame.time.get_ticks() - game_instance.minimap_toggle_time > 500:
                    game_instance.show_minimap = not game_instance.show_minimap
                    game_instance.minimap_toggle_time = pygame.time.get_ticks()
                    game_instance.add_notification(f"Minimap: {'ON' if game_instance.show_minimap else 'OFF'}", 2000, "blue")
                    return True
        
        return False
    
    game_instance.event_manager.register_handler(pygame.KEYDOWN, handle_keyboard_event)
    
    # Remplacer la méthode de traitement des événements
    original_run = game_instance.run
    
    def enhanced_run():
        running = True
        while running:
            try:
                # Calculer et lisser le FPS
                current_time = pygame.time.get_ticks()
                current_fps = game_instance.clock.get_fps()
                
                # Mettre à jour les valeurs FPS pour le lissage
                game_instance.fps_values.append(current_fps)
                if len(game_instance.fps_values) > 10:
                    game_instance.fps_values.pop(0)
                    
                # Mettre à jour l'affichage FPS moins fréquemment
                if current_time - game_instance.last_fps_update > game_instance.fps_update_interval:
                    avg_fps = sum(game_instance.fps_values) / len(game_instance.fps_values) if game_instance.fps_values else 0
                    game_instance.fps_display = f"FPS: {avg_fps:.1f}"
                    game_instance.last_fps_update = current_time
                
                # Mettre à jour les effets d'interface utilisateur
                if hasattr(game_instance, 'ui_effects'):
                    game_instance.ui_effects.update()
                game_instance.ui_animation_time += 1
                
                # Traiter les événements avec le gestionnaire d'événements
                context = game_instance.state
                game_instance.event_manager.process_events(context)
                
                # Mettre à jour l'état du jeu
                if game_instance.state == 'menu':
                    game_instance.update_menu()
                    game_instance.draw_menu()
                elif game_instance.state == 'playing':
                    game_instance.update_game()
                    game_instance.draw_game()
                elif game_instance.state == 'paused':
                    game_instance.draw_pause_menu()
                elif game_instance.state == 'game_over':
                    game_instance.draw_game_over()
                
                # Dessiner les notifications au-dessus de tout
                game_instance.draw_notifications()
                
                # Dessiner la popup de succès si active
                if hasattr(game_instance, 'achievements_popup') and game_instance.achievements_popup:
                    game_instance.draw_achievement_popup()
                
                # Dessiner l'infobulle active si présente
                if hasattr(game_instance, 'active_tooltip') and game_instance.active_tooltip:
                    game_instance.draw_tooltip()
                
                # Dessiner les infos de débogage si activées
                if debug_mode:
                    game_instance.draw_debug_info()
                
                # Mettre à jour l'affichage
                pygame.display.flip()
                
                # Limiter la fréquence d'images
                game_instance.clock.tick(60)
                
            except Exception as e:
                # Enregistrer l'erreur
                game_instance.error_handler.log_error('Runtime', 'Erreur pendant l\'exécution du jeu', str(e))
                
                # Afficher une notification d'erreur
                game_instance.add_notification(f"Erreur: {str(e)}", 5000, "red")
                
                # Continuer l'exécution
                continue
    
    # Remplacer la méthode originale par la version améliorée
    game_instance.run = enhanced_run
    
    return game_instance

# Fonction pour assurer la stabilité du jeu
def ensure_game_stability(game_instance):
    """
    Assure la stabilité du jeu en ajoutant des mécanismes de récupération
    et en corrigeant les problèmes potentiels.
    """
    # Vérifier si le gestionnaire de ressources existe déjà
    if not hasattr(game_instance, 'resource_manager'):
        game_instance.resource_manager = ResourceManager()
    
    # Ajouter une méthode de récupération en cas de crash
    def recover_from_crash():
        try:
            # Réinitialiser l'état du jeu
            game_instance.state = 'menu'
            
            # Réinitialiser les gestionnaires
            if hasattr(game_instance, 'menu_nav'):
                game_instance.menu_nav.clear_history()
                
            if hasattr(game_instance, 'collision_manager'):
                for group in list(game_instance.collision_manager.collision_groups.keys()):
                    game_instance.collision_manager.clear_group(group)
                    
            if hasattr(game_instance, 'resource_manager'):
                game_instance.resource_manager.clear_cache()
                
            # Afficher une notification
            game_instance.add_notification("Récupération après une erreur", 3000, "red")
            
            # Journaliser l'événement
            if hasattr(game_instance, 'error_handler'):
                game_instance.error_handler.log_error('Recovery', 'Récupération après un crash')
                
            return True
        except Exception as e:
            print(f"Erreur lors de la récupération: {e}")
            return False
    
    game_instance.recover_from_crash = recover_from_crash
    
    # Remplacer la méthode de configuration du jeu
    original_setup_game = game_instance.setup_game
    
    def safe_setup_game():
        try:
            original_setup_game()
        except Exception as e:
            if hasattr(game_instance, 'error_handler'):
                game_instance.error_handler.log_error('Setup', 'Erreur lors de la configuration du jeu', str(e))
            else:
                print(f"Erreur lors de la configuration du jeu: {e}")
                
            # Essayer de récupérer
            game_instance.recover_from_crash()
    
    # Remplacer la méthode originale par la version sécurisée
    game_instance.setup_game = safe_setup_game
    
    return game_instance

# Fonction principale pour appliquer toutes les corrections
def apply_bug_fixes(game_instance):
    """
    Applique toutes les corrections de bugs au jeu.
    """
    # Corriger les problèmes de navigation entre les menus
    game_instance = fix_menu_navigation(game_instance)
    
    # Corriger les problèmes de collision
    game_instance = fix_collision_issues(game_instance)
    
    # Corriger les erreurs dans la gestion des événements
    game_instance = fix_event_handling(game_instance)
    
    # Assurer la stabilité du jeu
    game_instance = ensure_game_stability(game_instance)
    
    return game_instance

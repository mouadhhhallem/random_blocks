import pygame
import sys
import os
import time
import importlib
import traceback

# Définir les couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialiser Pygame
pygame.init()

# Définir la taille de l'écran
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Test des améliorations du jeu")

# Charger les polices
font_large = pygame.font.SysFont('Arial', 36)
font_medium = pygame.font.SysFont('Arial', 24)
font_small = pygame.font.SysFont('Arial', 18)

# Classe pour les tests
class GameTester:
    def __init__(self):
        self.tests = []
        self.current_test = 0
        self.test_results = []
        self.running = True
        self.clock = pygame.time.Clock()
        self.log_messages = []
        
    def add_test(self, name, function, description):
        self.tests.append({
            'name': name,
            'function': function,
            'description': description
        })
        
    def log(self, message, color=WHITE):
        self.log_messages.append({
            'message': message,
            'color': color,
            'time': time.time()
        })
        print(message)
        
    def run_tests(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        if self.current_test < len(self.tests):
                            self.run_current_test()
                        else:
                            self.log("Tous les tests sont terminés.", GREEN)
                    elif event.key == pygame.K_r:
                        self.reset_tests()
                        
            self.draw_screen()
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        
    def run_current_test(self):
        if self.current_test < len(self.tests):
            test = self.tests[self.current_test]
            self.log(f"Exécution du test: {test['name']}...", BLUE)
            
            try:
                result = test['function']()
                if result:
                    self.log(f"Test réussi: {test['name']}", GREEN)
                    self.test_results.append(True)
                else:
                    self.log(f"Test échoué: {test['name']}", RED)
                    self.test_results.append(False)
            except Exception as e:
                self.log(f"Erreur lors du test {test['name']}: {str(e)}", RED)
                traceback.print_exc()
                self.test_results.append(False)
                
            self.current_test += 1
            
    def reset_tests(self):
        self.current_test = 0
        self.test_results = []
        self.log_messages = []
        self.log("Tests réinitialisés.", YELLOW)
        
    def draw_screen(self):
        screen.fill(BLACK)
        
        # Dessiner le titre
        title = font_large.render("Test des améliorations du jeu", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Dessiner les instructions
        instructions = font_small.render("Appuyez sur ESPACE pour exécuter le prochain test, R pour réinitialiser, ESC pour quitter", True, WHITE)
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 70))
        
        # Dessiner la liste des tests
        y_offset = 120
        for i, test in enumerate(self.tests):
            if i < self.current_test:
                if self.test_results[i]:
                    status = "✓"
                    color = GREEN
                else:
                    status = "✗"
                    color = RED
            elif i == self.current_test:
                status = "►"
                color = YELLOW
            else:
                status = " "
                color = WHITE
                
            test_text = font_medium.render(f"{status} {test['name']}", True, color)
            screen.blit(test_text, (50, y_offset))
            
            # Dessiner la description du test
            desc_text = font_small.render(test['description'], True, color)
            screen.blit(desc_text, (70, y_offset + 30))
            
            y_offset += 60
            
        # Dessiner le journal des messages
        log_y = SCREEN_HEIGHT - 200
        pygame.draw.rect(screen, (50, 50, 50), (10, log_y, SCREEN_WIDTH - 20, 180))
        pygame.draw.rect(screen, WHITE, (10, log_y, SCREEN_WIDTH - 20, 180), 1)
        
        log_title = font_medium.render("Journal des tests", True, WHITE)
        screen.blit(log_title, (20, log_y + 10))
        
        # Afficher les derniers messages du journal
        max_messages = 6
        start_index = max(0, len(self.log_messages) - max_messages)
        for i, log_entry in enumerate(self.log_messages[start_index:]):
            log_text = font_small.render(log_entry['message'], True, log_entry['color'])
            screen.blit(log_text, (20, log_y + 40 + i * 20))

# Fonctions de test
def test_import_modules():
    """Teste l'importation des modules améliorés"""
    try:
        # Importer les modules
        import particle_system_optimized
        import modern_background_optimized
        import ui_enhancements
        import bug_fixes
        
        return True
    except ImportError as e:
        print(f"Erreur d'importation: {e}")
        return False

def test_parallax_background():
    """Teste le fond parallaxe amélioré"""
    try:
        import modern_background_optimized
        
        # Créer une instance du fond parallaxe
        parallax = modern_background_optimized.EnhancedParallaxBackground(800, 600)
        
        # Tester les méthodes
        parallax.update(0)
        
        # Créer une surface pour tester le rendu
        test_surface = pygame.Surface((800, 600))
        parallax.draw(test_surface)
        
        return True
    except Exception as e:
        print(f"Erreur lors du test du fond parallaxe: {e}")
        return False

def test_particle_system():
    """Teste le système de particules optimisé"""
    try:
        import particle_system_optimized
        
        # Créer une instance du système de particules
        particles = particle_system_optimized.ParticleSystem(800, 600)
        
        # Tester les méthodes
        particles.add_movement_particles(400, 300, 10)
        particles.add_effect_particles(400, 300, 10, (255, 0, 0))
        particles.update()
        
        # Créer une surface pour tester le rendu
        test_surface = pygame.Surface((800, 600))
        particles.draw(test_surface)
        
        return True
    except Exception as e:
        print(f"Erreur lors du test du système de particules: {e}")
        return False

def test_ui_enhancements():
    """Teste les améliorations de l'interface utilisateur"""
    try:
        import ui_enhancements
        
        # Créer une instance des effets d'interface
        ui = ui_enhancements.UIEffects(800, 600)
        
        # Tester les méthodes
        ui.update()
        
        # Tester la création de boutons
        button = ui.create_gradient_button(200, 50, (41, 128, 185), (52, 152, 219))
        
        # Tester la création de panneaux
        panel = ui.create_glass_panel(300, 200, (0, 0, 0, 150), (255, 255, 255, 50), 2)
        
        # Tester la création de texte néon
        font = pygame.font.SysFont('Arial', 24)
        neon_text = ui.create_neon_text("Test", font, (255, 255, 255), (0, 0, 255))
        
        return True
    except Exception as e:
        print(f"Erreur lors du test des améliorations d'interface: {e}")
        return False

def test_bug_fixes():
    """Teste les corrections de bugs"""
    try:
        import bug_fixes
        
        # Créer une instance factice de jeu pour tester les corrections
        class MockGame:
            def __init__(self):
                self.state = 'menu'
                self.menu_buttons = []
                self.pause_buttons = []
                self.character_pos = [0, 0]
                self.grid = [[0, 0], [0, 0]]
                self.rows = 2
                self.cols = 2
                self.move_cooldown = 0
                self.default_move_cooldown = 10
                self.steps = 0
                self.end_pos = [1, 1]
                self.camera_x = 0
                self.camera_y = 0
                self.minimap_toggle_time = 0
                self.show_minimap = True
                self.ui_animation_time = 0
                self.fps_values = []
                self.last_fps_update = 0
                self.fps_update_interval = 500
                self.fps_display = "FPS: 0.0"
                self.clock = pygame.time.Clock()
                
            def start_game(self):
                self.state = 'playing'
                
            def show_high_scores(self):
                pass
                
            def show_settings(self):
                pass
                
            def return_to_menu(self):
                self.state = 'menu'
                
            def handle_game_events(self, event):
                return False
                
            def level_complete(self):
                pass
                
            def add_notification(self, text, duration=3000, color_scheme="blue"):
                pass
                
            def setup_game(self):
                pass
                
            def run(self):
                pass
                
            class particle_system:
                @staticmethod
                def add_movement_particles(x, y, count):
                    pass
        
        # Appliquer les corrections de bugs
        mock_game = MockGame()
        fixed_game = bug_fixes.apply_bug_fixes(mock_game)
        
        # Vérifier que les gestionnaires ont été ajoutés
        has_menu_nav = hasattr(fixed_game, 'menu_nav')
        has_event_manager = hasattr(fixed_game, 'event_manager')
        has_error_handler = hasattr(fixed_game, 'error_handler')
        has_collision_manager = hasattr(fixed_game, 'collision_manager')
        has_resource_manager = hasattr(fixed_game, 'resource_manager')
        
        # Vérifier que les méthodes ont été remplacées
        has_safe_start_game = fixed_game.start_game != mock_game.start_game
        has_handle_back_button = hasattr(fixed_game, 'handle_back_button')
        has_recover_from_crash = hasattr(fixed_game, 'recover_from_crash')
        
        return (has_menu_nav and has_event_manager and has_error_handler and 
                has_collision_manager and has_resource_manager and 
                has_safe_start_game and has_handle_back_button and 
                has_recover_from_crash)
    except Exception as e:
        print(f"Erreur lors du test des corrections de bugs: {e}")
        return False

def test_integration():
    """Teste l'intégration de toutes les améliorations"""
    try:
        # Créer un fichier temporaire pour tester l'intégration
        test_file = """
import pygame
import sys
from particle_system_optimized import ParticleSystem
from modern_background_optimized import EnhancedParallaxBackground
from ui_enhancements import UIEffects
import bug_fixes

# Initialiser Pygame
pygame.init()

# Créer l'écran
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test d'intégration")

# Créer les instances
particle_system = ParticleSystem(800, 600)
parallax_background = EnhancedParallaxBackground(800, 600)
ui_effects = UIEffects(800, 600)

# Classe de jeu simplifiée pour le test
class SimpleGame:
    def __init__(self):
        self.state = 'menu'
        self.running = True
        self.clock = pygame.time.Clock()
        
    def start_game(self):
        self.state = 'playing'
        
    def show_high_scores(self):
        pass
        
    def show_settings(self):
        pass
        
    def return_to_menu(self):
        self.state = 'menu'
        
    def run(self):
        # Boucle principale simplifiée
        for _ in range(10):  # Juste quelques itérations pour le test
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Mettre à jour
            parallax_background.update(0)
            particle_system.update()
            ui_effects.update()
            
            # Dessiner
            parallax_background.draw(screen)
            particle_system.draw(screen)
            
            # Afficher
            pygame.display.flip()
            self.clock.tick(60)
        
        return True

# Créer et corriger le jeu
game = SimpleGame()
fixed_game = bug_fixes.apply_bug_fixes(game)

# Exécuter le jeu
result = fixed_game.run()
pygame.quit()

# Retourner le résultat
sys.exit(0 if result else 1)
"""
        
        with open("test_integration.py", "w") as f:
            f.write(test_file)
        
        # Exécuter le test d'intégration
        import subprocess
        result = subprocess.run([sys.executable, "test_integration.py"], capture_output=True)
        
        # Nettoyer
        if os.path.exists("test_integration.py"):
            os.remove("test_integration.py")
        
        return result.returncode == 0
    except Exception as e:
        print(f"Erreur lors du test d'intégration: {e}")
        return False

def test_performance():
    """Teste les améliorations de performance"""
    try:
        import time
        import particle_system_optimized
        import modern_background_optimized
        
        # Créer les instances
        particle_system = particle_system_optimized.ParticleSystem(800, 600)
        parallax_background = modern_background_optimized.EnhancedParallaxBackground(800, 600)
        
        # Surface de test
        test_surface = pygame.Surface((800, 600))
        
        # Mesurer les performances du système de particules
        start_time = time.time()
        for _ in range(100):
            particle_system.add_movement_particles(400, 300, 5)
            particle_system.update()
            particle_system.draw(test_surface)
        particle_time = time.time() - start_time
        
        # Mesurer les performances du fond parallaxe
        start_time = time.time()
        for i in range(100):
            parallax_background.update(i)
            parallax_background.draw(test_surface)
        parallax_time = time.time() - start_time
        
        # Les tests sont considérés comme réussis si les opérations prennent moins de 1 seconde
        # Ce seuil peut être ajusté en fonction des performances attendues
        return particle_time < 1.0 and parallax_time < 1.0
    except Exception as e:
        print(f"Erreur lors du test de performance: {e}")
        return False

def test_final_game():
    """Teste le jeu final avec toutes les améliorations"""
    try:
        # Créer un fichier temporaire pour tester le jeu final
        test_file = """
import pygame
import sys
import importlib.util
import os

# Vérifier si les fichiers nécessaires existent
required_files = [
    'main_enhanced_ui.py',
    'particle_system_optimized.py',
    'modern_background_optimized.py',
    'ui_enhancements.py',
    'bug_fixes.py'
]

for file in required_files:
    if not os.path.exists(file):
        print(f"Fichier manquant: {file}")
        sys.exit(1)

# Charger le module main_enhanced_ui
spec = importlib.util.spec_from_file_location("main_enhanced_ui", "main_enhanced_ui.py")
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

# Importer bug_fixes
import bug_fixes

# Créer une instance du jeu
game = main_module.Game()

# Appliquer les corrections de bugs
fixed_game = bug_fixes.apply_bug_fixes(game)

# Remplacer la méthode run pour un test rapide
original_run = fixed_game.run

def test_run():
    # Initialiser le jeu
    fixed_game.setup_game()
    
    # Simuler quelques frames
    for _ in range(10):
        # Mettre à jour l'état du jeu
        if fixed_game.state == 'menu':
            fixed_game.update_menu()
        elif fixed_game.state == 'playing':
            fixed_game.update_game()
        
        # Simuler un événement de touche pour changer d'état
        if _ == 5:
            fixed_game.state = 'playing'
    
    return True

# Remplacer la méthode run
fixed_game.run = test_run

# Exécuter le test
result = fixed_game.run()
pygame.quit()

# Retourner le résultat
sys.exit(0 if result else 1)
"""
        
        with open("test_final_game.py", "w") as f:
            f.write(test_file)
        
        # Exécuter le test du jeu final
        import subprocess
        result = subprocess.run([sys.executable, "test_final_game.py"], capture_output=True)
        
        # Nettoyer
        if os.path.exists("test_final_game.py"):
            os.remove("test_final_game.py")
        
        return result.returncode == 0
    except Exception as e:
        print(f"Erreur lors du test du jeu final: {e}")
        return False

# Fonction principale
def main():
    tester = GameTester()
    
    # Ajouter les tests
    tester.add_test("Import des modules", test_import_modules, "Vérifie que tous les modules améliorés peuvent être importés")
    tester.add_test("Fond parallaxe", test_parallax_background, "Teste le fond parallaxe amélioré")
    tester.add_test("Système de particules", test_particle_system, "Teste le système de particules optimisé")
    tester.add_test("Améliorations UI", test_ui_enhancements, "Teste les améliorations de l'interface utilisateur")
    tester.add_test("Corrections de bugs", test_bug_fixes, "Teste les corrections de bugs et problèmes")
    tester.add_test("Performance", test_performance, "Teste les améliorations de performance")
    tester.add_test("Intégration", test_integration, "Teste l'intégration de toutes les améliorations")
    tester.add_test("Jeu final", test_final_game, "Teste le jeu final avec toutes les améliorations")
    
    # Exécuter les tests
    tester.run_tests()

if __name__ == "__main__":
    main()

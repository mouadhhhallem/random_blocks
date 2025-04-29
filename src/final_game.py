import pygame
import sys
import os
import importlib
from bug_fixes import apply_bug_fixes

# Vérifier que tous les fichiers nécessaires existent
required_files = [
    'main_enhanced_ui.py',
    'particle_system_optimized.py',
    'modern_background_optimized.py',
    'ui_enhancements.py',
    'bug_fixes.py'
]

missing_files = []
for file in required_files:
    if not os.path.exists(file):
        missing_files.append(file)

if missing_files:
    print(f"Erreur: Les fichiers suivants sont manquants: {', '.join(missing_files)}")
    sys.exit(1)

# Importer les modules nécessaires
try:
    # Importer le module principal
    spec = importlib.util.spec_from_file_location("main_enhanced_ui", "main_enhanced_ui.py")
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    
    # Importer les autres modules
    import particle_system_optimized
    import modern_background_optimized
    import ui_enhancements
    
    print("Tous les modules ont été importés avec succès.")
except ImportError as e:
    print(f"Erreur lors de l'importation des modules: {e}")
    sys.exit(1)

# Créer une instance du jeu avec toutes les améliorations
try:
    # Créer le jeu
    game = main_module.Game()
    
    # Appliquer les corrections de bugs
    game = apply_bug_fixes(game)
    
    print("Le jeu a été créé et les corrections de bugs ont été appliquées avec succès.")
except Exception as e:
    print(f"Erreur lors de la création du jeu: {e}")
    sys.exit(1)

# Fonction principale
def main():
    print("Démarrage du jeu avec toutes les améliorations...")
    
    try:
        # Exécuter le jeu
        game.run()
    except Exception as e:
        print(f"Erreur lors de l'exécution du jeu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("Jeu terminé.")

if __name__ == "__main__":
    main()

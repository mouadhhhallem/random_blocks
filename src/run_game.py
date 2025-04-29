import pygame
import sys
import os

# Vérifier que tous les fichiers nécessaires existent
required_files = [
    'main_fixed.py',
    'particle_system_fixed.py'
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
    from main_fixed import Game
    
    print("Tous les modules ont été importés avec succès.")
except ImportError as e:
    print(f"Erreur lors de l'importation des modules: {e}")
    sys.exit(1)

# Fonction principale
def main():
    print("Démarrage du jeu avec toutes les améliorations...")
    
    try:
        # Créer et exécuter le jeu
        game = Game()
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

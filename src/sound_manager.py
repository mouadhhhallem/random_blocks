import pygame
import os

class SoundManager:
    def __init__(self):
        self.audio_enabled = False
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except pygame.error:
            print("Avertissement: Impossible d'initialiser l'audio. Le jeu fonctionnera sans son.")
        
        self.music_dir = os.path.join("assets", "music")
        self.current_track = None
        self.volume = 0.5
        
        # Ensure music directory exists
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir, exist_ok=True)

    def play_menu_theme(self):
        """Play menu background music"""
        if not self.audio_enabled:
            return
            
        menu_theme = os.path.join(self.music_dir, "menu_theme.mp3")
        if os.path.exists(menu_theme) and self.current_track != "menu":
            pygame.mixer.music.load(menu_theme)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_track = "menu"

    def play_game_theme(self):
        """Play game background music"""
        if not self.audio_enabled:
            return
            
        game_theme = os.path.join(self.music_dir, "game_theme.mp3")
        if os.path.exists(game_theme) and self.current_track != "game":
            pygame.mixer.music.load(game_theme)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_track = "game"

    def play_victory(self):
        """Play victory sound"""
        if not self.audio_enabled:
            return
            
        victory_sound = os.path.join(self.music_dir, "victory.mp3")
        if os.path.exists(victory_sound):
            victory_channel = pygame.mixer.Channel(1)  # Use separate channel for sound effects
            victory_sound = pygame.mixer.Sound(victory_sound)
            victory_channel.play(victory_sound)

    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        if not self.audio_enabled:
            return
            
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def stop_music(self):
        """Stop current music"""
        if not self.audio_enabled:
            return
            
        pygame.mixer.music.stop()
        self.current_track = None

    def pause_music(self):
        """Pause current music"""
        if not self.audio_enabled:
            return
            
        pygame.mixer.music.pause()

    def unpause_music(self):
        """Unpause current music"""
        if not self.audio_enabled:
            return
            
        pygame.mixer.music.unpause()

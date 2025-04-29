import pygame
import math
import random

class UIEffects:
    """
    Classe pour les effets d'interface utilisateur avancés
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.time = 0
        
        # Couleurs
        self.colors = {
            'blue': (41, 128, 185),
            'light_blue': (52, 152, 219),
            'green': (39, 174, 96),
            'light_green': (46, 204, 113),
            'red': (192, 57, 43),
            'light_red': (231, 76, 60),
            'purple': (142, 68, 173),
            'light_purple': (155, 89, 182),
            'orange': (243, 156, 18),
            'light_orange': (255, 190, 118),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (100, 100, 100),
            'light_gray': (200, 200, 200),
        }
        
        # Cache pour les surfaces
        self.surface_cache = {}
        
    def update(self):
        """Mettre à jour les animations"""
        self.time += 1
        
    def create_gradient_button(self, width, height, color1, color2, border_radius=15, vertical=True):
        """Créer un bouton avec un dégradé de couleur"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if vertical:
            for y in range(height):
                ratio = y / height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        else:
            for x in range(width):
                ratio = x / width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))
                
        # Appliquer le rayon de bordure
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, width, height), border_radius=border_radius)
        surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        return surface
    
    def create_glass_panel(self, width, height, color=(255, 255, 255, 30), border_color=(255, 255, 255, 80), border_width=2, border_radius=15):
        """Créer un panneau avec effet de verre"""
        # Vérifier si cette surface est dans le cache
        cache_key = (width, height, color, border_color, border_width, border_radius)
        if cache_key in self.surface_cache:
            return self.surface_cache[cache_key]
            
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fond semi-transparent
        pygame.draw.rect(surface, color, (0, 0, width, height), border_radius=border_radius)
        
        # Effet de brillance en haut
        highlight = pygame.Surface((width, height // 3), pygame.SRCALPHA)
        for y in range(height // 3):
            alpha = 50 - int(y * 50 / (height // 3))
            if alpha > 0:
                pygame.draw.line(highlight, (255, 255, 255, alpha), (0, y), (width, y))
        
        # Appliquer le rayon de bordure à la surbrillance
        mask = pygame.Surface((width, height // 3), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, width, height // 3), border_radius=border_radius)
        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        surface.blit(highlight, (0, 0))
        
        # Bordure
        if border_width > 0:
            pygame.draw.rect(surface, border_color, (0, 0, width, height), width=border_width, border_radius=border_radius)
        
        # Stocker dans le cache
        self.surface_cache[cache_key] = surface
        
        return surface
    
    def create_neon_text(self, text, font, color, glow_color=None, glow_size=5):
        """Créer du texte avec un effet néon"""
        if glow_color is None:
            glow_color = color
            
        # Texte principal
        text_surface = font.render(text, True, color)
        text_width, text_height = text_surface.get_size()
        
        # Surface finale avec espace pour la lueur
        final_surface = pygame.Surface((text_width + glow_size*2, text_height + glow_size*2), pygame.SRCALPHA)
        
        # Créer la lueur
        glow_surf = pygame.Surface((text_width + glow_size*2, text_height + glow_size*2), pygame.SRCALPHA)
        for i in range(1, glow_size+1):
            alpha = 255 - int(i * 255 / glow_size)
            temp_surf = font.render(text, True, (*glow_color[:3], alpha))
            for offset_x in range(-i, i+1):
                for offset_y in range(-i, i+1):
                    if offset_x*offset_x + offset_y*offset_y <= i*i:  # Forme circulaire
                        glow_surf.blit(temp_surf, (glow_size + offset_x, glow_size + offset_y))
        
        # Combiner la lueur et le texte
        final_surface.blit(glow_surf, (0, 0))
        final_surface.blit(text_surface, (glow_size, glow_size))
        
        return final_surface
    
    def create_animated_icon(self, icon_type, size, color):
        """Créer une icône animée"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if icon_type == "coin":
            # Animation de pièce
            angle = (self.time * 5) % 360
            scale = 0.8 + 0.2 * math.sin(math.radians(self.time * 3))
            
            # Cercle extérieur
            pygame.draw.circle(surface, color, (size//2, size//2), int(size//2 * scale))
            
            # Cercle intérieur
            inner_size = int(size//3 * scale)
            pygame.draw.circle(surface, (255, 255, 255, 100), (size//2, size//2), inner_size)
            
            # Étoile au centre
            if angle < 180:  # Faire clignoter l'étoile
                points = []
                for i in range(5):
                    a = math.radians(angle + i * 72)
                    x = size//2 + int(inner_size * 0.8 * math.cos(a))
                    y = size//2 + int(inner_size * 0.8 * math.sin(a))
                    points.append((x, y))
                
                pygame.draw.polygon(surface, (255, 255, 255), points)
                
        elif icon_type == "clock":
            # Animation d'horloge
            pygame.draw.circle(surface, color, (size//2, size//2), size//2 - 2)
            pygame.draw.circle(surface, (255, 255, 255, 100), (size//2, size//2), size//2 - 4, 2)
            
            # Aiguilles
            hour_angle = math.radians(self.time % 360)
            minute_angle = math.radians((self.time * 12) % 360)
            
            # Aiguille des heures
            hour_x = size//2 + int((size//4) * math.sin(hour_angle))
            hour_y = size//2 - int((size//4) * math.cos(hour_angle))
            pygame.draw.line(surface, (255, 255, 255), (size//2, size//2), (hour_x, hour_y), 3)
            
            # Aiguille des minutes
            minute_x = size//2 + int((size//3) * math.sin(minute_angle))
            minute_y = size//2 - int((size//3) * math.cos(minute_angle))
            pygame.draw.line(surface, (255, 255, 255), (size//2, size//2), (minute_x, minute_y), 2)
            
            # Point central
            pygame.draw.circle(surface, (255, 255, 255), (size//2, size//2), 3)
            
        elif icon_type == "star":
            # Animation d'étoile
            scale = 0.8 + 0.2 * math.sin(math.radians(self.time * 3))
            points = []
            
            for i in range(5):
                # Pointes extérieures
                angle = math.radians(i * 72 - 90)
                x = size//2 + int((size//2 - 2) * scale * math.cos(angle))
                y = size//2 + int((size//2 - 2) * scale * math.sin(angle))
                points.append((x, y))
                
                # Pointes intérieures
                angle = math.radians(i * 72 - 90 + 36)
                x = size//2 + int((size//4) * scale * math.cos(angle))
                y = size//2 + int((size//4) * scale * math.sin(angle))
                points.append((x, y))
            
            pygame.draw.polygon(surface, color, points)
            
            # Effet de brillance
            if (self.time // 30) % 2 == 0:
                pygame.draw.polygon(surface, (255, 255, 255, 100), points, 2)
        
        return surface
    
    def create_progress_bar(self, width, height, progress, color_scheme="blue", animated=True):
        """Créer une barre de progression stylisée"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Couleurs selon le schéma
        if color_scheme == "blue":
            bg_color = (41, 128, 185, 100)
            fill_color = (52, 152, 219)
            highlight_color = (173, 216, 230)
        elif color_scheme == "green":
            bg_color = (39, 174, 96, 100)
            fill_color = (46, 204, 113)
            highlight_color = (163, 228, 215)
        elif color_scheme == "red":
            bg_color = (192, 57, 43, 100)
            fill_color = (231, 76, 60)
            highlight_color = (245, 183, 177)
        elif color_scheme == "purple":
            bg_color = (142, 68, 173, 100)
            fill_color = (155, 89, 182)
            highlight_color = (215, 189, 226)
        else:
            bg_color = (100, 100, 100, 100)
            fill_color = (150, 150, 150)
            highlight_color = (200, 200, 200)
        
        # Fond
        pygame.draw.rect(surface, bg_color, (0, 0, width, height), border_radius=height//2)
        
        # Remplissage
        fill_width = int(width * progress)
        if fill_width > 0:
            # Animation de pulsation
            if animated:
                pulse = 0.05 * math.sin(math.radians(self.time * 5))
                fill_height = height * (1.0 + pulse)
                fill_y = (height - fill_height) / 2
            else:
                fill_height = height
                fill_y = 0
                
            pygame.draw.rect(surface, fill_color, (0, fill_y, fill_width, fill_height), border_radius=height//2)
            
            # Effet de brillance
            highlight_height = fill_height // 3
            highlight = pygame.Surface((fill_width, highlight_height), pygame.SRCALPHA)
            for y in range(highlight_height):
                alpha = 100 - int(y * 100 / highlight_height)
                if alpha > 0:
                    pygame.draw.line(highlight, (*highlight_color[:3], alpha), (0, y), (fill_width, y))
            
            # Appliquer le rayon de bordure à la surbrillance
            if fill_width > height//2:
                mask = pygame.Surface((fill_width, highlight_height), pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255), (0, 0, fill_width, highlight_height), border_radius=height//2)
                highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            surface.blit(highlight, (0, fill_y))
        
        # Bordure
        pygame.draw.rect(surface, (*fill_color[:3], 150), (0, 0, width, height), width=2, border_radius=height//2)
        
        return surface
    
    def create_tooltip(self, text, font, width=200, color=(50, 50, 50, 220), border_color=(255, 255, 255, 100)):
        """Créer une infobulle stylisée"""
        # Rendu du texte
        text_surface = font.render(text, True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()
        
        # Ajuster la largeur si nécessaire
        if text_width + 20 > width:
            width = text_width + 20
            
        height = text_height + 16
        
        # Créer la surface
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fond avec effet de verre
        pygame.draw.rect(surface, color, (0, 0, width, height), border_radius=8)
        
        # Effet de brillance en haut
        highlight = pygame.Surface((width, height // 3), pygame.SRCALPHA)
        for y in range(height // 3):
            alpha = 30 - int(y * 30 / (height // 3))
            if alpha > 0:
                pygame.draw.line(highlight, (255, 255, 255, alpha), (0, y), (width, y))
        
        # Appliquer le rayon de bordure à la surbrillance
        mask = pygame.Surface((width, height // 3), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, width, height // 3), border_radius=8)
        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        surface.blit(highlight, (0, 0))
        
        # Bordure
        pygame.draw.rect(surface, border_color, (0, 0, width, height), width=1, border_radius=8)
        
        # Texte
        surface.blit(text_surface, ((width - text_width) // 2, (height - text_height) // 2))
        
        # Flèche en bas
        arrow_points = [
            (width // 2 - 8, height),
            (width // 2, height + 8),
            (width // 2 + 8, height)
        ]
        pygame.draw.polygon(surface, color, arrow_points)
        pygame.draw.polygon(surface, border_color, arrow_points, width=1)
        
        return surface
    
    def create_minimap(self, width, height, player_pos, grid, start_pos, end_pos, color_scheme="blue"):
        """Créer une mini-carte stylisée"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Couleurs selon le schéma
        if color_scheme == "blue":
            bg_color = (41, 128, 185, 100)
            wall_color = (52, 152, 219)
            player_color = (255, 255, 255)
            start_color = (46, 204, 113)
            end_color = (231, 76, 60)
        else:
            bg_color = (100, 100, 100, 100)
            wall_color = (150, 150, 150)
            player_color = (255, 255, 255)
            start_color = (0, 255, 0)
            end_color = (255, 0, 0)
        
        # Fond avec effet de verre
        pygame.draw.rect(surface, bg_color, (0, 0, width, height), border_radius=8)
        
        # Effet de brillance en haut
        highlight = pygame.Surface((width, height // 4), pygame.SRCALPHA)
        for y in range(height // 4):
            alpha = 30 - int(y * 30 / (height // 4))
            if alpha > 0:
                pygame.draw.line(highlight, (255, 255, 255, alpha), (0, y), (width, y))
        
        # Appliquer le rayon de bordure à la surbrillance
        mask = pygame.Surface((width, height // 4), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, width, height // 4), border_radius=8)
        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        surface.blit(highlight, (0, 0))
        
        # Bordure
        pygame.draw.rect(surface, (255, 255, 255, 100), (0, 0, width, height), width=1, border_radius=8)
        
        # Dessiner la grille
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        
        if rows > 0 and cols > 0:
            cell_width = (width - 10) / cols
            cell_height = (height - 10) / rows
            
            for y in range(rows):
                for x in range(cols):
                    cell_x = 5 + x * cell_width
                    cell_y = 5 + y * cell_height
                    
                    if grid[y][x] == 1:  # Mur
                        pygame.draw.rect(surface, wall_color, (cell_x, cell_y, cell_width, cell_height))
            
            # Dessiner la position de départ
            start_x = 5 + start_pos[0] * cell_width + cell_width / 2
            start_y = 5 + start_pos[1] * cell_height + cell_height / 2
            pygame.draw.circle(surface, start_color, (int(start_x), int(start_y)), int(min(cell_width, cell_height) / 2))
            
            # Dessiner la position de fin
            end_x = 5 + end_pos[0] * cell_width + cell_width / 2
            end_y = 5 + end_pos[1] * cell_height + cell_height / 2
            pygame.draw.circle(surface, end_color, (int(end_x), int(end_y)), int(min(cell_width, cell_height) / 2))
            
            # Dessiner la position du joueur avec animation de pulsation
            player_x = 5 + player_pos[0] * cell_width + cell_width / 2
            player_y = 5 + player_pos[1] * cell_height + cell_height / 2
            
            # Animation de pulsation
            pulse = 0.2 * math.sin(math.radians(self.time * 10)) + 1.0
            player_size = int(min(cell_width, cell_height) / 2 * pulse)
            
            pygame.draw.circle(surface, player_color, (int(player_x), int(player_y)), player_size)
            
            # Ajouter un halo autour du joueur
            halo_size = player_size + 2
            pygame.draw.circle(surface, (255, 255, 255, 50), (int(player_x), int(player_y)), halo_size, 1)
        
        return surface
    
    def create_notification(self, text, font, color_scheme="blue", width=300):
        """Créer une notification stylisée"""
        # Couleurs selon le schéma
        if color_scheme == "blue":
            bg_color = (41, 128, 185, 220)
            border_color = (52, 152, 219)
        elif color_scheme == "green":
            bg_color = (39, 174, 96, 220)
            border_color = (46, 204, 113)
        elif color_scheme == "red":
            bg_color = (192, 57, 43, 220)
            border_color = (231, 76, 60)
        elif color_scheme == "purple":
            bg_color = (142, 68, 173, 220)
            border_color = (155, 89, 182)
        else:
            bg_color = (100, 100, 100, 220)
            border_color = (150, 150, 150)
        
        # Rendu du texte
        text_surface = font.render(text, True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()
        
        # Ajuster la largeur si nécessaire
        if text_width + 40 > width:
            width = text_width + 40
            
        height = text_height + 20
        
        # Créer la surface
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fond avec effet de verre
        pygame.draw.rect(surface, bg_color, (0, 0, width, height), border_radius=10)
        
        # Effet de brillance en haut
        highlight = pygame.Surface((width, height // 3), pygame.SRCALPHA)
        for y in range(height // 3):
            alpha = 50 - int(y * 50 / (height // 3))
            if alpha > 0:
                pygame.draw.line(highlight, (255, 255, 255, alpha), (0, y), (width, y))
        
        # Appliquer le rayon de bordure à la surbrillance
        mask = pygame.Surface((width, height // 3), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, width, height // 3), border_radius=10)
        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        surface.blit(highlight, (0, 0))
        
        # Bordure
        pygame.draw.rect(surface, border_color, (0, 0, width, height), width=2, border_radius=10)
        
        # Icône (selon le schéma de couleur)
        if color_scheme == "green":
            # Icône de succès (coche)
            icon_points = [(10, height//2), (15, height//2 + 5), (25, height//2 - 5)]
            pygame.draw.lines(surface, (255, 255, 255), False, icon_points, 2)
            icon_width = 30
        elif color_scheme == "red":
            # Icône d'erreur (croix)
            pygame.draw.line(surface, (255, 255, 255), (10, height//2 - 5), (20, height//2 + 5), 2)
            pygame.draw.line(surface, (255, 255, 255), (10, height//2 + 5), (20, height//2 - 5), 2)
            icon_width = 30
        elif color_scheme == "blue":
            # Icône d'information (i)
            pygame.draw.circle(surface, (255, 255, 255), (15, height//2 - 5), 2)
            pygame.draw.line(surface, (255, 255, 255), (15, height//2), (15, height//2 + 5), 2)
            icon_width = 30
        else:
            # Pas d'icône
            icon_width = 10
        
        # Texte
        surface.blit(text_surface, (icon_width, (height - text_height) // 2))
        
        return surface
    
    def create_button_hover_effect(self, button_rect, color=(255, 255, 255, 30), glow_size=10):
        """Créer un effet de survol pour un bouton"""
        width, height = button_rect.width + glow_size * 2, button_rect.height + glow_size * 2
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Créer l'effet de lueur
        for i in range(1, glow_size+1):
            alpha = int(100 * (1 - i/glow_size))
            pygame.draw.rect(
                surface,
                (*color[:3], alpha),
                (glow_size-i, glow_size-i, button_rect.width+i*2, button_rect.height+i*2),
                border_radius=15
            )
        
        return surface, (button_rect.x - glow_size, button_rect.y - glow_size)
    
    def create_animated_background(self, width, height, color_scheme="blue"):
        """Créer un arrière-plan animé pour les menus"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Couleurs selon le schéma
        if color_scheme == "blue":
            bg_color1 = (41, 128, 185)
            bg_color2 = (52, 152, 219)
        elif color_scheme == "green":
            bg_color1 = (39, 174, 96)
            bg_color2 = (46, 204, 113)
        elif color_scheme == "purple":
            bg_color1 = (142, 68, 173)
            bg_color2 = (155, 89, 182)
        else:
            bg_color1 = (50, 50, 50)
            bg_color2 = (80, 80, 80)
        
        # Dégradé de fond
        for y in range(height):
            ratio = y / height
            r = int(bg_color1[0] * (1 - ratio) + bg_color2[0] * ratio)
            g = int(bg_color1[1] * (1 - ratio) + bg_color2[1] * ratio)
            b = int(bg_color1[2] * (1 - ratio) + bg_color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Ajouter des particules animées
        for i in range(50):
            x = (i * width // 50 + self.time) % width
            y = int(height * 0.5 + math.sin((x + self.time) * 0.01) * height * 0.3)
            size = int(3 + 2 * math.sin((x + self.time) * 0.02))
            alpha = int(100 + 50 * math.sin((x + self.time) * 0.01))
            pygame.draw.circle(surface, (255, 255, 255, alpha), (x, y), size)
        
        # Ajouter des lignes ondulées
        for i in range(5):
            points = []
            for x in range(0, width, 10):
                y = int(height * (0.2 + i * 0.15) + math.sin((x + self.time + i * 100) * 0.01) * height * 0.05)
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(surface, (255, 255, 255, 30), False, points, 2)
        
        return surface
    
    def create_achievement_popup(self, title, description, font_title, font_desc, icon_type="star", color_scheme="purple"):
        """Créer une popup de succès stylisée"""
        # Couleurs selon le schéma
        if color_scheme == "blue":
            bg_color = (41, 128, 185, 220)
            border_color = (52, 152, 219)
            icon_color = (52, 152, 219)
        elif color_scheme == "green":
            bg_color = (39, 174, 96, 220)
            border_color = (46, 204, 113)
            icon_color = (46, 204, 113)
        elif color_scheme == "purple":
            bg_color = (142, 68, 173, 220)
            border_color = (155, 89, 182)
            icon_color = (155, 89, 182)
        elif color_scheme == "gold":
            bg_color = (212, 175, 55, 220)
            border_color = (255, 215, 0)
            icon_color = (255, 215, 0)
        else:
            bg_color = (100, 100, 100, 220)
            border_color = (150, 150, 150)
            icon_color = (150, 150, 150)
        
        # Rendu du texte
        title_surface = font_title.render(title, True, (255, 255, 255))
        desc_surface = font_desc.render(description, True, (255, 255, 255))
        
        # Dimensions
        width = max(title_surface.get_width(), desc_surface.get_width()) + 100
        height = title_surface.get_height() + desc_surface.get_height() + 40
        
        # Créer la surface
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fond avec effet de verre
        pygame.draw.rect(surface, bg_color, (0, 0, width, height), border_radius=15)
        
        # Effet de brillance en haut
        highlight = pygame.Surface((width, height // 3), pygame.SRCALPHA)
        for y in range(height // 3):
            alpha = 50 - int(y * 50 / (height // 3))
            if alpha > 0:
                pygame.draw.line(highlight, (255, 255, 255, alpha), (0, y), (width, y))
        
        # Appliquer le rayon de bordure à la surbrillance
        mask = pygame.Surface((width, height // 3), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, width, height // 3), border_radius=15)
        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        surface.blit(highlight, (0, 0))
        
        # Bordure
        pygame.draw.rect(surface, border_color, (0, 0, width, height), width=2, border_radius=15)
        
        # Icône
        icon_surface = self.create_animated_icon(icon_type, 50, icon_color)
        surface.blit(icon_surface, (20, (height - 50) // 2))
        
        # Texte
        surface.blit(title_surface, (80, 15))
        surface.blit(desc_surface, (80, 15 + title_surface.get_height() + 10))
        
        # Effet de particules
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, 20)
            x = width // 2 + int(distance * math.cos(angle))
            y = height // 2 + int(distance * math.sin(angle))
            size = random.randint(1, 3)
            pygame.draw.circle(surface, (255, 255, 255, 150), (x, y), size)
        
        return surface

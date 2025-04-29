import pygame
import random
import math
import os

class ModernBackground:
    """
    Un fond moderne et dynamique optimisé pour de meilleures performances.
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Palette de couleurs moderne et vibrante
        self.colors = {
            'dark_blue': (18, 30, 49),       # Bleu foncé (arrière-plan)
            'medium_blue': (32, 60, 86),     # Bleu moyen
            'accent_blue': (59, 130, 246),   # Bleu accent
            'light_blue': (96, 165, 250),    # Bleu clair
            'purple': (124, 58, 237),        # Violet (accent secondaire)
            'pink': (236, 72, 153),          # Rose (accent tertiaire)
            'cyan': (45, 212, 191),          # Cyan (accent quaternaire)
            'dark_purple': (91, 33, 182),    # Violet foncé
            
            # Couleurs de particules et d'effets
            'particle1': (59, 130, 246, 150),  # Bleu semi-transparent
            'particle2': (124, 58, 237, 150),  # Violet semi-transparent
            'particle3': (236, 72, 153, 150),  # Rose semi-transparent
            'particle4': (45, 212, 191, 150),  # Cyan semi-transparent
            'glow': (255, 255, 255, 30),      # Blanc pour les effets de lueur
        }
        
        # Couches de base pour l'arrière-plan (pré-rendues)
        self.base_surface = self.create_base_surface()
        
        # Éléments dynamiques (limités en nombre)
        self.particles = []
        self.glows = []
        self.stars = []
        self.create_particles(max_particles=30)  # Limiter le nombre de particules
        self.create_stars(max_stars=20)          # Limiter le nombre d'étoiles
        
        # Variables d'animation
        self.time = 0
        self.wave_offset = 0
        
        # Effet de vignette (pré-rendu)
        self.vignette = self.create_vignette()
        
        # Effet de grille (pré-rendu)
        self.grid = self.create_grid()
        
        # Triangle rotatif et orbe lumineux
        self.triangle_angle = 0
        self.orb_position = [random.randint(0, screen_width), random.randint(0, screen_height)]
        self.orb_trail = []
        
        # Cache pour les surfaces fréquemment utilisées
        self.surface_cache = {}
        
        # Contrôle de la fréquence de mise à jour
        self.update_frequency = 2  # Mettre à jour tous les N frames
        self.frame_counter = 0
    
    def create_base_surface(self):
        """Créer la surface de base pré-rendue pour l'arrière-plan."""
        base_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Couche 1: Arrière-plan dégradé
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(self.colors['dark_blue'][0] * (1 - ratio) + self.colors['medium_blue'][0] * ratio)
            g = int(self.colors['dark_blue'][1] * (1 - ratio) + self.colors['medium_blue'][1] * ratio)
            b = int(self.colors['dark_blue'][2] * (1 - ratio) + self.colors['medium_blue'][2] * ratio)
            pygame.draw.line(base_surface, (r, g, b), (0, y), (self.screen_width, y))
        
        # Couche 2: Motif subtil
        for _ in range(200):  # Réduire le nombre de points
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            radius = random.randint(1, 3)
            alpha = random.randint(5, 20)
            color = (*self.colors['light_blue'][:3], alpha)
            pygame.draw.circle(base_surface, color, (x, y), radius)
            
        return base_surface
    
    def create_particles(self, max_particles=30):
        """Créer des particules pour l'animation d'arrière-plan (nombre limité)."""
        for _ in range(max_particles):
            particle = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'size': random.uniform(1, 4),
                'speed': random.uniform(0.2, 1.0),
                'color': random.choice([
                    self.colors['particle1'],
                    self.colors['particle2'],
                    self.colors['particle3'],
                    self.colors['particle4']
                ]),
                'angle': random.uniform(0, 2 * math.pi),
                'shape': random.choice(['circle', 'triangle', 'square'])
            }
            self.particles.append(particle)
        
        # Créer des points lumineux (nombre limité)
        for _ in range(5):  # Réduire le nombre de lueurs
            glow = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'size': random.uniform(50, 150),
                'alpha': random.randint(10, 30),
                'color': random.choice([
                    self.colors['accent_blue'],
                    self.colors['purple'],
                    self.colors['pink'],
                    self.colors['cyan']
                ]),
                'pulse_speed': random.uniform(0.01, 0.03),
                'pulse_offset': random.uniform(0, 2 * math.pi)
            }
            self.glows.append(glow)
    
    def create_stars(self, max_stars=20):
        """Créer un motif d'étoiles pour l'arrière-plan (nombre limité)."""
        star_size = 40
        
        for _ in range(max_stars):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            
            star = {
                'x': x,
                'y': y,
                'size': star_size,
                'color': self.colors['medium_blue'],
                'outline_color': (*self.colors['accent_blue'][:3], 40),
                'pulse_speed': random.uniform(0.005, 0.015),
                'pulse_offset': random.uniform(0, 2 * math.pi)
            }
            self.stars.append(star)
    
    def create_vignette(self):
        """Créer un effet de vignette pour les bords de l'écran."""
        vignette = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for i in range(0, 100, 5):  # Réduire le nombre d'itérations
            alpha = int(i * 1.5)
            pygame.draw.rect(
                vignette,
                (0, 0, 0, alpha),
                (i, i, self.screen_width - 2*i, self.screen_height - 2*i),
                1
            )
        return vignette
    
    def create_grid(self):
        """Créer un effet de grille subtil."""
        grid = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for y in range(0, self.screen_height, 80):  # Augmenter l'espacement
            pygame.draw.line(grid, (*self.colors['accent_blue'][:3], 15), (0, y), (self.screen_width, y))
        for x in range(0, self.screen_width, 80):  # Augmenter l'espacement
            pygame.draw.line(grid, (*self.colors['accent_blue'][:3], 15), (x, 0), (x, self.screen_height))
        return grid
    
    def get_star_surface(self, size, color, outline_color=None):
        """Obtenir une surface d'étoile du cache ou en créer une nouvelle."""
        key = (size, color, outline_color)
        if key not in self.surface_cache:
            # Créer une nouvelle surface d'étoile
            surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            
            points = []
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi / 2
                radius = size if i % 2 == 0 else size // 2
                px = size + radius * math.cos(angle)
                py = size + radius * math.sin(angle)
                points.append((px, py))
            
            if outline_color:
                pygame.draw.polygon(surface, outline_color, points, 2)
            pygame.draw.polygon(surface, color, points)
            
            self.surface_cache[key] = surface
            
            # Limiter la taille du cache
            if len(self.surface_cache) > 50:
                # Supprimer une entrée aléatoire
                random_key = random.choice(list(self.surface_cache.keys()))
                del self.surface_cache[random_key]
                
        return self.surface_cache[key]
    
    def update(self, camera_x=0):
        """Mettre à jour l'animation d'arrière-plan (optimisée)."""
        # Mettre à jour moins fréquemment pour économiser des ressources
        self.frame_counter += 1
        if self.frame_counter % self.update_frequency != 0:
            return
            
        self.time += 1
        self.wave_offset = (self.wave_offset + 0.02) % (2 * math.pi)
        
        # Mettre à jour les particules (seulement une partie à chaque frame)
        update_count = min(len(self.particles), 10)  # Limiter le nombre de mises à jour
        for i in range(update_count):
            idx = (self.time + i) % len(self.particles)
            particle = self.particles[idx]
            particle['y'] += particle['speed']
            particle['x'] += math.sin(particle['angle'] + self.time * 0.01) * 0.5
            
            # Réinitialiser si hors écran
            if particle['y'] > self.screen_height:
                particle['y'] = 0
                particle['x'] = random.randint(0, self.screen_width)
            
            if particle['x'] < 0 or particle['x'] > self.screen_width:
                particle['x'] = random.randint(0, self.screen_width)
        
        # Mettre à jour l'angle du triangle rotatif
        self.triangle_angle = (self.triangle_angle + 0.02) % (2 * math.pi)
        
        # Mettre à jour la position de l'orbe lumineux
        self.orb_position[0] += math.cos(self.time * 0.01) * 2
        self.orb_position[1] += math.sin(self.time * 0.01) * 2
        
        # Garder l'orbe dans les limites de l'écran
        self.orb_position[0] = max(0, min(self.screen_width, self.orb_position[0]))
        self.orb_position[1] = max(0, min(self.screen_height, self.orb_position[1]))
        
        # Ajouter la position actuelle de l'orbe à la traînée
        self.orb_trail.append((self.orb_position[0], self.orb_position[1]))
        if len(self.orb_trail) > 10:  # Réduire la longueur de la traînée
            self.orb_trail.pop(0)
    
    def draw(self, surface):
        """Dessiner l'arrière-plan complet sur la surface spécifiée."""
        # Dessiner les couches de base
        surface.blit(self.base_surface, (0, 0))
        
        # Dessiner la grille
        surface.blit(self.grid, (0, 0))
        
        # Dessiner les points lumineux (seulement quelques-uns)
        for glow in self.glows[:3]:  # Limiter le nombre de lueurs dessinées
            pulse = math.sin(self.time * glow['pulse_speed'] + glow['pulse_offset'])
            size = glow['size'] * (0.8 + 0.4 * pulse)
            alpha = glow['alpha'] * (0.7 + 0.3 * pulse)
            
            # Utiliser une surface plus petite pour l'effet de lueur
            glow_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            for i in range(0, int(size), 5):  # Réduire le nombre d'itérations
                alpha_i = int(alpha * (1 - i/size))
                if alpha_i > 0:
                    pygame.draw.circle(
                        glow_surface,
                        (*glow['color'][:3], alpha_i),
                        (int(size), int(size)),
                        int(size - i)
                    )
            surface.blit(glow_surface, (int(glow['x'] - size), int(glow['y'] - size)))
        
        # Dessiner les étoiles (seulement quelques-unes)
        for star in self.stars[:10]:  # Limiter le nombre d'étoiles dessinées
            pulse = 1 + 0.5 * math.sin(self.time * star['pulse_speed'] + star['pulse_offset'])
            outline_color = (*star['outline_color'][:3], int(star['outline_color'][3] * pulse))
            
            star_surface = self.get_star_surface(star['size'], star['color'], outline_color)
            surface.blit(star_surface, (int(star['x'] - star['size']), int(star['y'] - star['size'])))
        
        # Dessiner les particules (seulement quelques-unes)
        for particle in self.particles[:20]:  # Limiter le nombre de particules dessinées
            if particle['shape'] == 'circle':
                pygame.draw.circle(
                    surface,
                    particle['color'],
                    (int(particle['x']), int(particle['y'])),
                    int(particle['size'])
                )
            elif particle['shape'] == 'square':
                pygame.draw.rect(
                    surface,
                    particle['color'],
                    (int(particle['x'] - particle['size']), 
                     int(particle['y'] - particle['size']),
                     int(particle['size'] * 2), 
                     int(particle['size'] * 2))
                )
            elif particle['shape'] == 'triangle':
                points = []
                for i in range(3):
                    angle = self.triangle_angle + 2 * math.pi * i / 3
                    px = particle['x'] + particle['size'] * math.cos(angle)
                    py = particle['y'] + particle['size'] * math.sin(angle)
                    points.append((int(px), int(py)))
                pygame.draw.polygon(surface, particle['color'], points)
        
        # Dessiner la vignette
        surface.blit(self.vignette, (0, 0))


class EnhancedParallaxBackground:
    """
    Un fond parallaxe amélioré avec des effets visuels modernes, optimisé pour de meilleures performances.
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.modern_background = ModernBackground(screen_width, screen_height)
        self.layers = []
        self.create_modern_layers()
        self.time = 0
        
        # Optimisations
        self.update_frequency = 2  # Mettre à jour tous les N frames
        self.frame_counter = 0
    
    def create_modern_layers(self):
        """Créer des couches parallaxes avec un style moderne."""
        # Couche 1: Étoiles distantes (très lent)
        stars = pygame.Surface((self.screen_width * 2, self.screen_height), pygame.SRCALPHA)
        for _ in range(100):  # Réduire le nombre d'étoiles
            x = random.randint(0, stars.get_width())
            y = random.randint(0, stars.get_height())
            size = random.randint(1, 3)
            alpha = random.randint(100, 255)
            color = (255, 255, 255, alpha)
            pygame.draw.circle(stars, color, (x, y), size)
        self.layers.append({"surface": stars, "speed": 0.05, "scroll_x": 0})
        
        # Couche 2: Nuages stylisés (lent)
        clouds = pygame.Surface((self.screen_width * 3, self.screen_height), pygame.SRCALPHA)
        for _ in range(8):  # Réduire le nombre de nuages
            x = random.randint(0, clouds.get_width())
            y = random.randint(0, self.screen_height // 2)
            width = random.randint(200, 400)
            height = random.randint(50, 100)
            alpha = random.randint(10, 30)
            color = (255, 255, 255, alpha)
            cloud_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            for i in range(width // 60):  # Réduire la densité des cercles
                cx = random.randint(0, width)
                cy = random.randint(0, height)
                cr = random.randint(30, 60)
                pygame.draw.circle(cloud_surface, color, (cx, cy), cr)
            clouds.blit(cloud_surface, (x, y))
        self.layers.append({"surface": clouds, "speed": 0.1, "scroll_x": 0})
        
        # Couche 3: Montagnes stylisées (moyen)
        mountains = pygame.Surface((self.screen_width * 2, self.screen_height), pygame.SRCALPHA)
        mountain_color = (60, 70, 90, 150)
        for i in range(5):  # Réduire le nombre de montagnes
            base_x = i * (mountains.get_width() // 5)
            base_y = self.screen_height - random.randint(100, 300)
            peak_x = base_x + random.randint(-100, 100)
            peak_y = base_y - random.randint(150, 250)
            points = [
                (base_x - 200, self.screen_height),
                (peak_x, peak_y),
                (base_x + 200, self.screen_height)
            ]
            pygame.draw.polygon(mountains, mountain_color, points)
        self.layers.append({"surface": mountains, "speed": 0.3, "scroll_x": 0})
        
        # Couche 4: Silhouettes d'arbres (rapide)
        trees = pygame.Surface((self.screen_width * 2, self.screen_height), pygame.SRCALPHA)
        tree_color = (30, 40, 50, 200)
        for i in range(15):  # Réduire le nombre d'arbres
            base_x = random.randint(0, trees.get_width())
            base_y = self.screen_height
            trunk_height = random.randint(50, 100)
            trunk_width = random.randint(10, 20)
            pygame.draw.rect(trees, tree_color, (base_x - trunk_width//2, base_y - trunk_height, trunk_width, trunk_height))
            foliage_width = trunk_height
            foliage_height = trunk_height * 2
            points = [
                (base_x, base_y - trunk_height - foliage_height),
                (base_x - foliage_width, base_y - trunk_height),
                (base_x + foliage_width, base_y - trunk_height)
            ]
            pygame.draw.polygon(trees, tree_color, points)
        self.layers.append({"surface": trees, "speed": 0.5, "scroll_x": 0})
    
    def update(self, camera_x):
        """Mettre à jour l'animation du fond parallaxe."""
        # Mettre à jour moins fréquemment pour économiser des ressources
        self.frame_counter += 1
        if self.frame_counter % self.update_frequency != 0:
            return
            
        self.time += 1
        self.modern_background.update(camera_x)
        
        for layer in self.layers:
            layer["scroll_x"] = -camera_x * layer["speed"]
            layer["scroll_x"] = layer["scroll_x"] % layer["surface"].get_width()
    
    def draw(self, surface):
        """Dessiner le fond parallaxe complet sur la surface spécifiée."""
        # Dessiner l'arrière-plan moderne
        self.modern_background.draw(surface)
        
        # Dessiner les couches parallaxes
        for layer in self.layers:
            # Optimisation: ne dessiner que si la couche est visible
            if layer["scroll_x"] < self.screen_width:
                surface.blit(layer["surface"], (int(layer["scroll_x"]), 0))
                
                # Dessiner la partie qui se répète si nécessaire
                if layer["scroll_x"] + layer["surface"].get_width() < self.screen_width:
                    surface.blit(layer["surface"], (int(layer["scroll_x"] + layer["surface"].get_width()), 0))
                
                # Dessiner la partie précédente si nécessaire
                if layer["scroll_x"] > 0:
                    surface.blit(layer["surface"], (int(layer["scroll_x"] - layer["surface"].get_width()), 0))

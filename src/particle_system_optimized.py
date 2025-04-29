import pygame
import random
import math

class ParticleSystem:
    """
    Système de particules optimisé avec regroupement et rendu par lots
    pour améliorer les performances FPS.
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles = []
        self.max_particles = 200  # Limite le nombre maximum de particules
        self.batch_surfaces = {}  # Cache pour les surfaces de particules
        
    def add_movement_particles(self, x, y, count=5):
        # Limite le nombre de particules si nécessaire
        count = min(count, self.max_particles - len(self.particles))
        if count <= 0:
            return
            
        for _ in range(count):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'size': random.uniform(1, 3),
                'color': (255, 255, 255, random.randint(100, 200)),
                'life': random.randint(10, 30),
                'max_life': 30,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'type': 'movement'
            }
            self.particles.append(particle)
    
    def add_effect_particles(self, x, y, count=20, color=(255, 255, 255)):
        # Limite le nombre de particules si nécessaire
        count = min(count, self.max_particles - len(self.particles))
        if count <= 0:
            return
            
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            particle = {
                'x': x,
                'y': y,
                'size': random.uniform(2, 5),
                'color': (*color, random.randint(150, 255)),
                'life': random.randint(20, 60),
                'max_life': 60,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'type': 'effect'
            }
            self.particles.append(particle)
    
    def update(self):
        # Mise à jour optimisée avec suppression par remplacement
        i = 0
        while i < len(self.particles):
            particle = self.particles[i]
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            # Si la particule est morte ou hors écran, la supprimer
            if (particle['life'] <= 0 or 
                particle['x'] < -50 or particle['x'] > self.screen_width + 50 or
                particle['y'] < -50 or particle['y'] > self.screen_height + 50):
                
                # Remplacer cette particule par la dernière et réduire la taille de la liste
                if i < len(self.particles) - 1:
                    self.particles[i] = self.particles[-1]
                self.particles.pop()
            else:
                i += 1
    
    def _get_particle_surface(self, size, color):
        """Obtenir une surface de particule du cache ou en créer une nouvelle"""
        key = (size, color)
        if key not in self.batch_surfaces:
            particle_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface,
                color,
                (int(size), int(size)),
                int(size)
            )
            self.batch_surfaces[key] = particle_surface
            
            # Limiter la taille du cache
            if len(self.batch_surfaces) > 100:
                # Supprimer une entrée aléatoire
                random_key = random.choice(list(self.batch_surfaces.keys()))
                del self.batch_surfaces[random_key]
                
        return self.batch_surfaces[key]
    
    def draw(self, surface):
        # Regrouper les particules par type pour un rendu par lots
        particle_groups = {}
        
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'][:3], min(particle['color'][3], alpha))
            size = particle['size']
            
            # Arrondir la taille pour réduire le nombre de surfaces uniques
            rounded_size = round(size * 2) / 2
            
            key = (rounded_size, color)
            if key not in particle_groups:
                particle_groups[key] = []
            
            particle_groups[key].append((particle['x'], particle['y']))
        
        # Dessiner chaque groupe de particules avec une seule surface
        for (size, color), positions in particle_groups.items():
            particle_surface = self._get_particle_surface(size, color)
            
            # Dessiner toutes les particules de ce groupe
            for x, y in positions:
                surface.blit(particle_surface, (x - size, y - size))

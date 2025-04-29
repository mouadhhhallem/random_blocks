import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color=(255, 255, 255), size=3, speed=1, life=30, direction=None, alpha=255):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.life = life
        self.max_life = life
        self.alpha = alpha
        
        if direction is None:
            self.direction = random.uniform(0, 2 * math.pi)
        else:
            self.direction = direction
            
        self.dx = math.cos(self.direction) * self.speed
        self.dy = math.sin(self.direction) * self.speed
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.alpha = int(255 * (self.life / self.max_life))
        
    def draw(self, surface):
        if self.alpha > 0:
            particle_color = (*self.color, self.alpha)
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (self.size, self.size), self.size)
            surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))
            
    def is_dead(self):
        return self.life <= 0

class ParticleSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.particle_cache = {}
        
    def add_particles(self, x, y, count, color=(255, 255, 255), size_range=(1, 3), speed_range=(0.5, 2), life_range=(20, 40)):
        for _ in range(count):
            size = random.uniform(size_range[0], size_range[1])
            speed = random.uniform(speed_range[0], speed_range[1])
            life = random.randint(life_range[0], life_range[1])
            self.particles.append(Particle(x, y, color, size, speed, life))
            
    def add_movement_particles(self, x, y, count):
        colors = [(255, 255, 255), (200, 200, 255), (150, 150, 255)]
        for _ in range(count):
            color = random.choice(colors)
            size = random.uniform(1, 2)
            speed = random.uniform(0.3, 1.2)
            life = random.randint(10, 25)
            self.particles.append(Particle(x, y, color, size, speed, life))
            
    def add_effect_particles(self, x, y, count, color):
        for _ in range(count):
            size = random.uniform(1, 3)
            speed = random.uniform(0.5, 2)
            life = random.randint(20, 40)
            direction = random.uniform(0, 2 * math.pi)
            self.particles.append(Particle(x, y, color, size, speed, life, direction))
            
    def add_explosion_particles(self, x, y, count, color_range=None):
        if color_range is None:
            color_range = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]
            
        for _ in range(count):
            color = random.choice(color_range)
            size = random.uniform(1, 4)
            speed = random.uniform(1, 3)
            life = random.randint(20, 50)
            self.particles.append(Particle(x, y, color, size, speed, life))
            
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
                
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)
            
    def get_particle_count(self):
        return len(self.particles)
        
    def clear(self):
        self.particles.clear()
        
    def get_cached_surface(self, key):
        return self.particle_cache.get(key)
        
    def cache_surface(self, key, surface):
        self.particle_cache[key] = surface

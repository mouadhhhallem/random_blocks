import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, size=3, lifetime=60, velocity=None, alpha_decay=True, gravity=0):
        self.x = x
        self.y = y
        self.original_color = color
        self.color = color
        self.size = size
        self.original_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alpha_decay = alpha_decay
        self.gravity = gravity
        
        if velocity is None:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        else:
            self.vx, self.vy = velocity
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        if self.gravity > 0:
            self.vy += self.gravity
        
        self.lifetime -= 1
        
        if self.alpha_decay and self.lifetime > 0:
            alpha_ratio = self.lifetime / self.max_lifetime
            r, g, b = self.original_color
            self.color = (r, g, b, int(255 * alpha_ratio))
            self.size = self.original_size * alpha_ratio
        
        return self.lifetime > 0
    
    def draw(self, surface):
        if self.size <= 0:
            return
            
        if self.alpha_decay:
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                self.color, 
                (self.size, self.size), 
                self.size
            )
            surface.blit(particle_surface, (self.x - self.size, self.y - self.size))
        else:
            pygame.draw.circle(
                surface, 
                self.color, 
                (int(self.x), int(self.y)), 
                int(self.size)
            )

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.effects = {
            'dust': self._create_dust_effect,
            'sparkle': self._create_sparkle_effect,
            'trail': self._create_trail_effect,
            'explosion': self._create_explosion_effect,
            'confetti': self._create_confetti_effect
        }
    
    def add_particle(self, x, y, color, size=3, lifetime=60, velocity=None, alpha_decay=True, gravity=0):
        self.particles.append(Particle(x, y, color, size, lifetime, velocity, alpha_decay, gravity))
    
    def add_effect(self, effect_type, x, y, **kwargs):
        if effect_type in self.effects:
            self.effects[effect_type](x, y, **kwargs)
        else:
            print(f"Unknown effect type: {effect_type}")
    
    def _create_dust_effect(self, x, y, count=5, color=(200, 200, 200), **kwargs):
        for _ in range(count):
            size = random.uniform(1, 3)
            lifetime = random.randint(20, 40)
            velocity = (random.uniform(-0.5, 0.5), random.uniform(-0.2, 0.5))
            self.add_particle(x, y, color, size, lifetime, velocity, True, 0.02)
    
    def _create_sparkle_effect(self, x, y, count=10, color=(255, 255, 100), **kwargs):
        for _ in range(count):
            size = random.uniform(1, 2)
            lifetime = random.randint(10, 30)
            velocity = (random.uniform(-1, 1), random.uniform(-1, 1))
            self.add_particle(x, y, color, size, lifetime, velocity)
    
    def _create_trail_effect(self, x, y, count=3, color=(100, 100, 255), direction=(0, 0), **kwargs):
        vx, vy = direction
        for _ in range(count):
            size = random.uniform(1, 3)
            lifetime = random.randint(10, 20)
            velocity = (-vx * random.uniform(0.5, 1.0) + random.uniform(-0.2, 0.2),
                        -vy * random.uniform(0.5, 1.0) + random.uniform(-0.2, 0.2))
            self.add_particle(x, y, color, size, lifetime, velocity)
    
    def _create_explosion_effect(self, x, y, count=20, color=(255, 100, 50), **kwargs):
        for _ in range(count):
            size = random.uniform(2, 4)
            lifetime = random.randint(30, 60)
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.add_particle(x, y, color, size, lifetime, velocity, True, 0.05)
    
    def _create_confetti_effect(self, x, y, count=30, **kwargs):
        for _ in range(count):
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            size = random.uniform(2, 5)
            lifetime = random.randint(40, 80)
            velocity = (random.uniform(-2, 2), random.uniform(-3, -1))
            self.add_particle(x, y, color, size, lifetime, velocity, True, 0.05)
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)
    
    def clear(self):
        self.particles.clear()

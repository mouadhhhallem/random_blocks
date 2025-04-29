import pygame
import random
import math
import os

class ModernBackground:
    """
    A modern and dynamic background inspired by popular games and platforms like Steam, Epic Games, Twitch, and Kick.
    Features stars, glowing orbs, rotating triangles, and dynamic particles.
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Modern and vibrant color palette
        self.colors = {
            'dark_blue': (18, 30, 49),       # Dark blue (background)
            'medium_blue': (32, 60, 86),     # Medium blue
            'accent_blue': (59, 130, 246),   # Accent blue
            'light_blue': (96, 165, 250),    # Light blue
            'purple': (124, 58, 237),        # Purple (secondary accent)
            'pink': (236, 72, 153),          # Pink (tertiary accent)
            'cyan': (45, 212, 191),          # Cyan (quaternary accent)
            'dark_purple': (91, 33, 182),    # Dark purple
            
            # Particle and effect colors
            'particle1': (59, 130, 246, 150),  # Semi-transparent blue
            'particle2': (124, 58, 237, 150),  # Semi-transparent purple
            'particle3': (236, 72, 153, 150),  # Semi-transparent pink
            'particle4': (45, 212, 191, 150),  # Semi-transparent cyan
            'glow': (255, 255, 255, 30),      # White for glow effects
        }
        
        # Base layers for the background
        self.layers = []
        self.create_base_layers()
        
        # Dynamic elements
        self.particles = []
        self.glows = []
        self.stars = []
        self.create_particles()
        self.create_stars()
        
        # Animation variables
        self.time = 0
        self.wave_offset = 0
        
        # Vignette effect
        self.vignette = self.create_vignette()
        
        # Grid effect
        self.grid = self.create_grid()
        
        # Rotating triangle and glowing orb
        self.triangle_angle = 0  # Angle for rotating triangle
        self.orb_position = [random.randint(0, screen_width), random.randint(0, screen_height)]  # Orb position
        self.orb_trail = []  # Trail for the glowing orb
    
    def create_base_layers(self):
        """Create the base layers for the background."""
        # Layer 1: Gradient background
        gradient = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(self.colors['dark_blue'][0] * (1 - ratio) + self.colors['medium_blue'][0] * ratio)
            g = int(self.colors['dark_blue'][1] * (1 - ratio) + self.colors['medium_blue'][1] * ratio)
            b = int(self.colors['dark_blue'][2] * (1 - ratio) + self.colors['medium_blue'][2] * ratio)
            pygame.draw.line(gradient, (r, g, b), (0, y), (self.screen_width, y))
        self.layers.append(gradient)
        
        # Layer 2: Subtle pattern
        pattern = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for _ in range(300):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            radius = random.randint(1, 3)
            alpha = random.randint(5, 20)
            color = (*self.colors['light_blue'][:3], alpha)
            pygame.draw.circle(pattern, color, (x, y), radius)
        self.layers.append(pattern)
    
    def create_particles(self):
        """Create particles for the background animation."""
        for _ in range(50):
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
                'shape': random.choice(['circle', 'triangle', 'square'])  # Shape variety
            }
            self.particles.append(particle)
        
        # Create glowing points
        for _ in range(10):
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
    
    def create_stars(self):
        """Create a star pattern for the background."""
        star_size = 40
        star_spacing = 70
        
        for x in range(-star_spacing, self.screen_width + star_spacing, star_spacing):
            for y in range(-star_spacing, self.screen_height + star_spacing, star_spacing):
                offset = star_spacing // 2 if (y // star_spacing) % 2 == 0 else 0
                
                star = {
                    'x': x + offset,
                    'y': y,
                    'size': star_size,
                    'color': self.colors['medium_blue'],
                    'outline_color': (*self.colors['accent_blue'][:3], 40),
                    'pulse_speed': random.uniform(0.005, 0.015),
                    'pulse_offset': random.uniform(0, 2 * math.pi)
                }
                self.stars.append(star)
    
    def create_vignette(self):
        """Create a vignette effect for the screen edges."""
        vignette = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for i in range(100):
            alpha = int(i * 1.5)
            pygame.draw.rect(
                vignette,
                (0, 0, 0, alpha),
                (i, i, self.screen_width - 2*i, self.screen_height - 2*i),
                1
            )
        return vignette
    
    def create_grid(self):
        """Create a subtle grid effect."""
        grid = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for y in range(0, self.screen_height, 40):
            pygame.draw.line(grid, (*self.colors['accent_blue'][:3], 15), (0, y), (self.screen_width, y))
        for x in range(0, self.screen_width, 40):
            pygame.draw.line(grid, (*self.colors['accent_blue'][:3], 15), (x, 0), (x, self.screen_height))
        return grid
    
    def draw_star(self, surface, x, y, size, color, outline_color=None):
        """Draw a star at the specified position."""
        points = []
        for i in range(5):
            angle = 2 * math.pi * i / 5 - math.pi / 2
            radius = size if i % 2 == 0 else size // 2
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
        
        if outline_color:
            pygame.draw.polygon(surface, outline_color, points, 2)
        pygame.draw.polygon(surface, color, points)
    
    def update(self, camera_x=0):
        """Update the background animation."""
        self.time += 1
        self.wave_offset = (self.wave_offset + 0.02) % (2 * math.pi)
        
        # Update particles
        for particle in self.particles:
            particle['y'] += particle['speed']
            particle['x'] += math.sin(particle['angle'] + self.time * 0.01) * 0.5
            
            # Reset if off-screen
            if particle['y'] > self.screen_height:
                particle['y'] = 0
                particle['x'] = random.randint(0, self.screen_width)
            
            if particle['x'] < 0 or particle['x'] > self.screen_width:
                particle['x'] = random.randint(0, self.screen_width)
        
        # Update rotating triangle angle
        self.triangle_angle = (self.triangle_angle + 0.02) % (2 * math.pi)
        
        # Update glowing orb position
        self.orb_position[0] += math.cos(self.time * 0.01) * 2
        self.orb_position[1] += math.sin(self.time * 0.01) * 2
        
        # Keep orb within screen bounds
        self.orb_position[0] = max(0, min(self.screen_width, self.orb_position[0]))
        self.orb_position[1] = max(0, min(self.screen_height, self.orb_position[1]))
        
        # Add orb's current position to the trail
        self.orb_trail.append((self.orb_position[0], self.orb_position[1]))
        if len(self.orb_trail) > 20:  # Limit trail length
            self.orb_trail.pop(0)
    
    def draw(self, surface):
        """Draw the complete background on the specified surface."""
        # Draw base layers
        for layer in self.layers:
            surface.blit(layer, (0, 0))
        
        # Draw grid
        surface.blit(self.grid, (0, 0))
        
        # Draw glowing points
        for glow in self.glows:
            pulse = math.sin(self.time * glow['pulse_speed'] + glow['pulse_offset'])
            size = glow['size'] * (0.8 + 0.4 * pulse)
            alpha = glow['alpha'] * (0.7 + 0.3 * pulse)
            
            glow_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            for i in range(int(size)):
                alpha_i = int(alpha * (1 - i/size))
                if alpha_i > 0:
                    pygame.draw.circle(
                        glow_surface,
                        (*glow['color'][:3], alpha_i),
                        (int(size), int(size)),
                        int(size - i)
                    )
            surface.blit(glow_surface, (int(glow['x'] - size), int(glow['y'] - size)))
        
        # Draw stars
        for star in self.stars:
            pulse = 1 + 0.5 * math.sin(self.time * star['pulse_speed'] + star['pulse_offset'])
            self.draw_star(
                surface,
                star['x'],
                star['y'],
                star['size'],
                star['color'],
                (*star['outline_color'][:3], int(star['outline_color'][3] * pulse))
            )
        
        # Draw particles
        for particle in self.particles:
            particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
            if particle['shape'] == 'circle':
                pygame.draw.circle(
                    particle_surface,
                    particle['color'],
                    (int(particle['size']), int(particle['size'])),
                    int(particle['size'])
                )
            elif particle['shape'] == 'triangle':
                points = [
                    (int(particle['size']), 0),
                    (0, int(particle['size'] * 2)),
                    (int(particle['size'] * 2), int(particle['size'] * 2))
                ]
                pygame.draw.polygon(particle_surface, particle['color'], points)
            elif particle['shape'] == 'square':
                pygame.draw.rect(
                    particle_surface,
                    particle['color'],
                    (0, 0, int(particle['size'] * 2), int(particle['size'] * 2))
                )
            surface.blit(particle_surface, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
        
        # Draw vignette
        surface.blit(self.vignette, (0, 0))
        
        # Draw wave lines at the bottom
        wave_height = 5
        wave_count = 3
        wave_spacing = 15
        wave_colors = [
            (*self.colors['accent_blue'][:3], 100),
            (*self.colors['purple'][:3], 80),
            (*self.colors['cyan'][:3], 60)
        ]
        
        for i in range(wave_count):
            points = []
            wave_y = self.screen_height - 50 - i * wave_spacing
            for x in range(0, self.screen_width, 5):
                y = wave_y + math.sin(x * 0.01 + self.wave_offset + i * 0.5) * wave_height
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(surface, wave_colors[i], False, points, 2)
        
        # Draw rotating triangle
        triangle_size = 30
        triangle_color = self.colors['pink']
        pulse = 1 + 0.2 * math.sin(self.time * 0.05)  # Pulsing effect
        center_x, center_y = self.screen_width // 2, self.screen_height // 2
        points = [
            (center_x + triangle_size * pulse * math.cos(self.triangle_angle),
             center_y + triangle_size * pulse * math.sin(self.triangle_angle)),
            (center_x + triangle_size * pulse * math.cos(self.triangle_angle + 2 * math.pi / 3),
             center_y + triangle_size * pulse * math.sin(self.triangle_angle + 2 * math.pi / 3)),
            (center_x + triangle_size * pulse * math.cos(self.triangle_angle + 4 * math.pi / 3),
             center_y + triangle_size * pulse * math.sin(self.triangle_angle + 4 * math.pi / 3))
        ]
        pygame.draw.polygon(surface, triangle_color, points)
        
        # Draw glowing orb and its trail
        for i, (x, y) in enumerate(self.orb_trail):
            alpha = int(255 * (i / len(self.orb_trail)))  # Fade out the trail
            orb_color = (*self.colors['cyan'][:3], alpha)
            radius = 10 * (i / len(self.orb_trail))
            pygame.draw.circle(surface, orb_color, (int(x), int(y)), int(radius))
        
        # Draw the main orb
        pygame.draw.circle(surface, self.colors['cyan'], (int(self.orb_position[0]), int(self.orb_position[1])), 10)


class EnhancedParallaxBackground:
    """
    An enhanced parallax background with modern visual effects.
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.modern_background = ModernBackground(screen_width, screen_height)
        self.layers = []
        self.create_modern_layers()
        self.time = 0
    
    def create_modern_layers(self):
        """Create parallax layers with a modern style."""
        # Layer 1: Distant stars (very slow)
        stars = pygame.Surface((self.screen_width * 2, self.screen_height), pygame.SRCALPHA)
        for _ in range(200):
            x = random.randint(0, stars.get_width())
            y = random.randint(0, stars.get_height())
            size = random.randint(1, 3)
            alpha = random.randint(100, 255)
            color = (255, 255, 255, alpha)
            pygame.draw.circle(stars, color, (x, y), size)
        self.layers.append({"surface": stars, "speed": 0.05})
        
        # Layer 2: Stylized clouds (slow)
        clouds = pygame.Surface((self.screen_width * 3, self.screen_height), pygame.SRCALPHA)
        for _ in range(15):
            x = random.randint(0, clouds.get_width())
            y = random.randint(0, self.screen_height // 2)
            width = random.randint(200, 400)
            height = random.randint(50, 100)
            alpha = random.randint(10, 30)
            color = (255, 255, 255, alpha)
            cloud_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            for i in range(width // 30):
                cx = random.randint(0, width)
                cy = random.randint(0, height)
                cr = random.randint(30, 60)
                pygame.draw.circle(cloud_surface, color, (cx, cy), cr)
            clouds.blit(cloud_surface, (x, y))
        self.layers.append({"surface": clouds, "speed": 0.1})
        
        # Layer 3: Stylized mountains (medium)
        mountains = pygame.Surface((self.screen_width * 2, self.screen_height), pygame.SRCALPHA)
        mountain_color = (60, 70, 90, 150)
        for i in range(10):
            base_x = i * (mountains.get_width() // 10)
            base_y = self.screen_height - random.randint(100, 300)
            peak_x = base_x + random.randint(-100, 100)
            peak_y = base_y - random.randint(150, 250)
            points = [
                (base_x - 200, self.screen_height),
                (peak_x, peak_y),
                (base_x + 200, self.screen_height)
            ]
            pygame.draw.polygon(mountains, mountain_color, points)
        self.layers.append({"surface": mountains, "speed": 0.3})
        
        # Layer 4: Tree silhouettes (fast)
        trees = pygame.Surface((self.screen_width * 2, self.screen_height), pygame.SRCALPHA)
        tree_color = (30, 40, 50, 200)
        for i in range(30):
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
        self.layers.append({"surface": trees, "speed": 0.5})
    
    def update(self, camera_x):
        """Update the parallax background animation."""
        self.time += 1
        self.modern_background.update(camera_x)
        for layer in self.layers:
            layer["scroll_x"] = -camera_x * layer["speed"]
            layer["scroll_x"] = layer["scroll_x"] % layer["surface"].get_width()
    
    def draw(self, surface):
        """Draw the complete parallax background on the specified surface."""
        self.modern_background.draw(surface)
        for layer in self.layers:
            surface.blit(layer["surface"], (int(layer["scroll_x"]), 0))
            if layer["scroll_x"] + layer["surface"].get_width() < self.screen_width:
                surface.blit(layer["surface"], (int(layer["scroll_x"] + layer["surface"].get_width()), 0))
            if layer["scroll_x"] > 0:
                surface.blit(layer["surface"], (int(layer["scroll_x"] - layer["surface"].get_width()), 0))
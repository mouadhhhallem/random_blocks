import pygame
import os

class ParallaxLayer:
    def __init__(self, surface_or_path, scroll_speed):
        if isinstance(surface_or_path, str):
            try:
                self.image = pygame.image.load(surface_or_path).convert_alpha()
            except (pygame.error, FileNotFoundError) as e:
                print(f"Error loading image: {e}")
                # Create a fallback surface
                self.image = pygame.Surface((800, 600))
                self.image.fill((0, 0, 0))
        else:
            # Use the provided surface directly
            self.image = surface_or_path

        self.scroll_speed = scroll_speed
        self.width = self.image.get_width()
        self.scroll_x = 0

    def update(self, camera_x):
        self.scroll_x = -camera_x * self.scroll_speed
        self.scroll_x = self.scroll_x % self.width

    def draw(self, screen, screen_width):
        screen.blit(self.image, (self.scroll_x, 0))

        if self.scroll_x + self.width < screen_width:
            screen.blit(self.image, (self.scroll_x + self.width, 0))

        if self.scroll_x > 0:
            screen.blit(self.image, (self.scroll_x - self.width, 0))


class ParallaxBackground:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layers = []

        # Try to load images first
        try:
            backgrounds_dir = os.path.join("assets", "backgrounds", "sky")
            if os.path.exists(backgrounds_dir):
                self.add_layer(os.path.join(backgrounds_dir, "sky.png"), 0.0)
                self.add_layer(os.path.join(backgrounds_dir, "clouds.png"), 0.1)
                self.add_layer(os.path.join(backgrounds_dir, "mountains_far.png"), 0.3)
                self.add_layer(os.path.join(backgrounds_dir, "mountains_near.png"), 0.5)
                self.add_layer(os.path.join(backgrounds_dir, "foreground.png"), 0.7)
            else:
                print(f"Background directory not found: {backgrounds_dir}")
                self.add_layer_color((135, 206, 235), 0.0)  # Sky blue
                self.add_layer_color((200, 200, 255), 0.1)  # Light blue (clouds)
                self.add_layer_color((100, 100, 150), 0.3)  # Blue-gray (distant mountains)
                self.add_layer_color((70, 90, 120), 0.5)    # Dark blue (near mountains)
                self.add_layer_color((50, 120, 50), 0.7)    # Green (foreground)
        except Exception as e:
            print(f"Error initializing parallax background: {e}")
            # Use fallback colors in case of error
            self.add_layer_color((135, 206, 235), 0.0)  # Sky blue
            self.add_layer_color((200, 200, 255), 0.1)  # Light blue (clouds)
            self.add_layer_color((100, 100, 150), 0.3)  # Blue-gray (distant mountains)
            self.add_layer_color((70, 90, 120), 0.5)    # Dark blue (near mountains)
            self.add_layer_color((50, 120, 50), 0.7)    # Green (foreground)

    def add_layer(self, image_path, scroll_speed):
        try:
            layer = ParallaxLayer(image_path, scroll_speed)
            self.layers.append(layer)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading parallax layer {image_path}: {e}")
            # Create a fallback colored layer
            self.add_layer_color(self.get_fallback_color(scroll_speed), scroll_speed)

    def add_layer_color(self, color, scroll_speed):
        """Add a solid color layer"""
        surface = pygame.Surface((self.screen_width * 2, self.screen_height))
        surface.fill(color)
        layer = ParallaxLayer(surface, scroll_speed)
        self.layers.append(layer)

    def get_fallback_color(self, scroll_speed):
        """Return a fallback color based on scroll speed"""
        if scroll_speed < 0.1:
            return (135, 206, 235)  # Sky blue
        elif scroll_speed < 0.2:
            return (200, 200, 255)  # Light blue (clouds)
        elif scroll_speed < 0.4:
            return (100, 100, 150)  # Blue-gray (distant mountains)
        elif scroll_speed < 0.6:
            return (70, 90, 120)    # Dark blue (near mountains)
        else:
            return (50, 120, 50)    # Green (foreground)

    def update(self, camera_x):
        for layer in self.layers:
            layer.update(camera_x)

    def draw(self, screen):
        screen.fill((0, 0, 0))

        for layer in self.layers:
            layer.draw(screen, self.screen_width)
"""
Explosion entity for Space Invaders game.
Handles explosion animation and rendering.
"""

import pygame
from typing import Tuple

class Explosion:
    """Explosion effect entity."""
    
    def __init__(self, config, position: Tuple[int, int]):
        """Initialize an explosion."""
        self.config = config
        self.position = position
        self.timer = 0
        self.max_timer = config.EXPLOSION_DURATION
        self.finished = False
        
        # Create explosion sprite
        self.image = pygame.Surface((30, 30))
        self.image.fill(self.config.BACKGROUND_COLOR)
    
    def update(self):
        """Update explosion animation."""
        self.timer += 1
        if self.timer >= self.max_timer:
            self.finished = True
    
    def is_finished(self) -> bool:
        """Check if explosion animation is finished."""
        return self.finished
    
    def render(self, screen):
        """Render the explosion on screen."""
        if not self.finished:
            # Create animated explosion effect
            explosion_size = int(20 * (self.timer / self.max_timer))
            explosion_surface = pygame.Surface((explosion_size * 2, explosion_size * 2))
            explosion_surface.fill(self.config.BACKGROUND_COLOR)
            
            # Draw explosion rings
            for i in range(3):
                radius = explosion_size - i * 5
                if radius > 0:
                    color_intensity = 255 - (i * 80)
                    color = (color_intensity, color_intensity // 2, 0)
                    pygame.draw.circle(explosion_surface, color, 
                                    (explosion_size, explosion_size), radius, 2)
            
            # Blit explosion at position
            explosion_rect = explosion_surface.get_rect()
            explosion_rect.center = self.position
            screen.blit(explosion_surface, explosion_rect)

"""
Bullet entity for Space Invaders game.
Handles bullet movement and rendering.
"""

import pygame
from typing import Tuple

class Bullet:
    """Bullet entity."""
    
    def __init__(self, config, x: int, y: int, direction: int = -1):
        """Initialize a bullet.
        
        Args:
            config: Game configuration
            x: Starting x position
            y: Starting y position
            direction: -1 for player bullets (up), 1 for invader bullets (down)
        """
        self.config = config
        self.width = config.BULLET_WIDTH
        self.height = config.BULLET_HEIGHT
        self.direction = direction
        self.speed = config.BULLET_SPEED
        
        # Create bullet sprite
        self.image = pygame.Surface((self.width, self.height))
        if direction == -1:  # Player bullet
            self.image.fill(config.PLAYER_BULLET_COLOR)
        else:  # Invader bullet
            self.image.fill(config.INVADER_BULLET_COLOR)
        
        self.rect = self.image.get_rect()
        self.rect.x = x - self.width // 2
        self.rect.y = y
    
    def update(self):
        """Update bullet position."""
        self.rect.y += self.direction * self.speed
    
    def is_off_screen(self) -> bool:
        """Check if bullet is off screen."""
        return (self.rect.bottom < 0 or 
                self.rect.top > self.config.SCREEN_HEIGHT or
                self.rect.right < 0 or 
                self.rect.left > self.config.SCREEN_WIDTH)
    
    def render(self, screen):
        """Render the bullet on screen."""
        screen.blit(self.image, self.rect)

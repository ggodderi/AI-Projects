"""
Bomb entity for Space Invaders game.
Handles invader bombs that drop down toward the player.
"""

import pygame
import random
from typing import Tuple

class Bomb:
    """Bomb entity dropped by invaders."""
    
    def __init__(self, config, x: int, y: int):
        """Initialize a bomb."""
        self.config = config
        self.width = 6
        self.height = 8
        self.speed = 3
        
        # Create bomb sprite
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.config.BACKGROUND_COLOR)
        
        # Draw bomb shape
        pygame.draw.ellipse(self.image, self.config.RED, (1, 1, 4, 6), 2)
        pygame.draw.line(self.image, self.config.YELLOW, (3, 0), (3, 2), 1)  # Fuse
        
        self.rect = self.image.get_rect()
        self.rect.x = x - self.width // 2
        self.rect.y = y
    
    def update(self):
        """Update bomb position."""
        self.rect.y += self.speed
    
    def is_off_screen(self) -> bool:
        """Check if bomb is off screen."""
        return (self.rect.top > self.config.SCREEN_HEIGHT or
                self.rect.right < 0 or 
                self.rect.left > self.config.SCREEN_WIDTH)
    
    def render(self, screen):
        """Render the bomb on screen."""
        screen.blit(self.image, self.rect)


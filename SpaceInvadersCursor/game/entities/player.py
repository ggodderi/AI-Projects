"""
Player entity for Space Invaders game.
Handles player movement, rendering, and input.
"""

import pygame
from typing import Tuple

class Player:
    """Player/ship entity."""
    
    def __init__(self, config):
        """Initialize the player."""
        self.config = config
        self.width = config.PLAYER_WIDTH
        self.height = config.PLAYER_HEIGHT
        
        # Create player sprite (simple rectangle for now)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(config.WHITE)
        
        # Create rectangular outline for authentic look
        pygame.draw.rect(self.image, config.WHITE, (0, 0, self.width, self.height), 2)
        pygame.draw.polygon(self.image, config.WHITE, [
            (self.width//2, self.height-5),  # Bottom center
            (self.width//2-10, self.height-15),  # Left wing
            (self.width//2+10, self.height-15)   # Right wing
        ])
        
        self.rect = self.image.get_rect()
        self.rect.x = config.PLAYER_START_X
        self.rect.y = config.PLAYER_START_Y
        
        self.speed = config.PLAYER_SPEED
        self.moving_left = False
        self.moving_right = False
    
    def update(self):
        """Update player position."""
        # Handle movement
        keys = pygame.key.get_pressed()
        self.moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        if self.moving_left and self.rect.left > 0:
            self.rect.x -= self.speed
        if self.moving_right and self.rect.right < self.config.SCREEN_WIDTH:
            self.rect.x += self.speed
    
    def render(self, screen):
        """Render the player on screen."""
        screen.blit(self.image, self.rect)
    
    def get_shoot_position(self) -> Tuple[int, int]:
        """Get the position where bullets should be fired from."""
        return (self.rect.centerx, self.rect.top)

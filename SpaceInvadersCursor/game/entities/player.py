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
        
        # Create player sprite (tank/gun design)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(config.BACKGROUND_COLOR)
        
        # Draw tank body (rectangular base) - adjusted for smaller width
        pygame.draw.rect(self.image, config.WHITE, (3, 20, self.width-6, 15), 2)
        
        # Draw tank tracks (bottom)
        pygame.draw.rect(self.image, config.WHITE, (1, 32, self.width-2, 6), 1)
        
        # Draw gun turret (top part) - smaller to fit
        pygame.draw.rect(self.image, config.WHITE, (self.width//2-6, 8, 12, 12), 2)
        
        # Draw gun barrel (extending upward)
        pygame.draw.rect(self.image, config.WHITE, (self.width//2-2, 0, 4, 12), 2)
        
        # Draw gun muzzle (tip)
        pygame.draw.rect(self.image, config.WHITE, (self.width//2-3, 0, 6, 4), 2)
        
        # Draw side details (tank features) - smaller details
        pygame.draw.rect(self.image, config.WHITE, (5, 22, 4, 6), 1)  # Left detail
        pygame.draw.rect(self.image, config.WHITE, (self.width-9, 22, 4, 6), 1)  # Right detail
        
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

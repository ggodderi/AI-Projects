"""
Invader entities for Space Invaders game.
Handles invader sprites, movement patterns, and group management.
"""

import pygame
import random
from typing import List, Optional
from .player import Player

class Invader:
    """Individual invader entity."""
    
    def __init__(self, config, x: int, y: int, invader_type: int = 0):
        """Initialize an invader."""
        self.config = config
        self.width = config.INVADER_WIDTH
        self.height = config.INVADER_HEIGHT
        self.invader_type = invader_type
        
        # Create invader sprite based on type
        self.image = self.create_invader_sprite()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Points for destroying this invader
        self.points = self.get_points_for_type()
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
    
    def create_invader_sprite(self) -> pygame.Surface:
        """Create the invader sprite."""
        image = pygame.Surface((self.width, self.height))
        image.fill(self.config.BACKGROUND_COLOR)
        
        # Draw different invader types
        if self.invader_type == 0:  # Top row - most points
            self.draw_top_invader(image)
        elif self.invader_type == 1:  # Middle rows
            self.draw_middle_invader(image)
        else:  # Bottom rows - least points
            self.draw_bottom_invader(image)
        
        return image
    
    def draw_top_invader(self, image):
        """Draw the top invader sprite (octopus-like)."""
        pygame.draw.rect(image, self.config.WHITE, (5, 5, 30, 20), 2)
        pygame.draw.circle(image, self.config.WHITE, (10, 10), 3)
        pygame.draw.circle(image, self.config.WHITE, (30, 10), 3)
        pygame.draw.rect(image, self.config.WHITE, (15, 15, 10, 5))
    
    def draw_middle_invader(self, image):
        """Draw the middle invader sprite (crab-like)."""
        pygame.draw.rect(image, self.config.WHITE, (8, 8, 24, 16), 2)
        pygame.draw.rect(image, self.config.WHITE, (5, 12, 8, 4))
        pygame.draw.rect(image, self.config.WHITE, (27, 12, 8, 4))
        pygame.draw.rect(image, self.config.WHITE, (18, 20, 4, 6))
    
    def draw_bottom_invader(self, image):
        """Draw the bottom invader sprite (squid-like)."""
        pygame.draw.rect(image, self.config.WHITE, (10, 10, 20, 15), 2)
        pygame.draw.rect(image, self.config.WHITE, (8, 8, 4, 4))
        pygame.draw.rect(image, self.config.WHITE, (28, 8, 4, 4))
        pygame.draw.rect(image, self.config.WHITE, (18, 22, 4, 6))
    
    def get_points_for_type(self) -> int:
        """Get points awarded for destroying this invader type."""
        if self.invader_type == 0:
            return 30
        elif self.invader_type == 1:
            return 20
        else:
            return 10
    
    def update(self):
        """Update invader animation."""
        self.animation_timer += 1
        if self.animation_timer >= 30:  # Change animation every 30 frames
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
            # Redraw sprite with animation
            self.image = self.create_invader_sprite()
    
    def render(self, screen):
        """Render the invader on screen."""
        screen.blit(self.image, self.rect)

class InvaderGroup:
    """Group of invaders with movement patterns."""
    
    def __init__(self, config, level: int):
        """Initialize invader group."""
        self.config = config
        self.level = level
        self.invaders: List[Invader] = []
        self.direction = 1  # 1 for right, -1 for left
        self.speed = config.INVADER_SPEED_BASE + (level - 1) * config.INVADER_SPEED_INCREMENT
        self.drop_timer = 0
        self.last_drop_time = 0
        
        self.create_invaders()
    
    def create_invaders(self):
        """Create the initial formation of invaders."""
        start_x = self.config.INVADER_START_X
        start_y = self.config.INVADER_START_Y
        
        for row in range(self.config.INVADER_ROWS):
            for col in range(self.config.INVADER_COLS):
                x = start_x + col * self.config.INVADER_SPACING_X
                y = start_y + row * self.config.INVADER_SPACING_Y
                
                # Determine invader type based on row
                if row == 0:
                    invader_type = 0
                elif row < 3:
                    invader_type = 1
                else:
                    invader_type = 2
                
                invader = Invader(self.config, x, y, invader_type)
                self.invaders.append(invader)
    
    def update(self):
        """Update all invaders and handle group movement."""
        if not self.invaders:
            return
        
        # Update individual invaders
        for invader in self.invaders:
            invader.update()
        
        # Handle group movement
        self.update_group_movement()
        
        # Speed up as invaders are destroyed (more gradual increase)
        remaining_invaders = len(self.invaders)
        total_invaders = self.config.INVADER_ROWS * self.config.INVADER_COLS
        speed_multiplier = 1 + (total_invaders - remaining_invaders) * 0.05  # Reduced from 0.1 to 0.05
        current_speed = self.speed * speed_multiplier
        
        # Move invaders horizontally
        for invader in self.invaders:
            invader.rect.x += self.direction * current_speed
    
    def update_group_movement(self):
        """Update the group's movement direction and dropping."""
        if not self.invaders:
            return
        
        # Check if any invader hit the screen edge
        leftmost_x = min(invader.rect.left for invader in self.invaders)
        rightmost_x = max(invader.rect.right for invader in self.invaders)
        
        should_drop = False
        
        if self.direction == 1 and rightmost_x >= self.config.SCREEN_WIDTH - 20:
            self.direction = -1
            should_drop = True
        elif self.direction == -1 and leftmost_x <= 20:
            self.direction = 1
            should_drop = True
        
        # Drop invaders down
        if should_drop:
            for invader in self.invaders:
                invader.rect.y += self.config.INVADER_DROP_DISTANCE
    
    def check_collision(self, bullet) -> Optional[Invader]:
        """Check if any invader collides with the given bullet."""
        for invader in self.invaders:
            if invader.rect.colliderect(bullet.rect):
                self.invaders.remove(invader)
                return invader
        return None
    
    def check_player_collision(self, player: Player) -> bool:
        """Check if any invader collides with the player."""
        for invader in self.invaders:
            if invader.rect.colliderect(player.rect):
                return True
        return False
    
    def has_reached_bottom(self) -> bool:
        """Check if any invader has reached the bottom of the screen."""
        for invader in self.invaders:
            if invader.rect.bottom >= self.config.SCREEN_HEIGHT - 50:
                return True
        return False
    
    def is_empty(self) -> bool:
        """Check if all invaders are destroyed."""
        return len(self.invaders) == 0
    
    def render(self, screen):
        """Render all invaders."""
        for invader in self.invaders:
            invader.render(screen)

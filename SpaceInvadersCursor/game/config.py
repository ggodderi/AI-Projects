"""
Game Configuration
Central configuration file for all game constants and settings.
"""

import pygame

class GameConfig:
    """Configuration class containing all game constants."""
    
    # Screen dimensions
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    
    # Colors (RGB)
    BACKGROUND_COLOR = (0, 0, 0)  # Black
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    
    # Game settings
    FPS = 60
    MAX_BULLETS = 5
    BULLETS_PER_LEVEL = 170
    MAX_LEVELS = 12
    
    # Player settings
    PLAYER_WIDTH = 40  # Reduced from 60 to match invader width
    PLAYER_HEIGHT = 40
    PLAYER_SPEED = 5
    PLAYER_START_X = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
    PLAYER_START_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 20
    
    # Invader settings
    INVADER_WIDTH = 40
    INVADER_HEIGHT = 30
    INVADER_ROWS = 5
    INVADER_COLS = 8  # Reduced from 11 to 8 for easier first level
    INVADER_SPACING_X = 60
    INVADER_SPACING_Y = 50
    INVADER_START_X = 50
    INVADER_START_Y = 100
    INVADER_SPEED_BASE = 0.5  # Reduced from 1 to 0.5 for slower movement
    INVADER_SPEED_INCREMENT = 0.3  # Reduced from 0.5 to 0.3 for gentler progression
    INVADER_DROP_DISTANCE = 30
    
    # Bullet settings
    BULLET_WIDTH = 4
    BULLET_HEIGHT = 10
    BULLET_SPEED = 7
    PLAYER_BULLET_COLOR = GREEN
    INVADER_BULLET_COLOR = RED
    
    # Explosion settings
    EXPLOSION_DURATION = 20  # frames
    
    # Font settings
    FONT_SIZE_LARGE = 48
    FONT_SIZE_MEDIUM = 24
    FONT_SIZE_SMALL = 18
    
    def __init__(self):
        """Initialize configuration."""
        pygame.font.init()
        self.font_large = pygame.font.Font(None, self.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, self.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, self.FONT_SIZE_SMALL)

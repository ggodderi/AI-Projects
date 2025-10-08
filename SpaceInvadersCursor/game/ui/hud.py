"""
Heads-Up Display for Space Invaders game.
Displays score, level, bullets remaining, and other game information.
"""

import pygame

class HUD:
    """Heads-Up Display class."""
    
    def __init__(self, config):
        """Initialize the HUD."""
        self.config = config
        self.font = config.font_medium
    
    def render(self, screen, score: int, level: int, bullets_remaining: int):
        """Render the HUD on screen."""
        # Score
        score_text = self.font.render(f"SCORE: {score:06d}", True, self.config.WHITE)
        screen.blit(score_text, (10, 10))
        
        # Level
        level_text = self.font.render(f"LEVEL: {level}", True, self.config.WHITE)
        screen.blit(level_text, (10, 40))
        
        # Bullets remaining
        bullets_text = self.font.render(f"BULLETS: {bullets_remaining}", True, self.config.WHITE)
        screen.blit(bullets_text, (10, 70))
        
        # Lives (if implemented)
        lives_text = self.font.render("LIVES: 1", True, self.config.WHITE)
        screen.blit(lives_text, (self.config.SCREEN_WIDTH - 120, 10))
        
        # High score placeholder
        high_score_text = self.font.render("HIGH: 000000", True, self.config.WHITE)
        screen.blit(high_score_text, (self.config.SCREEN_WIDTH - 150, 40))

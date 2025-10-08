"""
Game Over screen for Space Invaders game.
Handles game over display and restart options.
"""

import pygame

class GameOverScreen:
    """Game Over screen class."""
    
    def __init__(self, config):
        """Initialize the game over screen."""
        self.config = config
        self.font_large = config.font_large
        self.font_medium = config.font_medium
        self.font_small = config.font_small
    
    def render(self, screen, final_score: int, final_level: int):
        """Render the game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        overlay.fill(self.config.BACKGROUND_COLOR)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER", True, self.config.RED)
        game_over_rect = game_over_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 200))
        screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {final_score:06d}", True, self.config.WHITE)
        score_rect = score_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 280))
        screen.blit(score_text, score_rect)
        
        # Level reached
        level_text = self.font_medium.render(f"Level Reached: {final_level}", True, self.config.WHITE)
        level_rect = level_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 320))
        screen.blit(level_text, level_rect)
        
        # Play again prompt
        play_again_text = self.font_medium.render("Play Again? (Y/N)", True, self.config.YELLOW)
        play_again_rect = play_again_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 400))
        screen.blit(play_again_text, play_again_rect)
        
        # Instructions
        instructions_text = self.font_small.render("Press Y to restart or N to quit", True, self.config.WHITE)
        instructions_rect = instructions_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 450))
        screen.blit(instructions_text, instructions_rect)

"""
Space Invaders Game Engine
Main game class that handles the game loop, rendering, and overall game state.
"""

import pygame
import sys
import threading
import time
from typing import List, Tuple
from .entities.player import Player
from .entities.invader import Invader, InvaderGroup
from .entities.bullet import Bullet
from .entities.explosion import Explosion
from .ui.hud import HUD
from .ui.game_over_screen import GameOverScreen
from .audio.sound_manager import SoundManager
from .config import GameConfig

class SpaceInvadersGame:
    """Main game class for Space Invaders."""
    
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        pygame.mixer.init()
        
        self.config = GameConfig()
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.level = 1
        self.score = 0
        self.bullets_remaining = self.config.BULLETS_PER_LEVEL
        
        # Initialize game components
        self.player = Player(self.config)
        self.invader_group = InvaderGroup(self.config, self.level)
        self.bullets: List[Bullet] = []
        self.explosions: List[Explosion] = []
        self.hud = HUD(self.config)
        self.game_over_screen = GameOverScreen(self.config)
        self.sound_manager = SoundManager()
        
        # Performance tracking
        self.last_frame_time = time.time()
        self.frame_count = 0
        
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            if not self.game_over:
                self.update()
            self.render()
            self.clock.tick(self.config.FPS)
            
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    self.handle_game_over_input(event.key)
                else:
                    self.handle_game_input(event.key)
            elif event.type == pygame.KEYUP and not self.game_over:
                self.handle_key_release(event.key)
    
    def handle_game_input(self, key):
        """Handle input during gameplay."""
        if key == pygame.K_SPACE and len(self.bullets) < self.config.MAX_BULLETS and self.bullets_remaining > 0:
            self.shoot_bullet()
        elif key == pygame.K_ESCAPE:
            self.running = False
    
    def handle_key_release(self, key):
        """Handle key release events."""
        pass
    
    def handle_game_over_input(self, key):
        """Handle input on game over screen."""
        if key == pygame.K_y:
            self.restart_game()
        elif key == pygame.K_n:
            self.running = False
    
    def update(self):
        """Update game state."""
        # Update player
        self.player.update()
        
        # Update invaders
        self.invader_group.update()
        
        # Update bullets
        self.update_bullets()
        
        # Update explosions
        self.update_explosions()
        
        # Check collisions
        self.check_collisions()
        self.check_bomb_collisions()
        
        # Check game over conditions
        self.check_game_over()
        
        # Check level completion
        self.check_level_completion()
    
    def update_bullets(self):
        """Update all bullets."""
        bullets_to_remove = []
        
        for bullet in self.bullets:
            bullet.update()
            if bullet.is_off_screen():
                bullets_to_remove.append(bullet)
        
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
    
    def update_explosions(self):
        """Update all explosions."""
        explosions_to_remove = []
        
        for explosion in self.explosions:
            explosion.update()
            if explosion.is_finished():
                explosions_to_remove.append(explosion)
        
        for explosion in explosions_to_remove:
            self.explosions.remove(explosion)
    
    def shoot_bullet(self):
        """Create a new bullet."""
        bullet = Bullet(self.config, self.player.rect.centerx, self.player.rect.top)
        self.bullets.append(bullet)
        self.bullets_remaining -= 1
        self.sound_manager.play_shot_sound()
    
    def check_collisions(self):
        """Check for collisions between bullets and invaders/bombs."""
        bullets_to_remove = []
        
        for bullet in self.bullets:
            # Check collision with invaders
            hit_invader = self.invader_group.check_collision(bullet)
            if hit_invader:
                bullets_to_remove.append(bullet)
                self.score += hit_invader.points
                self.create_explosion(hit_invader.rect.center)
                self.sound_manager.play_hit_sound()
            else:
                # Check collision with bombs
                hit_bomb = self.invader_group.check_bullet_bomb_collision(bullet)
                if hit_bomb:
                    bullets_to_remove.append(bullet)
                    self.create_explosion(hit_bomb.rect.center)
                    self.sound_manager.play_hit_sound()
        
        # Remove hit bullets
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
    
    def check_bomb_collisions(self):
        """Check for collisions between bombs and player."""
        if self.invader_group.check_bomb_collision(self.player):
            self.game_over = True
    
    def create_explosion(self, position):
        """Create an explosion at the given position."""
        explosion = Explosion(self.config, position)
        self.explosions.append(explosion)
    
    def check_game_over(self):
        """Check if the game should end."""
        # Check if invaders reached the bottom
        if self.invader_group.has_reached_bottom():
            self.game_over = True
            return
        
        # Check if invaders hit the player
        if self.invader_group.check_player_collision(self.player):
            self.game_over = True
            return
        
        # Check if bullets are exhausted and invaders are still alive
        if self.bullets_remaining <= 0 and len(self.bullets) == 0 and not self.invader_group.is_empty():
            self.game_over = True
    
    def check_level_completion(self):
        """Check if the current level is completed."""
        if self.invader_group.is_empty():
            self.level += 1
            if self.level <= self.config.MAX_LEVELS:
                self.bullets_remaining = self.config.BULLETS_PER_LEVEL
                self.invader_group = InvaderGroup(self.config, self.level)
            else:
                # Game completed - all levels beaten
                self.game_over = True
    
    def restart_game(self):
        """Restart the game."""
        self.game_over = False
        self.level = 1
        self.score = 0
        self.bullets_remaining = self.config.BULLETS_PER_LEVEL
        
        self.player = Player(self.config)
        self.invader_group = InvaderGroup(self.config, self.level)
        self.bullets.clear()
        self.explosions.clear()
    
    def render(self):
        """Render the game."""
        # Clear screen
        self.screen.fill(self.config.BACKGROUND_COLOR)
        
        if self.game_over:
            self.game_over_screen.render(self.screen, self.score, self.level)
        else:
            # Render game objects
            self.player.render(self.screen)
            self.invader_group.render(self.screen)
            
            for bullet in self.bullets:
                bullet.render(self.screen)
            
            for explosion in self.explosions:
                explosion.render(self.screen)
            
            # Render HUD
            self.hud.render(self.screen, self.score, self.level, self.bullets_remaining)
        
        pygame.display.flip()

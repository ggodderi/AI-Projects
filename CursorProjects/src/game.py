import pygame

import random

from config import (
	SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE,
	BOMB_SPAWN_INTERVAL_BASE, BOMB_MAX_COUNT_BASE, BOMB_MAX_COUNT_PER_WAVE,
	STARTING_LIVES,
)
from src.game_state import GameState, GameStateManager
from src.player import Player
from src.bullet import Bullet
from src.bomb import Bomb
from src.formation import InvaderFormation


class Game:
	def __init__(self) -> None:
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()
		self.state = GameStateManager()
		self.running = True
		pygame.font.init()
		self.font_large = pygame.font.Font(None, 72)
		self.font_medium = pygame.font.Font(None, 36)
		self.font_small = pygame.font.Font(None, 24)
		
		# Game objects
		self.player: Player | None = None
		self.bullets: pygame.sprite.Group = pygame.sprite.Group()
		self.bombs: pygame.sprite.Group = pygame.sprite.Group()
		self.formation: InvaderFormation | None = None
		self.score = 0
		self.wave = 1
		
		# Bomb spawning
		self.bomb_spawn_timer = 0.0

	def init_game(self, reset_score: bool = False) -> None:
		"""Initialize/reset game objects when entering PLAYING state"""
		if reset_score or self.player is None:
			# New game - reset everything
			if self.player is None:
				self.player = Player()
			else:
				self.player.lives = STARTING_LIVES
			self.score = 0
			self.wave = 1
		else:
			# Respawn - just reset position
			self.player.rect.centerx = SCREEN_WIDTH // 2
			self.player.rect.bottom = SCREEN_HEIGHT - 40
			self.player.invulnerable = False
			self.player.invulnerability_timer = 0.0
		
		self.bullets.empty()
		self.bombs.empty()
		self.bomb_spawn_timer = 0.0
		# Create formation at top of screen (centered, with margins)
		formation_start_x = SCREEN_WIDTH // 2 - (11 * 50) // 2 + 25  # Center the formation
		formation_start_y = 50
		self.formation = InvaderFormation(formation_start_x, formation_start_y)
	
	def get_max_bombs(self) -> int:
		"""Calculate max active bombs based on wave and remaining invaders."""
		if not self.formation:
			return 0
		remaining = self.formation.get_invader_count()
		# More invaders = more bombs allowed
		invader_ratio = remaining / (5 * 11)  # Normalize to 0-1
		base_max = BOMB_MAX_COUNT_BASE + int(invader_ratio * 3)  # 2-5 based on invaders
		return base_max + (self.wave - 1) * BOMB_MAX_COUNT_PER_WAVE
	
	def try_spawn_bomb(self, dt: float) -> None:
		"""Attempt to spawn a bomb from a random front-line invader."""
		if not self.formation:
			return
		
		self.bomb_spawn_timer += dt
		
		# Calculate spawn interval (faster with fewer invaders and higher waves)
		speed_mult = self.formation.get_speed_multiplier()
		spawn_interval = BOMB_SPAWN_INTERVAL_BASE / speed_mult
		
		if self.bomb_spawn_timer >= spawn_interval:
			self.bomb_spawn_timer = 0.0
			
			# Only spawn if under max bombs
			if len(self.bombs) >= self.get_max_bombs():
				return
			
			# Get front-line invaders (eligible to fire)
			front_line = self.formation.get_front_line_invaders()
			if not front_line:
				return
			
			# Pick random front-line invader
			invader = random.choice(front_line)
			
			# Spawn bomb at invader position
			bomb = Bomb(invader.rect.centerx, invader.rect.bottom)
			self.bombs.add(bomb)
	
	def handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				if self.state.current == GameState.TITLE:
					if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
						self.init_game(reset_score=True)  # Reset score when starting new game
						self.state.set_state(GameState.PLAYING)
				elif self.state.current == GameState.PLAYING:
					if event.key == pygame.K_p:
						self.state.set_state(GameState.PAUSED)
					elif event.key == pygame.K_SPACE:
						# Fire bullet
						if self.player and self.player.can_fire(len(self.bullets)):
							x, y = self.player.get_spawn_position()
							bullet = Bullet(x, y)
							self.bullets.add(bullet)
				elif self.state.current == GameState.PAUSED:
					if event.key == pygame.K_p:
						self.state.set_state(GameState.PLAYING)
					elif event.key == pygame.K_ESCAPE:
						self.state.set_state(GameState.TITLE)
				elif self.state.current == GameState.GAME_OVER:
					if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
						self.state.set_state(GameState.TITLE)

	def update(self, dt: float) -> None:
		if self.state.current == GameState.PLAYING:
			if self.player:
				keys = pygame.key.get_pressed()
				self.player.update(dt, keys)
			
			self.bullets.update(dt)
			self.bombs.update(dt)
			
			if self.formation:
				self.formation.update(dt)
				
				# Try to spawn bombs
				self.try_spawn_bomb(dt)
				
				# Check for bullet-invader collisions
				for bullet in self.bullets:
					for invader in self.formation.get_all_invaders():
						if bullet.rect.colliderect(invader.rect):
							# Hit! Remove invader and bullet, award points
							self.score += invader.points
							self.formation.remove_invader(invader)
							bullet.kill()
							break  # Each bullet only hits one invader
				
				# Check for bomb-player collisions
				if self.player and not self.player.invulnerable:
					for bomb in self.bombs:
						if bomb.rect.colliderect(self.player.rect):
							# Player hit! Lose life
							self.player.lives -= 1
							bomb.kill()
							if self.player.lives > 0:
								# Respawn with invulnerability
								self.player.rect.centerx = SCREEN_WIDTH // 2
								self.player.rect.bottom = SCREEN_HEIGHT - 40
								self.player.invulnerable = True
								self.player.invulnerability_timer = 2.0  # 2 seconds invulnerable
								self.bullets.empty()  # Clear bullets on death
							else:
								# Game over
								self.state.set_state(GameState.GAME_OVER)
							break
				
				# Check if all invaders destroyed
				if self.formation.get_invader_count() == 0:
					# Wave cleared - advance to next wave
					self.wave += 1
					formation_start_x = SCREEN_WIDTH // 2 - (11 * 50) // 2 + 25
					self.formation = InvaderFormation(formation_start_x, 50)
					self.bombs.empty()  # Clear any remaining bombs
				
				# Check if invaders reached player
				if self.player and not self.player.invulnerable:
					if self.formation.check_descend_limit(self.player.rect.top):
						# Invaders reached player - lose life
						self.player.lives -= 1
						if self.player.lives > 0:
							# Respawn with invulnerability
							self.player.invulnerable = True
							self.player.invulnerability_timer = 2.0
							self.init_game()
						else:
							# Game over
							self.state.set_state(GameState.GAME_OVER)

	def render_title(self) -> None:
		self.screen.fill(BLACK)
		title_text = self.font_large.render("SPACE INVADERS", True, WHITE)
		title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
		self.screen.blit(title_text, title_rect)
		
		start_text = self.font_medium.render("Press SPACE or ENTER to Start", True, WHITE)
		start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
		self.screen.blit(start_text, start_rect)
		
		controls_text = self.font_small.render("Arrow Keys: Move | SPACE: Fire | P: Pause | ESC: Quit", True, WHITE)
		controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
		self.screen.blit(controls_text, controls_rect)

	def render_playing(self) -> None:
		self.screen.fill(BLACK)
		
		# Render invaders
		if self.formation:
			for invader in self.formation.get_all_invaders():
				self.screen.blit(invader.image, invader.rect)
		
		# Render bullets
		self.bullets.draw(self.screen)
		
		# Render bombs
		self.bombs.draw(self.screen)
		
		# Render player (flash if invulnerable)
		if self.player:
			if not self.player.invulnerable or int(self.player.invulnerability_timer * 10) % 2 == 0:
				self.screen.blit(self.player.image, self.player.rect)
		
		# Render score (simple text for now, HUD will be added later)
		score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
		self.screen.blit(score_text, (10, 10))
		
		# Render lives
		if self.player:
			lives_text = self.font_small.render(f"Lives: {self.player.lives}", True, WHITE)
			self.screen.blit(lives_text, (10, 35))
		
		# Render wave
		wave_text = self.font_small.render(f"Wave: {self.wave}", True, WHITE)
		self.screen.blit(wave_text, (10, 60))

	def render_paused(self) -> None:
		# Semi-transparent overlay on top of game
		overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		overlay.set_alpha(128)
		overlay.fill(BLACK)
		self.screen.blit(overlay, (0, 0))
		
		paused_text = self.font_large.render("PAUSED", True, WHITE)
		paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
		self.screen.blit(paused_text, paused_rect)
		
		resume_text = self.font_small.render("Press P to Resume | ESC to Return to Title", True, WHITE)
		resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
		self.screen.blit(resume_text, resume_rect)
	
	def render_game_over(self) -> None:
		self.screen.fill(BLACK)
		game_over_text = self.font_large.render("GAME OVER", True, WHITE)
		game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
		self.screen.blit(game_over_text, game_over_rect)
		
		score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
		score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
		self.screen.blit(score_text, score_rect)
		
		restart_text = self.font_small.render("Press SPACE or ENTER to Return to Title", True, WHITE)
		restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
		self.screen.blit(restart_text, restart_rect)

	def render(self) -> None:
		if self.state.current == GameState.TITLE:
			self.render_title()
		elif self.state.current == GameState.PLAYING:
			self.render_playing()
		elif self.state.current == GameState.PAUSED:
			self.render_playing()  # Show game underneath
			self.render_paused()  # Then overlay pause
		elif self.state.current == GameState.GAME_OVER:
			self.render_game_over()
		else:
			self.screen.fill(BLACK)
		
		pygame.display.flip()

	def run(self) -> None:
		while self.running:
			dt = self.clock.tick(FPS) / 1000.0
			self.handle_events()
			self.update(dt)
			self.render()

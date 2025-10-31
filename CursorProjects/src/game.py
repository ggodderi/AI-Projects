import pygame

import random

from config import (
	SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE,
	BOMB_SPAWN_INTERVAL_BASE, BOMB_MAX_COUNT_BASE, BOMB_MAX_COUNT_PER_WAVE,
	STARTING_LIVES, BUNKER_COUNT, BUNKER_WIDTH,
	EXTRA_LIFE_SCORE, SAUCER_SPAWN_INTERVAL_MIN, SAUCER_SPAWN_INTERVAL_MAX,
)
from src.game_state import GameState, GameStateManager
from src.player import Player
from src.bullet import Bullet
from src.bomb import Bomb
from src.bunker import Bunker
from src.saucer import Saucer
from src.formation import InvaderFormation
from src.audio_manager import AudioManager
from src.high_scores import load_high_scores, submit_score
from src.settings import load_settings


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
		self.bunkers: list[Bunker] = []
		self.saucer: Saucer | None = None
		self.formation: InvaderFormation | None = None
		self.score = 0
		self.wave = 1
		self.next_extra_life_score = EXTRA_LIFE_SCORE
		self.high_scores = load_high_scores()
		
		# Audio
		settings = load_settings()
		self.audio = AudioManager(settings.get("audio", {}).get("volume", 0.7))
		
		# Spawning timers
		self.bomb_spawn_timer = 0.0
		self.saucer_spawn_timer = 0.0
		self.next_saucer_interval = random.uniform(SAUCER_SPAWN_INTERVAL_MIN, SAUCER_SPAWN_INTERVAL_MAX)

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
		self.saucer = None
		self.saucer_spawn_timer = 0.0
		self.next_saucer_interval = random.uniform(SAUCER_SPAWN_INTERVAL_MIN, SAUCER_SPAWN_INTERVAL_MAX)
		if reset_score:
			self.next_extra_life_score = EXTRA_LIFE_SCORE
		
		# Create bunkers (4 bunkers evenly spaced above player)
		self.bunkers.clear()
		bunker_y = SCREEN_HEIGHT - 150  # Position above player
		total_bunker_width = BUNKER_COUNT * BUNKER_WIDTH
		spacing = (SCREEN_WIDTH - total_bunker_width) // (BUNKER_COUNT + 1)
		for i in range(BUNKER_COUNT):
			bunker_x = spacing + i * (BUNKER_WIDTH + spacing)
			bunker = Bunker(bunker_x, bunker_y)
			self.bunkers.append(bunker)
		
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
	
	def check_extra_life(self) -> None:
		"""Check if player earned an extra life."""
		if self.score >= self.next_extra_life_score and self.player:
			self.player.lives += 1
			self.next_extra_life_score += EXTRA_LIFE_SCORE  # Next life at next threshold
	
	def try_spawn_saucer(self, dt: float) -> None:
		"""Attempt to spawn a saucer."""
		# Don't spawn if one already exists
		if self.saucer is not None:
			return
		
		self.saucer_spawn_timer += dt
		if self.saucer_spawn_timer >= self.next_saucer_interval:
			self.saucer_spawn_timer = 0.0
			self.next_saucer_interval = random.uniform(SAUCER_SPAWN_INTERVAL_MIN, SAUCER_SPAWN_INTERVAL_MAX)
			# Spawn saucer
			self.saucer = Saucer()
	
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
			self.audio.play_sound("invader_shot")
	
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
							self.audio.play_sound("player_shot")
				elif self.state.current == GameState.TITLE:
					if event.key == pygame.K_h:
						self.state.set_state(GameState.HIGH_SCORES)
					elif event.key == pygame.K_s:
						self.state.set_state(GameState.SETTINGS)
				elif self.state.current == GameState.HIGH_SCORES:
					if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
						self.state.set_state(GameState.TITLE)
				elif self.state.current == GameState.SETTINGS:
					if event.key == pygame.K_ESCAPE:
						self.state.set_state(GameState.TITLE)
					elif event.key == pygame.K_m:
						self.audio.mute()
				elif self.state.current == GameState.PAUSED:
					if event.key == pygame.K_p:
						self.state.set_state(GameState.PLAYING)
					elif event.key == pygame.K_ESCAPE:
						self.state.set_state(GameState.TITLE)
				elif self.state.current == GameState.GAME_OVER:
					if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
						# Submit score before returning to title
						if self.score > 0:
							self.high_scores = submit_score(self.score)
						self.state.set_state(GameState.TITLE)

	def update(self, dt: float) -> None:
		if self.state.current == GameState.PLAYING:
			if self.player:
				keys = pygame.key.get_pressed()
				self.player.update(dt, keys)
			
			self.bullets.update(dt)
			self.bombs.update(dt)
			
			# Update saucer
			if self.saucer:
				self.saucer.update(dt)
				if not self.saucer.alive():  # Despawned off screen
					self.saucer = None
			
		# Try to spawn saucer
		had_saucer = self.saucer is not None
		self.try_spawn_saucer(dt)
		# Play flyby sound when saucer first spawns
		if self.saucer and not had_saucer:
			self.audio.play_sound("saucer_flyby")
		
		if self.formation:
				self.formation.update(dt)
				
				# Try to spawn bombs
				self.try_spawn_bomb(dt)
				
				# Check for bullet-invader collisions
				for bullet in list(self.bullets):  # Use list copy to avoid modification during iteration
					bullet_hit = False
					
					# Check invader collisions first
					for invader in self.formation.get_all_invaders():
						if bullet.rect.colliderect(invader.rect):
							# Hit! Remove invader and bullet, award points
							self.score += invader.points
							self.formation.remove_invader(invader)
							bullet.kill()
							bullet_hit = True
							self.audio.play_sound("invader_hit")
							self.check_extra_life()  # Check for extra life after scoring
							break  # Each bullet only hits one invader
					
					# Check saucer collision if bullet still active
					if not bullet_hit and self.saucer:
						if bullet.rect.colliderect(self.saucer.rect):
							# Hit saucer! Award points and despawn
							self.score += self.saucer.get_points()
							self.saucer.kill()
							self.saucer = None
							bullet.kill()
							self.audio.play_sound("saucer_hit")
							self.check_extra_life()  # Check for extra life after scoring
							bullet_hit = True
					
					# Check bunker collisions if bullet still active
					if not bullet_hit:
						for bunker in self.bunkers:
							if bunker.is_colliding(bullet.rect):
								# Hit bunker - damage it and despawn bullet
								collision_point = bunker.get_collision_point(bullet.rect)
								if collision_point:
									bunker.damage_at(collision_point)
									self.audio.play_sound("bunker_chip")
								bullet.kill()
								break
				
				# Check for bomb collisions (bunkers and player)
				for bomb in list(self.bombs):  # Use list copy to avoid modification during iteration
					bomb_hit = False
					
					# Check bunker collisions first
					for bunker in self.bunkers:
							if bunker.is_colliding(bomb.rect):
								# Hit bunker - damage it and despawn bomb
								collision_point = bunker.get_collision_point(bomb.rect)
								if collision_point:
									bunker.damage_at(collision_point)
									self.audio.play_sound("bunker_chip")
								bomb.kill()
								bomb_hit = True
								break
					
					# Check player collision if bomb still active
					if not bomb_hit and self.player and not self.player.invulnerable:
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
								self.audio.play_sound("player_death")
							else:
								# Game over
								self.audio.play_sound("player_death")
								self.state.set_state(GameState.GAME_OVER)
							break
				
				# Check if all invaders destroyed
				if self.formation.get_invader_count() == 0:
					# Wave cleared - advance to next wave
					self.wave += 1
					formation_start_x = SCREEN_WIDTH // 2 - (11 * 50) // 2 + 25
					self.formation = InvaderFormation(formation_start_x, 50)
					self.bombs.empty()  # Clear any remaining bombs
					# Reset bunkers for new wave
					bunker_y = SCREEN_HEIGHT - 150
					total_bunker_width = BUNKER_COUNT * BUNKER_WIDTH
					spacing = (SCREEN_WIDTH - total_bunker_width) // (BUNKER_COUNT + 1)
					self.bunkers.clear()
					for i in range(BUNKER_COUNT):
						bunker_x = spacing + i * (BUNKER_WIDTH + spacing)
						bunker = Bunker(bunker_x, bunker_y)
						self.bunkers.append(bunker)
				
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
		start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
		self.screen.blit(start_text, start_rect)
		
		menu_text = self.font_small.render("H: High Scores | S: Settings", True, WHITE)
		menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
		self.screen.blit(menu_text, menu_rect)
		
		controls_text = self.font_small.render("Arrow Keys: Move | SPACE: Fire | P: Pause | ESC: Quit", True, WHITE)
		controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
		self.screen.blit(controls_text, controls_rect)

	def render_playing(self) -> None:
		self.screen.fill(BLACK)
		
		# Render invaders
		if self.formation:
			for invader in self.formation.get_all_invaders():
				self.screen.blit(invader.image, invader.rect)
		
		# Render bunkers
		for bunker in self.bunkers:
			self.screen.blit(bunker.image, bunker.rect)
		
		# Render saucer
		if self.saucer:
			self.screen.blit(self.saucer.image, self.saucer.rect)
		
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

	def render_high_scores(self) -> None:
		self.screen.fill(BLACK)
		title_text = self.font_large.render("HIGH SCORES", True, WHITE)
		title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
		self.screen.blit(title_text, title_rect)
		
		if not self.high_scores:
			no_scores = self.font_medium.render("No scores yet!", True, WHITE)
			no_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
			self.screen.blit(no_scores, no_rect)
		else:
			start_y = 150
			for i, score in enumerate(self.high_scores[:10], 1):
				score_text = self.font_medium.render(f"{i}. {score:,}", True, WHITE)
				score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 35))
				self.screen.blit(score_text, score_rect)
		
		back_text = self.font_small.render("Press ESC or SPACE to return", True, WHITE)
		back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
		self.screen.blit(back_text, back_rect)
	
	def render_settings(self) -> None:
		self.screen.fill(BLACK)
		title_text = self.font_large.render("SETTINGS", True, WHITE)
		title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
		self.screen.blit(title_text, title_rect)
		
		mute_status = "ON" if self.audio.is_muted() else "OFF"
		mute_text = self.font_medium.render(f"Sound: {mute_status} (Press M to toggle)", True, WHITE)
		mute_rect = mute_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
		self.screen.blit(mute_text, mute_rect)
		
		volume_text = self.font_medium.render(f"Volume: {int(self.audio.volume * 100)}%", True, WHITE)
		volume_rect = volume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
		self.screen.blit(volume_text, volume_rect)
		
		back_text = self.font_small.render("Press ESC to return", True, WHITE)
		back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
		self.screen.blit(back_text, back_rect)
	
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
		elif self.state.current == GameState.HIGH_SCORES:
			self.render_high_scores()
		elif self.state.current == GameState.SETTINGS:
			self.render_settings()
		else:
			self.screen.fill(BLACK)
		
		pygame.display.flip()

	def run(self) -> None:
		while self.running:
			dt = self.clock.tick(FPS) / 1000.0
			self.handle_events()
			self.update(dt)
			self.render()

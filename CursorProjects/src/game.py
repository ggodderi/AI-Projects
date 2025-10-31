import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE
from src.game_state import GameState, GameStateManager
from src.player import Player
from src.bullet import Bullet


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
		
		# Set up state transitions
		self.state.set_on_enter(GameState.PLAYING, self.init_game)

	def init_game(self) -> None:
		"""Initialize/reset game objects when entering PLAYING state"""
		self.player = Player()
		self.bullets.empty()
	
	def handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				if self.state.current == GameState.TITLE:
					if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
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

	def update(self, dt: float) -> None:
		if self.state.current == GameState.PLAYING:
			if self.player:
				keys = pygame.key.get_pressed()
				self.player.update(dt, keys)
			
			self.bullets.update(dt)

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
		
		# Render game objects
		if self.player:
			self.screen.blit(self.player.image, self.player.rect)
		
		self.bullets.draw(self.screen)

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

	def render(self) -> None:
		if self.state.current == GameState.TITLE:
			self.render_title()
		elif self.state.current == GameState.PLAYING:
			self.render_playing()
		elif self.state.current == GameState.PAUSED:
			self.render_playing()  # Show game underneath
			self.render_paused()  # Then overlay pause
		else:
			self.screen.fill(BLACK)
		
		pygame.display.flip()

	def run(self) -> None:
		while self.running:
			dt = self.clock.tick(FPS) / 1000.0
			self.handle_events()
			self.update(dt)
			self.render()

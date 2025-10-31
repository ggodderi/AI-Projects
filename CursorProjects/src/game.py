import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from src.game_state import GameState, GameStateManager


class Game:
	def __init__(self) -> None:
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()
		self.state = GameStateManager()
		self.running = True

		# Example: enter playing on any key from title (to be implemented later)

	def handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False

	def update(self, dt: float) -> None:
		# Placeholder for state-specific updates
		pass

	def render(self) -> None:
		self.screen.fill(BLACK)
		pygame.display.flip()

	def run(self) -> None:
		while self.running:
			dt = self.clock.tick(FPS) / 1000.0
			self.handle_events()
			self.update(dt)
			self.render()

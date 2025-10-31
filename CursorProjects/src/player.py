import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, MAX_PLAYER_BULLETS


class Player(pygame.sprite.Sprite):
	def __init__(self, x: float = None, y: float = None) -> None:
		super().__init__()
		# Default position: center bottom of screen
		if x is None:
			x = SCREEN_WIDTH // 2
		if y is None:
			y = SCREEN_HEIGHT - 40  # Bottom with margin
		
		# Create cannon sprite
		self.image = pygame.Surface((44, 24), pygame.SRCALPHA)
		self._draw_cannon()
		self.rect = self.image.get_rect(center=(int(x), int(y)))
	
	def _draw_cannon(self) -> None:
		"""Draw a cannon/base sprite."""
		# Cannon color (green/yellow)
		CANNON_COLOR = (0, 255, 0)
		HIGHLIGHT = (150, 255, 150)
		DARK = (0, 200, 0)
		
		# Base (bottom rectangle)
		pygame.draw.rect(self.image, CANNON_COLOR, (4, 16, 36, 8))
		# Barrel (top trapezoid shape)
		pygame.draw.polygon(self.image, CANNON_COLOR, [
			(8, 16), (36, 16), (38, 8), (6, 8)
		])
		# Barrel tip
		pygame.draw.rect(self.image, CANNON_COLOR, (18, 4, 8, 4))
		# Highlight on barrel
		pygame.draw.line(self.image, HIGHLIGHT, (8, 12), (36, 12), 2)
		# Barrel detail
		pygame.draw.rect(self.image, DARK, (20, 6, 4, 4))
		
		self.speed = 300.0  # pixels per second
		self.lives = 3
		self.invulnerable = False
		self.invulnerability_timer = 0.0
		
	def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
		# Handle movement
		dx = 0.0
		if keys[pygame.K_LEFT] or keys[pygame.K_a]:
			dx -= self.speed * dt
		if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
			dx += self.speed * dt
		
		# Move and clamp to screen bounds
		self.rect.x += int(dx)
		self.rect.left = max(0, self.rect.left)
		self.rect.right = min(SCREEN_WIDTH, self.rect.right)
		
		# Update invulnerability timer
		if self.invulnerable:
			self.invulnerability_timer -= dt
			if self.invulnerability_timer <= 0:
				self.invulnerable = False
	
	def can_fire(self, active_bullets: int) -> bool:
		return not self.invulnerable and active_bullets < MAX_PLAYER_BULLETS
	
	def get_spawn_position(self) -> tuple[int, int]:
		"""Return position where bullet should spawn (center top of player)"""
		return (self.rect.centerx, self.rect.top)


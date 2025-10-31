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
		
		self.image = pygame.Surface((40, 20))
		self.image.fill((0, 255, 0))  # Green rectangle placeholder
		self.rect = self.image.get_rect(center=(int(x), int(y)))
		
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


import pygame

from config import SCREEN_HEIGHT, BOMB_SPEED


class Bomb(pygame.sprite.Sprite):
	def __init__(self, x: int, y: int) -> None:
		super().__init__()
		self.image = pygame.Surface((6, 12))
		self.image.fill((255, 0, 0))  # Red bomb
		# Add a simple pattern
		pygame.draw.circle(self.image, (255, 200, 0), (3, 6), 2)
		self.rect = self.image.get_rect(center=(x, y))
		
		self.speed = BOMB_SPEED
		
	def update(self, dt: float) -> None:
		self.rect.y += int(self.speed * dt)
		# Despawn if off screen bottom
		if self.rect.top > SCREEN_HEIGHT:
			self.kill()


import pygame

from config import SCREEN_HEIGHT


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x: int, y: int) -> None:
		super().__init__()
		self.image = pygame.Surface((4, 10))
		self.image.fill((255, 255, 255))  # White bullet
		self.rect = self.image.get_rect(center=(x, y))
		
		self.speed = 400.0  # pixels per second upward
		
	def update(self, dt: float) -> None:
		self.rect.y -= int(self.speed * dt)
		# Despawn if off screen
		if self.rect.bottom < 0:
			self.kill()


import random

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, SAUCER_SPEED, SAUCER_POINTS_VALUES


class Saucer(pygame.sprite.Sprite):
	def __init__(self, direction: int = None) -> None:
		super().__init__()
		# Direction: -1 = left to right, 1 = right to left
		if direction is None:
			direction = random.choice([-1, 1])
		self.direction = direction
		
		# Create saucer sprite
		self.image = pygame.Surface((40, 20), pygame.SRCALPHA)
		# Draw saucer shape (simple UFO)
		pygame.draw.ellipse(self.image, (255, 150, 150), (0, 5, 40, 15))
		pygame.draw.ellipse(self.image, (200, 100, 100), (5, 8, 30, 10))
		pygame.draw.rect(self.image, (150, 80, 80), (15, 0, 10, 8))
		
		self.rect = self.image.get_rect()
		
		# Set starting position based on direction
		if self.direction == -1:  # Left to right
			self.rect.x = -40
			self.rect.y = 30
		else:  # Right to left
			self.rect.x = SCREEN_WIDTH
			self.rect.y = 30
		
		self.speed = SAUCER_SPEED
		self.points_value = random.choice(SAUCER_POINTS_VALUES)
	
	def update(self, dt: float) -> None:
		"""Move saucer horizontally."""
		self.rect.x += int(self.direction * self.speed * dt)
		
		# Despawn if off screen
		if self.direction == -1 and self.rect.left > SCREEN_WIDTH:
			self.kill()
		elif self.direction == 1 and self.rect.right < 0:
			self.kill()
	
	def get_points(self) -> int:
		"""Get the point value for this saucer."""
		return self.points_value


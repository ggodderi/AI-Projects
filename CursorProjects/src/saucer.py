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
		
		# Create saucer sprite (UFO/mystery ship)
		self.image = pygame.Surface((48, 20), pygame.SRCALPHA)
		# Draw saucer shape - classic Space Invaders style
		# Top arc
		pygame.draw.arc(self.image, (255, 255, 255), (0, 0, 48, 20), 0, 3.14159, 3)
		# Bottom body
		pygame.draw.rect(self.image, (255, 255, 255), (4, 10, 40, 8))
		# Windows/details
		pygame.draw.rect(self.image, (255, 0, 0), (10, 12, 6, 4))
		pygame.draw.rect(self.image, (255, 0, 0), (20, 12, 6, 4))
		pygame.draw.rect(self.image, (255, 0, 0), (30, 12, 6, 4))
		# Tip
		pygame.draw.polygon(self.image, (255, 255, 255), [(0, 10), (4, 6), (4, 14)])
		pygame.draw.polygon(self.image, (255, 255, 255), [(48, 10), (44, 6), (44, 14)])
		
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


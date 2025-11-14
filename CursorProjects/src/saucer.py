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
		
		# Create saucer sprite (UFO/mystery ship) - make it more visible
		self.image = pygame.Surface((60, 24), pygame.SRCALPHA)
		# Fill with white background first for visibility
		pygame.draw.rect(self.image, (255, 255, 255), (0, 0, 60, 24))
		# Top arc (filled ellipse)
		pygame.draw.ellipse(self.image, (200, 200, 255), (2, 2, 56, 14))
		# Bottom body
		pygame.draw.rect(self.image, (200, 200, 255), (6, 14, 48, 8))
		# Windows/details (red)
		pygame.draw.rect(self.image, (255, 0, 0), (12, 16, 8, 4))
		pygame.draw.rect(self.image, (255, 0, 0), (26, 16, 8, 4))
		pygame.draw.rect(self.image, (255, 0, 0), (40, 16, 8, 4))
		# Tip (triangles)
		pygame.draw.polygon(self.image, (150, 150, 255), [(0, 12), (6, 8), (6, 16)])
		pygame.draw.polygon(self.image, (150, 150, 255), [(60, 12), (54, 8), (54, 16)])
		
		self.rect = self.image.get_rect()
		
		# Set starting position based on direction
		if self.direction == -1:  # Left to right
			self.rect.x = -60
			self.rect.y = 30
		else:  # Right to left
			self.rect.x = SCREEN_WIDTH
			self.rect.y = 30
		
		self.speed = SAUCER_SPEED
		self.points_value = random.choice(SAUCER_POINTS_VALUES)
	
	def update(self, dt: float) -> None:
		"""Move saucer horizontally."""
		# Direction: -1 = left to right (positive movement), 1 = right to left (negative movement)
		# So we negate the direction to get the correct movement
		self.rect.x += int(-self.direction * self.speed * dt)
		
		# Despawn if off screen
		# For left-to-right (direction=-1): check if past right edge
		# For right-to-left (direction=1): check if past left edge
		if self.direction == -1 and self.rect.left > SCREEN_WIDTH:
			self.kill()
		elif self.direction == 1 and self.rect.right < 0:
			self.kill()
	
	def get_points(self) -> int:
		"""Get the point value for this saucer."""
		return self.points_value


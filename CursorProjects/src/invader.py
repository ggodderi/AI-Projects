import pygame

from config import (
	INVADER_POINTS_TOP,
	INVADER_POINTS_MIDDLE,
	INVADER_POINTS_BOTTOM,
)


class Invader(pygame.sprite.Sprite):
	def __init__(self, row: int, col: int, x: float, y: float) -> None:
		super().__init__()
		self.row = row
		self.col = col
		
		# Determine invader type based on row (top rows = higher value)
		# Row 0 = top (30 points), rows 1-2 = middle (20 points), rows 3-4 = bottom (10 points)
		if row == 0:
			self.points = INVADER_POINTS_TOP
			self.color = (255, 100, 100)  # Light red
		elif row <= 2:
			self.points = INVADER_POINTS_MIDDLE
			self.color = (255, 200, 100)  # Orange
		else:
			self.points = INVADER_POINTS_BOTTOM
			self.color = (100, 255, 100)  # Light green
		
		# Create sprite with two-frame animation
		self.image_frame_0 = pygame.Surface((30, 24))
		self.image_frame_0.fill(self.color)
		# Add a simple pattern to distinguish frames
		pygame.draw.rect(self.image_frame_0, (255, 255, 255), (5, 5, 20, 14), 2)
		
		self.image_frame_1 = pygame.Surface((30, 24))
		self.image_frame_1.fill(self.color)
		pygame.draw.rect(self.image_frame_1, (255, 255, 255), (8, 8, 14, 8), 2)
		
		self.image = self.image_frame_0
		self.rect = self.image.get_rect(center=(int(x), int(y)))
		
		self.animation_frame = 0
		self.animation_timer = 0.0
	
	def update_animation(self, dt: float, animation_speed: float = 1.0) -> None:
		"""Update animation frames. animation_speed scales with formation speed."""
		self.animation_timer += dt * animation_speed
		if self.animation_timer >= 0.5:  # Switch every 0.5 seconds (scaled)
			self.animation_timer = 0.0
			self.animation_frame = 1 - self.animation_frame
			if self.animation_frame == 0:
				self.image = self.image_frame_0
			else:
				self.image = self.image_frame_1


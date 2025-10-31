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
		# Row 0 = top (30 points) - Squid-like, rows 1-2 = middle (20 points) - Crab-like, rows 3-4 = bottom (10 points) - Octopus-like
		if row == 0:
			self.points = INVADER_POINTS_TOP
			self.invader_type = "squid"
		elif row <= 2:
			self.points = INVADER_POINTS_MIDDLE
			self.invader_type = "crab"
		else:
			self.points = INVADER_POINTS_BOTTOM
			self.invader_type = "octopus"
		
		# Create sprite with two-frame animation
		self.image_frame_0 = pygame.Surface((32, 24), pygame.SRCALPHA)
		self.image_frame_1 = pygame.Surface((32, 24), pygame.SRCALPHA)
		self._draw_invader_frames()
		
		self.image = self.image_frame_0
		self.rect = self.image.get_rect(center=(int(x), int(y)))
		
		self.animation_frame = 0
		self.animation_timer = 0.0
	
	def _draw_invader_frames(self) -> None:
		"""Draw Space Invaders-style sprites with two animation frames."""
		# Colors
		WHITE = (255, 255, 255)
		YELLOW = (255, 255, 0)
		RED = (255, 0, 0)
		GREEN = (0, 255, 0)
		
		if self.invader_type == "squid":  # Top row - Squid-like
			color = GREEN
			# Frame 0 - arms up
			self._draw_squid_frame_0(self.image_frame_0, color)
			# Frame 1 - arms down
			self._draw_squid_frame_1(self.image_frame_1, color)
		elif self.invader_type == "crab":  # Middle rows - Crab-like
			color = YELLOW
			# Frame 0 - legs spread
			self._draw_crab_frame_0(self.image_frame_0, color)
			# Frame 1 - legs together
			self._draw_crab_frame_1(self.image_frame_1, color)
		else:  # Bottom rows - Octopus-like
			color = RED
			# Frame 0 - tentacles spread
			self._draw_octopus_frame_0(self.image_frame_0, color)
			# Frame 1 - tentacles together
			self._draw_octopus_frame_1(self.image_frame_1, color)
	
	def _draw_squid_frame_0(self, surf: pygame.Surface, color: tuple) -> None:
		"""Draw squid frame 0 (arms up)."""
		# Body (center ellipse)
		pygame.draw.ellipse(surf, color, (10, 8, 12, 10))
		# Eyes
		pygame.draw.rect(surf, (255, 255, 255), (12, 10, 2, 2))
		pygame.draw.rect(surf, (255, 255, 255), (18, 10, 2, 2))
		# Arms up
		pygame.draw.rect(surf, color, (4, 0, 4, 8))
		pygame.draw.rect(surf, color, (24, 0, 4, 8))
	
	def _draw_squid_frame_1(self, surf: pygame.Surface, color: tuple) -> None:
		"""Draw squid frame 1 (arms down)."""
		# Body
		pygame.draw.ellipse(surf, color, (10, 8, 12, 10))
		# Eyes
		pygame.draw.rect(surf, (255, 255, 255), (12, 10, 2, 2))
		pygame.draw.rect(surf, (255, 255, 255), (18, 10, 2, 2))
		# Arms down
		pygame.draw.rect(surf, color, (4, 16, 4, 8))
		pygame.draw.rect(surf, color, (24, 16, 4, 8))
	
	def _draw_crab_frame_0(self, surf: pygame.Surface, color: tuple) -> None:
		"""Draw crab frame 0 (legs spread)."""
		# Body
		pygame.draw.ellipse(surf, color, (8, 6, 16, 12))
		# Eyes
		pygame.draw.rect(surf, (255, 255, 255), (11, 8, 2, 2))
		pygame.draw.rect(surf, (255, 255, 255), (19, 8, 2, 2))
		# Top pincers spread
		pygame.draw.rect(surf, color, (2, 2, 6, 4))
		pygame.draw.rect(surf, color, (24, 2, 6, 4))
		# Bottom legs spread
		pygame.draw.rect(surf, color, (2, 18, 4, 6))
		pygame.draw.rect(surf, color, (26, 18, 4, 6))
	
	def _draw_crab_frame_1(self, surf: pygame.Surface, color: tuple) -> None:
		"""Draw crab frame 1 (legs together)."""
		# Body
		pygame.draw.ellipse(surf, color, (8, 6, 16, 12))
		# Eyes
		pygame.draw.rect(surf, (255, 255, 255), (11, 8, 2, 2))
		pygame.draw.rect(surf, (255, 255, 255), (19, 8, 2, 2))
		# Top pincers together
		pygame.draw.rect(surf, color, (4, 2, 6, 4))
		pygame.draw.rect(surf, color, (22, 2, 6, 4))
		# Bottom legs together
		pygame.draw.rect(surf, color, (6, 18, 4, 6))
		pygame.draw.rect(surf, color, (22, 18, 4, 6))
	
	def _draw_octopus_frame_0(self, surf: pygame.Surface, color: tuple) -> None:
		"""Draw octopus frame 0 (tentacles spread)."""
		# Head
		pygame.draw.ellipse(surf, color, (10, 4, 12, 8))
		# Eyes
		pygame.draw.rect(surf, (255, 255, 255), (12, 6, 2, 2))
		pygame.draw.rect(surf, (255, 255, 255), (18, 6, 2, 2))
		# Tentacles spread
		pygame.draw.rect(surf, color, (2, 14, 3, 10))
		pygame.draw.rect(surf, color, (8, 14, 3, 10))
		pygame.draw.rect(surf, color, (21, 14, 3, 10))
		pygame.draw.rect(surf, color, (27, 14, 3, 10))
	
	def _draw_octopus_frame_1(self, surf: pygame.Surface, color: tuple) -> None:
		"""Draw octopus frame 1 (tentacles together)."""
		# Head
		pygame.draw.ellipse(surf, color, (10, 4, 12, 8))
		# Eyes
		pygame.draw.rect(surf, (255, 255, 255), (12, 6, 2, 2))
		pygame.draw.rect(surf, (255, 255, 255), (18, 6, 2, 2))
		# Tentacles together
		pygame.draw.rect(surf, color, (5, 14, 3, 10))
		pygame.draw.rect(surf, color, (10, 14, 3, 10))
		pygame.draw.rect(surf, color, (19, 14, 3, 10))
		pygame.draw.rect(surf, color, (24, 14, 3, 10))
	
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


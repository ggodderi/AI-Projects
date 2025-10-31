import pygame

from config import BUNKER_WIDTH, BUNKER_HEIGHT, BUNKER_DAMAGE_RADIUS


class Bunker(pygame.sprite.Sprite):
	def __init__(self, x: int, y: int) -> None:
		super().__init__()
		self.base_image = pygame.Surface((BUNKER_WIDTH, BUNKER_HEIGHT), pygame.SRCALPHA)
		self.rect = self.base_image.get_rect(topleft=(x, y))
		
		# Create initial bunker shape (simple arc/arch design)
		self._draw_bunker_shape()
		
		# Damage mask - tracks which pixels are destroyed
		# True = intact, False = destroyed
		self.damage_mask = pygame.Surface((BUNKER_WIDTH, BUNKER_HEIGHT), pygame.SRCALPHA)
		self.damage_mask.fill((255, 255, 255, 255))  # All intact initially
		
		# Update display image
		self.image = self.base_image.copy()
	
	def _draw_bunker_shape(self) -> None:
		"""Draw the bunker's basic shape."""
		# Draw a simple arch/bunker shape
		# Bottom solid block
		pygame.draw.rect(self.base_image, (0, 255, 0), (0, BUNKER_HEIGHT - 20, BUNKER_WIDTH, 20))
		
		# Middle section with arch cutout
		pygame.draw.rect(self.base_image, (0, 255, 0), (0, BUNKER_HEIGHT - 40, BUNKER_WIDTH, 20))
		# Arch cutout (top center)
		arch_center_x = BUNKER_WIDTH // 2
		arch_radius = 15
		pygame.draw.circle(self.base_image, (0, 0, 0, 0), (arch_center_x, BUNKER_HEIGHT - 40), arch_radius)
		
		# Top small block
		pygame.draw.rect(self.base_image, (0, 255, 0), (0, 0, BUNKER_WIDTH, BUNKER_HEIGHT - 50))
	
	def is_colliding(self, rect: pygame.Rect) -> bool:
		"""Check if a rect collides with intact parts of the bunker."""
		# First check if rect overlaps bunker bounds
		if not self.rect.colliderect(rect):
			return False
		
		# Convert rect center to bunker-relative coordinates
		rel_x = rect.centerx - self.rect.x
		rel_y = rect.centery - self.rect.y
		
		# Clamp to bunker bounds
		if rel_x < 0 or rel_x >= BUNKER_WIDTH or rel_y < 0 or rel_y >= BUNKER_HEIGHT:
			return False
		
		# Check if this point is part of the bunker and intact
		# Check base image (is it part of bunker?)
		if self.base_image.get_at((int(rel_x), int(rel_y)))[3] == 0:
			return False  # Not part of bunker
		
		# Check damage mask (is it still intact?)
		mask_alpha = self.damage_mask.get_at((int(rel_x), int(rel_y)))[3]
		return mask_alpha > 128  # Intact if alpha > 128
	
	def damage_at(self, point: tuple[int, int]) -> None:
		"""Apply damage to the bunker at a specific point (in screen coordinates)."""
		# Convert to bunker-relative coordinates
		rel_x = point[0] - self.rect.x
		rel_y = point[1] - self.rect.y
		
		# Clamp to bunker bounds
		if rel_x < 0 or rel_x >= BUNKER_WIDTH or rel_y < 0 or rel_y >= BUNKER_HEIGHT:
			return
		
		# Draw a circle of damage
		pygame.draw.circle(
			self.damage_mask,
			(0, 0, 0, 0),  # Transparent = destroyed
			(rel_x, rel_y),
			BUNKER_DAMAGE_RADIUS
		)
		
		# Update display image
		self._update_image()
	
	def _update_image(self) -> None:
		"""Update the display image based on damage mask."""
		self.image = self.base_image.copy()
		# Apply damage mask - where mask is transparent, make bunker transparent
		for y in range(BUNKER_HEIGHT):
			for x in range(BUNKER_WIDTH):
				mask_alpha = self.damage_mask.get_at((x, y))[3]
				if mask_alpha < 128:  # Damaged
					# Make this pixel transparent
					base_color = self.base_image.get_at((x, y))
					self.image.set_at((x, y), (*base_color[:3], 0))
	
	def get_collision_point(self, rect: pygame.Rect) -> tuple[int, int] | None:
		"""Get the collision point between rect and bunker (in screen coordinates), or None if no collision."""
		if not self.is_colliding(rect):
			return None
		
		# Return center of rect as collision point
		return (rect.centerx, rect.centery)


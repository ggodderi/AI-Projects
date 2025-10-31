import pygame
import random

from config import (
	SCREEN_WIDTH,
	INVADER_ROWS,
	INVADER_COLS,
	INVADER_HORIZONTAL_SPEED,
	INVADER_BASE_STEP_INTERVAL,
	INVADER_STEP_DOWN_AMOUNT,
)

from src.invader import Invader


class InvaderFormation:
	def __init__(self, start_x: float, start_y: float) -> None:
		self.start_x = start_x
		self.start_y = start_y
		
		# Grid: dict mapping (row, col) to Invader
		self.invaders: dict[tuple[int, int], Invader] = {}
		
		# Formation movement
		self.direction = 1  # 1 = right, -1 = left
		self.step_timer = 0.0
		self.current_step_interval = INVADER_BASE_STEP_INTERVAL
		
		# Create invaders in grid
		invader_spacing_x = 50
		invader_spacing_y = 40
		
		for row in range(INVADER_ROWS):
			for col in range(INVADER_COLS):
				x = start_x + col * invader_spacing_x
				y = start_y + row * invader_spacing_y
				invader = Invader(row, col, x, y)
				self.invaders[(row, col)] = invader
	
	def get_all_invaders(self) -> list[Invader]:
		"""Get all active invaders as a list."""
		return list(self.invaders.values())
	
	def get_invader_count(self) -> int:
		"""Get number of remaining invaders."""
		return len(self.invaders)
	
	def get_speed_multiplier(self) -> float:
		"""Calculate speed multiplier based on remaining invaders (fewer = faster)."""
		total = INVADER_ROWS * INVADER_COLS
		remaining = self.get_invader_count()
		if remaining == 0:
			return 3.0
		# Speed increases as invaders are destroyed
		# Formula: base speed * (1 + (destroyed/total) * 2)
		destroyed = total - remaining
		ratio = destroyed / total
		return 1.0 + ratio * 2.0
	
	def get_front_line_invaders(self) -> list[Invader]:
		"""Get invaders that can fire (lowest invader in each non-empty column)."""
		front_line: dict[int, Invader] = {}  # col -> invader
		
		for (row, col), invader in self.invaders.items():
			# If no invader in this column yet, or this one is lower (higher row number)
			if col not in front_line or row > front_line[col].row:
				front_line[col] = invader
		
		return list(front_line.values())
	
	def remove_invader(self, invader: Invader) -> None:
		"""Remove an invader from the formation."""
		key = (invader.row, invader.col)
		if key in self.invaders:
			del self.invaders[key]
			# Recalculate speed after removal
			self._update_step_interval()
	
	def _update_step_interval(self) -> None:
		"""Update step interval based on remaining invaders."""
		multiplier = self.get_speed_multiplier()
		self.current_step_interval = INVADER_BASE_STEP_INTERVAL / multiplier
	
	def check_boundaries(self) -> tuple[int, int, int]:
		"""Check if any invader hits screen boundaries. Returns (leftmost_x, rightmost_x, bottom_y)."""
		if not self.invaders:
			return (0, SCREEN_WIDTH, 0)
		
		leftmost = min(inv.rect.left for inv in self.invaders.values())
		rightmost = max(inv.rect.right for inv in self.invaders.values())
		bottom = max(inv.rect.bottom for inv in self.invaders.values())
		
		return (leftmost, rightmost, bottom)
	
	def reverse_and_step_down(self) -> None:
		"""Reverse direction and step all invaders down."""
		self.direction *= -1
		for invader in self.invaders.values():
			invader.rect.y += INVADER_STEP_DOWN_AMOUNT
	
	def check_descend_limit(self, player_y_threshold: int) -> bool:
		"""Check if any invader has reached the player row threshold."""
		_, _, bottom = self.check_boundaries()
		return bottom >= player_y_threshold
	
	def update(self, dt: float) -> None:
		"""Update formation movement and animations."""
		if not self.invaders:
			return
		
		# Update step timer
		self.step_timer += dt
		
		# Check if it's time to step
		if self.step_timer >= self.current_step_interval:
			self.step_timer = 0.0
			
			# Move all invaders horizontally
			for invader in self.invaders.values():
				invader.rect.x += int(self.direction * INVADER_HORIZONTAL_SPEED * self.current_step_interval)
			
			# Check boundaries
			leftmost, rightmost, _ = self.check_boundaries()
			
			# If hit left or right wall, reverse and step down
			if leftmost <= 0 or rightmost >= SCREEN_WIDTH:
				self.reverse_and_step_down()
		
		# Update animations for all invaders
		animation_speed = self.get_speed_multiplier()
		for invader in self.invaders.values():
			invader.update_animation(dt, animation_speed)


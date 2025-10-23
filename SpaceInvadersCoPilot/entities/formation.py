from __future__ import annotations

import random
from typing import List, Optional

import pygame

from settings import (
    ALIEN_COLS,
    ALIEN_ROWS,
    ALIEN_X_SPACING,
    ALIEN_Y_SPACING,
    ALIEN_START_X,
    ALIEN_START_Y,
    ALIEN_STEP_X,
    ALIEN_STEP_Y,
    ALIEN_BASE_STEP_TIME,
    ALIEN_MIN_STEP_TIME,
    ALIEN_BULLET_SPEED,
    ALIEN_BULLET_WIDTH,
    ALIEN_BULLET_HEIGHT,
    WINDOW_WIDTH,
    WHITE,
)
from entities.alien import Alien
from entities.projectile import Projectile


class Formation:
    def __init__(self) -> None:
        self.aliens: List[List[Optional[Alien]]] = []
        y = ALIEN_START_Y
        # Score values and colors by row (top higher)
        values = [30, 20, 20, 10, 10]
        colors = [(255,255,0), (0,255,255), (255,0,255), (0,255,0), (255,255,255)]
        for r in range(ALIEN_ROWS):
            row: List[Optional[Alien]] = []
            x = ALIEN_START_X
            for c in range(ALIEN_COLS):
                row.append(Alien(x, y, 32, 24, values[r % len(values)], colors[r % len(colors)]))
                x += ALIEN_X_SPACING
            self.aliens.append(row)
            y += ALIEN_Y_SPACING

        self.direction = 1  # 1 right, -1 left
        self.step_timer = ALIEN_BASE_STEP_TIME
        self.current_step_time = ALIEN_BASE_STEP_TIME
        self.bounds = self.compute_bounds()

    def compute_bounds(self) -> pygame.Rect:
        rects = [a.rect for row in self.aliens for a in row if a]
        if not rects:
            return pygame.Rect(0, 0, 0, 0)
        min_x = min(r.left for r in rects)
        max_x = max(r.right for r in rects)
        min_y = min(r.top for r in rects)
        max_y = max(r.bottom for r in rects)
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def alive_aliens(self) -> List[Alien]:
        return [a for row in self.aliens for a in row if a and a.alive]

    def count(self) -> int:
        return len(self.alive_aliens())

    def update(self, dt: float) -> None:
        alive = self.alive_aliens()
        count = len(alive)
        if count == 0:
            return
        # Speed up as aliens decrease
        t = max(ALIEN_MIN_STEP_TIME, ALIEN_BASE_STEP_TIME * (count / float(ALIEN_COLS * ALIEN_ROWS)))
        self.current_step_time = t
        self.step_timer -= dt
        if self.step_timer <= 0:
            self.step_timer = self.current_step_time
            # Check edge and move
            self.bounds = self.compute_bounds()
            hit_edge = (self.direction > 0 and self.bounds.right + ALIEN_STEP_X >= WINDOW_WIDTH - 10) or (
                self.direction < 0 and self.bounds.left - ALIEN_STEP_X <= 10
            )
            if hit_edge:
                # drop and reverse
                for a in alive:
                    a.rect.y += ALIEN_STEP_Y
                self.direction *= -1
            else:
                for a in alive:
                    a.rect.x += ALIEN_STEP_X * self.direction
            self.bounds = self.compute_bounds()

    def lowest_in_column(self, col: int) -> Optional[Alien]:
        for r in range(ALIEN_ROWS - 1, -1, -1):
            a = self.aliens[r][col]
            if a and a.alive:
                return a
        return None

    def try_fire(self) -> Optional[Projectile]:
        # Random chance to fire each call; caller can control rate
        cols = list(range(ALIEN_COLS))
        random.shuffle(cols)
        for col in cols:
            a = self.lowest_in_column(col)
            if a is not None:
                bx = a.rect.centerx - ALIEN_BULLET_WIDTH // 2
                by = a.rect.bottom
                return Projectile(bx, by, ALIEN_BULLET_WIDTH, ALIEN_BULLET_HEIGHT, ALIEN_BULLET_SPEED, WHITE)
        return None

    def draw(self, surface: pygame.Surface) -> None:
        for a in self.alive_aliens():
            a.draw(surface)

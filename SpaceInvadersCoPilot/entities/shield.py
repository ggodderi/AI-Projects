from __future__ import annotations

from typing import List

import pygame

from settings import SHIELD_BLOCK_SIZE, SHIELD_WIDTH, SHIELD_HEIGHT, WHITE


class Shield:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.cols = SHIELD_WIDTH // SHIELD_BLOCK_SIZE
        self.rows = SHIELD_HEIGHT // SHIELD_BLOCK_SIZE
        # True means intact block
        self.grid: List[List[bool]] = [[True for _ in range(self.cols)] for _ in range(self.rows)]

        # carve a notch shape at bottom
        for r in range(self.rows - 4, self.rows):
            for c in range(self.cols):
                if abs(c - self.cols // 2) < (self.rows - r):
                    self.grid[r][c] = False

    def rects(self) -> List[pygame.Rect]:
        rs: List[pygame.Rect] = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]:
                    rx = self.x + c * SHIELD_BLOCK_SIZE
                    ry = self.y + r * SHIELD_BLOCK_SIZE
                    rs.append(pygame.Rect(rx, ry, SHIELD_BLOCK_SIZE, SHIELD_BLOCK_SIZE))
        return rs

    def hit(self, point_rect: pygame.Rect) -> bool:
        # Find the grid cell overlapped by projectile rect center
        cx = point_rect.centerx - self.x
        cy = point_rect.centery - self.y
        if cx < 0 or cy < 0:
            return False
        c = cx // SHIELD_BLOCK_SIZE
        r = cy // SHIELD_BLOCK_SIZE
        if 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c]:
            # Erode a small 3x3 area around impact
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    rr = r + dr
                    cc = c + dc
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        self.grid[rr][cc] = False
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]:
                    rx = self.x + c * SHIELD_BLOCK_SIZE
                    ry = self.y + r * SHIELD_BLOCK_SIZE
                    pygame.draw.rect(surface, WHITE, (rx, ry, SHIELD_BLOCK_SIZE, SHIELD_BLOCK_SIZE))

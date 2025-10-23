from __future__ import annotations

import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PLAYER_SPEED,
    PLAYER_LIVES,
    PLAYER_COOLDOWN,
    PLAYER_WIDTH,
    PLAYER_HEIGHT,
    PLAYER_BULLET_WIDTH,
    PLAYER_BULLET_HEIGHT,
    PLAYER_BULLET_SPEED,
    GREEN,
)
from entities.projectile import Projectile


class Player:
    def __init__(self) -> None:
        self.rect = pygame.Rect(
            WINDOW_WIDTH // 2 - PLAYER_WIDTH // 2,
            WINDOW_HEIGHT - 60,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )
        self.lives = PLAYER_LIVES
        self.cooldown = 0.0
        self.active_bullet: Projectile | None = None

    def update(self, dt: float, keys) -> None:
        # Movement
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        self.rect.x += int(dx * PLAYER_SPEED * dt)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WINDOW_WIDTH, self.rect.right)

        # Cooldown
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)

        # Update bullet
        if self.active_bullet is not None:
            self.active_bullet.update(dt)
            if not self.active_bullet.alive:
                self.active_bullet = None

    def can_fire(self) -> bool:
        return self.cooldown <= 0.0 and self.active_bullet is None

    def fire(self) -> Projectile | None:
        if not self.can_fire():
            return None
        bx = self.rect.centerx - PLAYER_BULLET_WIDTH // 2
        by = self.rect.top - PLAYER_BULLET_HEIGHT
        self.active_bullet = Projectile(bx, by, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT, PLAYER_BULLET_SPEED, GREEN)
        self.cooldown = PLAYER_COOLDOWN
        return self.active_bullet

    def draw(self, surface: pygame.Surface) -> None:
        # Draw a more detailed cannon shape (pixel-art)
        x, y, w, h = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        # Base
        pygame.draw.rect(surface, (0,255,0), (x, y + h // 2, w, h // 2))
        # Barrel
        pygame.draw.rect(surface, (0,200,0), (x + w // 2 - w // 8, y, w // 4, h // 2))
        # Left foot
        pygame.draw.rect(surface, (0,180,0), (x, y + h - h // 6, w // 4, h // 6))
        # Right foot
        pygame.draw.rect(surface, (0,180,0), (x + w - w // 4, y + h - h // 6, w // 4, h // 6))
        # Add a small red tip to barrel
        pygame.draw.rect(surface, (255,0,0), (x + w // 2 - w // 16, y, w // 8, h // 6))
        # Add a yellow highlight to base
        pygame.draw.rect(surface, (255,255,0), (x + w // 4, y + h // 2 + h // 6, w // 2, h // 8))
        if self.active_bullet is not None:
            self.active_bullet.draw(surface)

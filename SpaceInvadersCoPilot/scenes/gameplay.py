from __future__ import annotations

import random
from typing import List

import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WHITE,
    GREEN,
    RED,
    HUD_FONT_SIZE,
    NUM_SHIELDS,
    SHIELD_TOP,
    SHIELD_WIDTH,
    PLAYER_BULLET_WIDTH,
    PLAYER_BULLET_HEIGHT,
    ALIEN_MAX_CONCURRENT_BULLETS,
)
from entities.player import Player
from entities.formation import Formation
from entities.projectile import Projectile
from entities.shield import Shield
from entities.ufo import UFO
from systems.collision import rect_collision
from scenes.pause import PauseScene
from scenes.game_over import GameOverScene


class GameplayScene:
    def __init__(self, game) -> None:
        self.game = game
        self.font = pygame.font.SysFont(None, HUD_FONT_SIZE)

        self.player = Player()
        self.formation = Formation()
    # Player bullets now tracked in Player.bullets
        self.alien_bullets: List[Projectile] = []

        # Shields
        self.shields: List[Shield] = []
        spacing = (WINDOW_WIDTH - NUM_SHIELDS * SHIELD_WIDTH) // (NUM_SHIELDS + 1)
        x = spacing
        for _ in range(NUM_SHIELDS):
            self.shields.append(Shield(x, SHIELD_TOP))
            x += SHIELD_WIDTH + spacing

        # UFO
        self.ufo = UFO()
        self.next_ufo_time = random.uniform(12.0, 22.0)
        self.ufo_timer = 0.0

        self.score = 0
        self.lives = self.player.lives
        self.alien_fire_timer = 0.0
        self.alien_fire_interval = 0.9

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                self.game.set_scene(PauseScene(self.game, self))
            elif event.key == pygame.K_SPACE:
                self.player.fire()

    def update(self, dt: float) -> None:
        # Update player
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)

        # Update formation
        self.formation.update(dt)

        # Alien firing
        self.alien_fire_timer -= dt
        if self.alien_fire_timer <= 0 and len(self.alien_bullets) < ALIEN_MAX_CONCURRENT_BULLETS:
            shot = self.formation.try_fire()
            if shot:
                self.alien_bullets.append(shot)
            self.alien_fire_timer = self.formation.current_step_time * 2.0

        # Update alien bullets
        for b in self.alien_bullets:
            b.update(dt)
        self.alien_bullets = [b for b in self.alien_bullets if b.alive]

        # Update UFO
        self.ufo_timer += dt
        if not self.ufo.active and self.ufo_timer >= self.next_ufo_time:
            self.ufo.spawn()
            self.ufo_timer = 0.0
            self.next_ufo_time = random.uniform(12.0, 22.0)
        self.ufo.update(dt)

        # Collisions
        self.handle_collisions()

        # Check wave clear
        if self.formation.count() == 0:
            # New wave
            self.formation = Formation()

        # Check bottom reach (game over)
        if self.formation.bounds.bottom >= self.player.rect.bottom:
            self.end_game()

    def handle_collisions(self) -> None:
        # Player bullets vs aliens/UFO/shields
        for pb in list(self.player.bullets):
            # Shields
            for shield in self.shields:
                if shield.hit(pb.rect):
                    pb.alive = False
                    break
            if not pb.alive:
                continue
            # UFO
            if self.ufo.active and rect_collision(pb.rect, self.ufo.rect):
                self.score += self.ufo.value
                self.ufo.active = False
                pb.alive = False
                continue
            # Aliens (coarse scan)
            for row in self.formation.aliens:
                hit = False
                for i, alien in enumerate(row):
                    if alien and alien.alive and rect_collision(pb.rect, alien.rect):
                        alien.alive = False
                        self.score += alien.value
                        pb.alive = False
                        hit = True
                        break
                if hit:
                    break

        # Alien bullets vs shields and player
        for b in list(self.alien_bullets):
            # Shields
            shield_hit = False
            for shield in self.shields:
                if shield.hit(b.rect):
                    b.alive = False
                    shield_hit = True
                    break
            if shield_hit:
                continue
            # Player
            if rect_collision(b.rect, self.player.rect):
                b.alive = False
                self.lives -= 1
                if self.lives <= 0:
                    self.end_game()
                    return
        self.alien_bullets = [b for b in self.alien_bullets if b.alive]

    def end_game(self) -> None:
        self.game.set_scene(GameOverScene(self.game, self.score))

    def draw(self, surface: pygame.Surface) -> None:
        # Draw shields
        for shield in self.shields:
            shield.draw(surface)

        # Draw aliens
        self.formation.draw(surface)

        # Draw UFO
        self.ufo.draw(surface)

        # Draw player and bullets
        self.player.draw(surface)

        # Draw alien bullets
        for b in self.alien_bullets:
            b.draw(surface)

        # HUD
        score_txt = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_txt = self.font.render(f"Lives: {self.lives}", True, WHITE)
        surface.blit(score_txt, (16, 8))
        surface.blit(lives_txt, (WINDOW_WIDTH - lives_txt.get_width() - 16, 8))

"""Scorched Earth — a polished, asset-free Pygame artillery duel."""

from __future__ import annotations

import math
import sys
import pygame

from game_core import Battle, GROUND_Y, HEIGHT, MAX_POWER, WIDTH


BG = (13, 18, 31)
PANEL = (21, 28, 46)
TEXT = (224, 232, 245)
MUTED = (132, 148, 175)
SAND = (213, 150, 76)
SAND_DARK = (126, 80, 48)
GRID = (35, 46, 69)


class ScorchedEarth:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("SCORCHED EARTH // ARTILLERY DUEL")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 22)
        self.small = pygame.font.Font(None, 17)
        self.big = pygame.font.Font(None, 50)
        self.battle = Battle()
        self.running = True

    def text(self, value: str, x: int, y: int, color=TEXT, font=None) -> None:
        self.screen.blit((font or self.font).render(value, True, color), (x, y))

    def draw_background(self) -> None:
        self.screen.fill(BG)
        for y in range(80, GROUND_Y, 44):
            pygame.draw.line(self.screen, GRID, (0, y), (WIDTH, y), 1)
        for x in range(0, WIDTH, 48):
            pygame.draw.line(self.screen, GRID, (x, 70), (x, GROUND_Y), 1)
        pygame.draw.rect(self.screen, (17, 23, 39), (0, 0, WIDTH, 66))
        pygame.draw.line(self.screen, (44, 57, 84), (0, 66), (WIDTH, 66), 2)

    def draw_terrain(self) -> None:
        points = [(0, GROUND_Y)] + [(x, int(self.battle.terrain.heights[x])) for x in range(WIDTH)] + [(WIDTH, GROUND_Y)]
        pygame.draw.polygon(self.screen, SAND_DARK, points)
        top = [(x, int(self.battle.terrain.heights[x])) for x in range(WIDTH)]
        pygame.draw.lines(self.screen, SAND, False, top, 3)

    def draw_tank(self, index: int) -> None:
        tank = self.battle.tanks[index]
        if not tank.alive():
            return
        x, y = tank.x, self.battle.tank_y(tank)
        direction = 1 if index == 0 else -1
        body = pygame.Rect(int(x - 17), int(y - 4), 34, 15)
        pygame.draw.rect(self.screen, tank.color, body, border_radius=5)
        pygame.draw.circle(self.screen, tank.color, (int(x), int(y - 5)), 9)
        angle = math.radians(tank.angle)
        end = (x + direction * math.cos(angle) * 28, y - 8 - math.sin(angle) * 28)
        pygame.draw.line(self.screen, tank.color, (x, y - 8), end, 6)
        pygame.draw.rect(self.screen, (30, 35, 50), (int(x - 23), int(y - 29), 46, 5), border_radius=2)
        pygame.draw.rect(self.screen, (82, 220, 143), (int(x - 23), int(y - 29), int(46 * tank.health / 100), 5), border_radius=2)

    def draw_projectile(self) -> None:
        p = self.battle.projectile
        if not p:
            return
        for index, (x, y) in enumerate(p.trail):
            alpha = (index + 1) / len(p.trail)
            color = (int(255 * alpha), int(180 * alpha), int(88 * alpha))
            pygame.draw.circle(self.screen, color, (int(x), int(y)), max(1, int(3 * alpha)))
        pygame.draw.circle(self.screen, (255, 225, 135), (int(p.x), int(p.y)), 5)

    def draw_explosion(self) -> None:
        e = self.battle.explosion
        if not e:
            return
        x, y, radius, age = e
        scale = min(1.0, age / 0.12) if age else 0.15
        radius *= 1.0 - max(0.0, age - 0.25) / 0.2
        pygame.draw.circle(self.screen, (255, 110, 50), (int(x), int(y)), max(2, int(radius * scale)), 4)
        pygame.draw.circle(self.screen, (255, 213, 92), (int(x), int(y)), max(2, int(radius * scale * 0.55)), 3)

    def draw_ui(self) -> None:
        self.text("SCORCHED EARTH", 24, 18, (255, 193, 92), self.font)
        self.text("ARTILLERY DUEL", 24, 39, MUTED, self.small)
        self.text(f"WIND  {self.battle.wind:+.1f}", WIDTH - 148, 20, MUTED, self.small)
        self.text(self.battle.message, WIDTH // 2 - 145, 22, TEXT, self.small)
        pygame.draw.rect(self.screen, PANEL, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(self.screen, (44, 57, 84), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
        you, cpu = self.battle.tanks
        self.text("YOU", 30, GROUND_Y + 17, you.color, self.small)
        self.text(f"{you.health:03d}", 30, GROUND_Y + 35, TEXT, self.font)
        self.text("CPU", WIDTH - 72, GROUND_Y + 17, cpu.color, self.small)
        self.text(f"{cpu.health:03d}", WIDTH - 72, GROUND_Y + 35, TEXT, self.font)
        self.text(f"ANGLE  {int(self.battle.active_tank.angle):02d}°", 250, GROUND_Y + 18, TEXT, self.small)
        self.text(f"POWER  {int(self.battle.active_tank.power):03d}", 250, GROUND_Y + 39, TEXT, self.small)
        pygame.draw.rect(self.screen, (38, 49, 71), (420, GROUND_Y + 22, 230, 8), border_radius=4)
        pygame.draw.rect(self.screen, (255, 193, 92), (420, GROUND_Y + 22, int(230 * self.battle.active_tank.power / MAX_POWER), 8), border_radius=4)
        self.text("←/→ AIM   ↑/↓ POWER   SPACE FIRE   R RESET", 740, GROUND_Y + 25, MUTED, self.small)

    def draw_overlay(self) -> None:
        if not self.battle.game_over:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 15, 160))
        self.screen.blit(overlay, (0, 0))
        title = self.battle.winner_text()
        rect = self.big.render(title, True, (255, 193, 92)).get_rect(center=(WIDTH // 2, HEIGHT // 2 - 25))
        self.screen.blit(self.big.render(title, True, (255, 193, 92)), rect)
        hint = self.font.render("PRESS R TO PLAY AGAIN", True, TEXT)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.battle.skip_or_reset()
                elif not self.battle.projectile and not self.battle.game_over and self.battle.turn == 0:
                    if event.key == pygame.K_LEFT:
                        self.battle.aim(angle_delta=2)
                    elif event.key == pygame.K_RIGHT:
                        self.battle.aim(angle_delta=-2)
                    elif event.key == pygame.K_UP:
                        self.battle.aim(power_delta=5)
                    elif event.key == pygame.K_DOWN:
                        self.battle.aim(power_delta=-5)
                    elif event.key == pygame.K_SPACE:
                        self.battle.fire()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.battle.update(dt)
            self.battle.update_effects(dt)
            self.draw_background()
            self.draw_terrain()
            self.draw_tank(0)
            self.draw_tank(1)
            self.draw_projectile()
            self.draw_explosion()
            self.draw_ui()
            self.draw_overlay()
            pygame.display.flip()
        pygame.quit()
        return None


def main() -> None:
    if "--smoke-test" in sys.argv:
        pygame.init()
        game = ScorchedEarth()
        game.draw_background()
        game.draw_terrain()
        game.draw_tank(0)
        game.draw_tank(1)
        pygame.display.flip()
        pygame.quit()
        print("Pygame smoke test passed")
        return
    ScorchedEarth().run()


if __name__ == "__main__":
    main()


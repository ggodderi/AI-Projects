"""Core simulation for the Scorched Earth style artillery game.

This module deliberately contains no Pygame imports.  It can be exercised by
unit tests or reused by another front end.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Iterable


WIDTH = 1200
HEIGHT = 700
GROUND_Y = 610
GRAVITY = 180.0
MAX_POWER = 175.0


@dataclass
class Tank:
    name: str
    x: float
    color: tuple[int, int, int]
    health: int = 100
    angle: float = 45.0
    power: float = 95.0

    def alive(self) -> bool:
        return self.health > 0


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    owner: int
    trail: list[tuple[float, float]] = field(default_factory=list)

    def step(self, dt: float, wind: float) -> None:
        self.trail.append((self.x, self.y))
        if len(self.trail) > 18:
            self.trail.pop(0)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx += wind * dt
        self.vy += GRAVITY * dt


class Terrain:
    """A destructible height map with smooth procedural hills."""

    def __init__(self, width: int = WIDTH, ground_y: int = GROUND_Y, seed: int | None = None) -> None:
        self.width = width
        self.ground_y = ground_y
        self.random = random.Random(seed)
        self.heights: list[float] = []
        self.regenerate()

    def regenerate(self) -> None:
        phase = self.random.random() * math.tau
        points = [
            self.ground_y - 52 - 45 * math.sin(i / self.width * math.tau * 1.35 + phase)
            - 24 * math.sin(i / self.width * math.tau * 3.8 + phase * 0.4)
            for i in range(self.width)
        ]
        # Smooth in a deterministic way while preserving cliff-like variation.
        self.heights = [sum(points[max(0, i - 4): min(self.width, i + 5)]) / len(points[max(0, i - 4): min(self.width, i + 5)]) for i in range(self.width)]

    def surface_y(self, x: float) -> float:
        ix = max(0, min(self.width - 1, int(x)))
        return self.heights[ix]

    def crater(self, x: float, y: float, radius: float) -> None:
        left = max(0, int(x - radius - 2))
        right = min(self.width - 1, int(x + radius + 2))
        for ix in range(left, right + 1):
            distance = abs(ix - x)
            if distance < radius:
                cut = math.sqrt(max(0.0, radius * radius - distance * distance)) * 0.92
                self.heights[ix] = min(self.ground_y + 15, max(self.heights[ix], y + cut))
        # Smooth only around the crater edge to avoid unnatural single-pixel steps.
        for ix in range(max(1, left), min(self.width - 1, right + 1)):
            self.heights[ix] = (self.heights[ix - 1] + self.heights[ix] * 2 + self.heights[ix + 1]) / 4


class Battle:
    """Turn-based artillery simulation."""

    def __init__(self, width: int = WIDTH, height: int = HEIGHT, seed: int | None = None) -> None:
        self.width = width
        self.height = height
        self.random = random.Random(seed)
        self.turn = 0
        self.wind = 0.0
        self.terrain = Terrain(width, GROUND_Y, seed)
        self.tanks: list[Tank] = []
        self.projectile: Projectile | None = None
        self.explosion: tuple[float, float, float, float] | None = None
        self.message = ""
        self.game_over = False
        self.new_round()

    @property
    def active_tank(self) -> Tank:
        return self.tanks[self.turn]

    def new_round(self) -> None:
        self.terrain.regenerate()
        self.tanks = [
            Tank("YOU", self.width * 0.18, (255, 193, 92)),
            Tank("CPU", self.width * 0.82, (255, 105, 110)),
        ]
        for tank in self.tanks:
            tank.health = 100
            tank.angle = 45.0
            tank.power = 95.0
        self.projectile = None
        self.explosion = None
        self.turn = 0
        self.game_over = False
        self.wind = self.random.uniform(-24, 24)
        self.message = "YOUR TURN  ·  SET ANGLE & POWER"

    def tank_y(self, tank: Tank) -> float:
        return self.terrain.surface_y(tank.x) - 15

    def aim(self, angle_delta: float = 0.0, power_delta: float = 0.0) -> None:
        if self.projectile or self.game_over:
            return
        tank = self.active_tank
        tank.angle = max(5.0, min(85.0, tank.angle + angle_delta))
        tank.power = max(20.0, min(MAX_POWER, tank.power + power_delta))

    def fire(self) -> bool:
        if self.projectile or self.game_over or not self.active_tank.alive():
            return False
        tank = self.active_tank
        direction = 1.0 if self.turn == 0 else -1.0
        radians = math.radians(tank.angle)
        speed = tank.power * 3.0
        self.projectile = Projectile(
            tank.x + direction * 17,
            self.tank_y(tank) - 18,
            direction * math.cos(radians) * speed,
            -math.sin(radians) * speed,
            self.turn,
        )
        self.message = f"{tank.name} FIRED"
        return True

    def update(self, dt: float) -> None:
        if not self.projectile:
            return
        self.projectile.step(min(dt, 0.05), self.wind)
        p = self.projectile
        hit_ground = 0 <= p.x < self.width and p.y >= self.terrain.surface_y(p.x)
        off_screen = p.x < -30 or p.x > self.width + 30 or p.y > self.height + 50
        hit_tank = None
        for index, tank in enumerate(self.tanks):
            if index != p.owner and tank.alive() and math.hypot(p.x - tank.x, p.y - self.tank_y(tank)) < 24:
                hit_tank = index
                break
        if hit_ground or hit_tank is not None or off_screen:
            x = max(0.0, min(float(self.width - 1), p.x))
            y = self.terrain.surface_y(x) if hit_ground else p.y
            self.resolve_impact(x, y, hit_tank)

    def resolve_impact(self, x: float, y: float, hit_tank: int | None) -> None:
        p = self.projectile
        if not p:
            return
        radius = 54.0
        self.terrain.crater(x, y, radius)
        for index, tank in enumerate(self.tanks):
            distance = math.hypot(tank.x - x, self.tank_y(tank) - y)
            if tank.alive() and distance < radius + 20:
                damage = max(5, int(48 * (1 - min(distance, radius + 20) / (radius + 20))))
                tank.health = max(0, tank.health - damage)
                if index == hit_tank:
                    self.message = f"DIRECT HIT  ·  {damage} DAMAGE"
        self.projectile = None
        self.explosion = (x, y, radius, 0.0)
        if not self.tanks[0].alive() or not self.tanks[1].alive():
            self.game_over = True
            self.message = "VICTORY" if self.tanks[1].health <= 0 else "DEFEAT"

    def update_effects(self, dt: float) -> None:
        if self.explosion:
            x, y, radius, age = self.explosion
            age += dt
            self.explosion = (x, y, radius, age) if age < 0.45 else None
        if self.projectile is None and self.explosion is None and not self.game_over:
            self.turn = 1 - self.turn
            self.wind = self.random.uniform(-24, 24)
            tank = self.active_tank
            if self.turn == 1:
                self.cpu_turn()
            else:
                self.message = "YOUR TURN  ·  SET ANGLE & POWER"

    def cpu_turn(self) -> None:
        cpu = self.active_tank
        target = self.tanks[0]
        dx = abs(target.x - cpu.x)
        cpu.angle = self.random.uniform(34, 62)
        cpu.power = max(55, min(MAX_POWER, dx / 4.2 + self.random.uniform(-14, 14)))
        self.message = "CPU IS AIMING..."

    def skip_or_reset(self) -> None:
        if self.game_over:
            self.new_round()

    def winner_text(self) -> str:
        if self.tanks[0].health > 0 and self.tanks[1].health > 0:
            return ""
        return "YOU WIN" if self.tanks[1].health <= 0 else "YOU LOSE"


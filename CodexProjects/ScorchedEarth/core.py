"""Deterministic artillery simulation. No dependency on Pygame."""
from dataclasses import dataclass, field
import math
from random import Random

WORLD_W, WORLD_H = 1120, 500
GRAVITY = 230.0
STEP = 1 / 120
TURN_LIMIT = 40


@dataclass(frozen=True)
class Weapon:
    name: str
    radius: int
    damage: int
    description: str


WEAPONS = (
    Weapon("Shell", 38, 55, "Reliable. Unlimited ammunition."),
    Weapon("Heavy", 65, 90, "A larger crater and a heavier punch."),
    Weapon("Cluster", 34, 38, "Splits into five bomblets at the apex."),
    Weapon("Atomic", 115, 155, "A massive blast. Watch the friendly fire."),
)
SHOP = (
    ("Heavy x3", 400, "Three heavy shells.", "heavy"),
    ("Cluster x2", 550, "Two cluster shells.", "cluster"),
    ("Atomic x1", 1100, "One atomic shell.", "atomic"),
    ("Shield +40", 500, "Absorbs damage next round. Maximum 80.", "shield"),
)
SKILLS = ("Cadet", "Veteran", "Expert")


@dataclass
class Player:
    name: str
    cash: int = 900
    wins: int = 0
    damage: int = 0
    ammo: list = field(default_factory=lambda: [-1, 3, 2, 0])
    next_shield: int = 0


@dataclass
class Tank:
    x: float
    y: float
    angle: float
    power: float = 60
    hp: int = 100
    shield: int = 0
    weapon: int = 0

    @property
    def alive(self):
        return self.hp > 0

    def muzzle(self):
        angle = math.radians(self.angle)
        return self.x + math.cos(angle) * 23, self.y - 10 - math.sin(angle) * 23


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    weapon: int
    owner: int
    age: float = 0
    pellet: bool = False


class Terrain:
    def __init__(self, rng):
        phases = [rng.uniform(0, math.tau) for _ in range(4)]
        self.heights = [max(150, min(420, 300 + 63 * math.sin(x / 180 + phases[0])
                        + 32 * math.sin(x / 78 + phases[1])
                        + 16 * math.sin(x / 35 + phases[2])
                        + 10 * math.sin(x / 400 + phases[3]))) for x in range(WORLD_W)]
        self.revision = 0

    def ground(self, x):
        return self.heights[max(0, min(WORLD_W - 1, int(x)))]

    def platform(self, x):
        """Flatten the launch pad, so every generated terrain is playable."""
        y = self.ground(x)
        for i in range(max(0, int(x) - 20), min(WORLD_W, int(x) + 21)):
            self.heights[i] = y
        self.revision += 1

    def support(self, x):
        return min(self.heights[max(0, int(x) - 10):min(WORLD_W, int(x) + 11)])

    def crater(self, x, y, radius):
        for i in range(max(0, int(x - radius)), min(WORLD_W, int(x + radius) + 1)):
            depth = radius * radius - (i - x) ** 2
            if depth >= 0:
                bottom = y + math.sqrt(depth)
                if bottom >= self.heights[i]:
                    self.heights[i] = min(WORLD_H - 15, max(self.heights[i], bottom))
        self.revision += 1


def launch(tank, weapon, owner):
    x, y = tank.muzzle()
    speed = 110 + tank.power * 6
    angle = math.radians(tank.angle)
    return Projectile(x, y, math.cos(angle) * speed, -math.sin(angle) * speed, weapon, owner)


def advance(projectile, dt, wind, terrain, tanks):
    """Exact constant-acceleration integration plus swept collision samples."""
    p = projectile
    nx = p.x + p.vx * dt + .5 * wind * dt * dt
    ny = p.y + p.vy * dt + .5 * GRAVITY * dt * dt
    p.vx += wind * dt
    p.vy += GRAVITY * dt
    p.age += dt
    distance = math.hypot(nx - p.x, ny - p.y)
    # Subpixel spacing visits every crossed terrain column, even a 1px ridge.
    samples = max(1, math.ceil(distance / .75))
    for i in range(1, samples + 1):
        x, y = p.x + (nx - p.x) * i / samples, p.y + (ny - p.y) * i / samples
        if x < 0 or x >= WORLD_W or y > WORLD_H + 20 or p.age > 16:
            p.x, p.y = x, y
            return "miss"
        if y >= terrain.ground(x):
            p.x, p.y = x, y
            return "impact"
        for tank in tanks:
            if tank.alive and abs(x - tank.x) <= 13 and tank.y - 18 <= y <= tank.y + 1:
                p.x, p.y = x, y
                return "impact"
    p.x, p.y = nx, ny
    return "flying"


class Match:
    def __init__(self, seed=None, mode="Solo", skill="Veteran", rounds=3):
        if mode not in ("Solo", "Hotseat") or skill not in SKILLS or type(rounds) is not int or rounds not in (3, 5, 7):
            raise ValueError("Invalid match settings")
        self.rng = Random(seed)
        self.mode, self.skill, self.rounds = mode, skill, rounds
        self.players = [Player("COPPER"), Player("OVERLORD" if mode == "Solo" else "COBALT")]
        self.round = 0
        self.winner = None
        self.match_over = False
        self.shop_player = 0
        self.start_round()

    def start_round(self):
        self.round += 1
        self.terrain = Terrain(self.rng)
        positions = [self.rng.randint(85, 180), self.rng.randint(WORLD_W - 180, WORLD_W - 85)]
        for x in positions:
            self.terrain.platform(x)
        self.tanks = [Tank(x, self.terrain.support(x), 45 if i == 0 else 135,
                           shield=self.players[i].next_shield) for i, x in enumerate(positions)]
        for player in self.players:
            player.next_shield = 0
        self.active = (self.round - 1) % 2
        self.wind = self.rng.randint(-45, 45)
        self.turn = 1
        self.phase = "aim"
        self.projectiles = []
        self.events = []
        self.round_winner = None
        self.message = f"{self.players[self.active].name} has the first shot."

    def available(self, owner, weapon):
        return weapon == 0 or self.players[owner].ammo[weapon] > 0

    def select_weapon(self, delta):
        if self.phase != "aim":
            return
        tank = self.tanks[self.active]
        for _ in WEAPONS:
            tank.weapon = (tank.weapon + delta) % len(WEAPONS)
            if self.available(self.active, tank.weapon):
                break

    def fire(self):
        if self.phase != "aim" or not self.tanks[self.active].alive:
            return False
        tank = self.tanks[self.active]
        if not self.available(self.active, tank.weapon):
            tank.weapon = 0
        if tank.weapon:
            self.players[self.active].ammo[tank.weapon] -= 1
        self.projectiles = [launch(tank, tank.weapon, self.active)]
        self.phase = "flight"
        self.events.append(("fire", tank.x, tank.y, tank.weapon))
        self.message = f"{WEAPONS[tank.weapon].name} away."
        return True

    def damage(self, index, amount, owner):
        tank = self.tanks[index]
        amount = max(0, round(amount))
        absorbed = min(tank.shield, amount)
        tank.shield -= absorbed
        hp_loss = min(tank.hp, amount - absorbed)
        tank.hp -= hp_loss
        if index != owner:
            self.players[owner].cash += (hp_loss + absorbed) * 4
            self.players[owner].damage += hp_loss + absorbed

    def explode(self, p):
        weapon = WEAPONS[p.weapon]
        self.events.append(("blast", p.x, p.y, weapon.radius))
        for i, tank in enumerate(self.tanks):
            if not tank.alive:
                continue
            distance = math.hypot(tank.x - p.x, tank.y - 9 - p.y)
            radius = weapon.radius + 15
            if distance < radius:
                self.damage(i, weapon.damage * max(0, 1 - distance / radius), p.owner)
        self.terrain.crater(p.x, p.y, weapon.radius)
        for i, tank in enumerate(self.tanks):
            ground = self.terrain.support(tank.x)
            drop = max(0, ground - tank.y)
            tank.y = ground
            if tank.alive and drop > 22:
                self.damage(i, (drop - 22) * .65, p.owner)

    def tick(self, dt=STEP):
        if self.phase != "flight":
            return
        survivors = []
        for p in self.projectiles:
            result = advance(p, dt, self.wind, self.terrain, self.tanks)
            if result == "impact":
                self.explode(p)
            elif result == "miss":
                self.events.append(("miss", p.x, p.y, 0))
            elif p.weapon == 2 and not p.pellet and p.vy >= 0:
                for offset in (-90, -45, 0, 45, 90):
                    survivors.append(Projectile(p.x, p.y, p.vx + offset, p.vy + 8,
                                                  2, p.owner, p.age, True))
                self.events.append(("split", p.x, p.y, 0))
            else:
                survivors.append(p)
        self.projectiles = survivors
        if not self.projectiles:
            self.phase = "settle"

    def end_turn(self):
        if self.phase != "settle":
            return
        alive = [i for i, tank in enumerate(self.tanks) if tank.alive]
        if len(alive) < 2 or self.turn >= TURN_LIMIT:
            if len(alive) == 1:
                winner = alive[0]
            elif len(alive) == 2:
                strengths = [t.hp + t.shield for t in self.tanks]
                winner = None if strengths[0] == strengths[1] else strengths.index(max(strengths))
            else:
                winner = None
            self.finish_round(winner)
        else:
            self.active = 1 - self.active
            self.turn += 1
            self.wind = self.rng.randint(-45, 45)
            if not self.available(self.active, self.tanks[self.active].weapon):
                self.tanks[self.active].weapon = 0
            self.phase = "aim"
            self.message = f"{self.players[self.active].name}, choose your trajectory."

    def finish_round(self, winner):
        self.phase = "round_over"
        self.round_winner = winner
        if winner is not None:
            self.players[winner].wins += 1
            self.players[winner].cash += 700
        for player in self.players:
            player.cash += 400
        self.match_over = self.round >= self.rounds
        if self.match_over:
            ranks = [(p.wins, p.damage) for p in self.players]
            self.winner = None if ranks[0] == ranks[1] else ranks.index(max(ranks))
        self.shop_player = 0

    def buy(self, owner, item):
        if self.phase != "round_over" or self.match_over or owner not in (0, 1) or not 0 <= item < len(SHOP):
            return False
        player = self.players[owner]
        _, price, _, kind = SHOP[item]
        if player.cash < price or (kind == "shield" and player.next_shield >= 80):
            return False
        player.cash -= price
        if kind == "shield":
            player.next_shield += 40
        else:
            weapon, count = {"heavy": (1, 3), "cluster": (2, 2), "atomic": (3, 1)}[kind]
            player.ammo[weapon] += count
        return True

    def ai_shop(self):
        for item in (3, 0, 1, 2):
            self.buy(1, item)

    def ai_search(self):
        """Yield after each angle to let the UI process input during planning."""
        owner = self.active
        tank, target = self.tanks[owner], self.tanks[1 - owner]
        best = (float("inf"), tank.angle, tank.power)
        angles = range(20, 86, 4) if owner == 0 else range(94, 161, 4)
        for angle in angles:
            for power in range(24, 101, 4):
                probe_tank = Tank(tank.x, tank.y, angle, power)
                p = launch(probe_tank, 0, owner)
                for _ in range(850):
                    status = advance(p, 1 / 45, self.wind, self.terrain, self.tanks)
                    if status != "flying":
                        distance = math.hypot(p.x - target.x, p.y - target.y + 9)
                        if status == "miss":
                            distance += 200
                        if distance < best[0]:
                            best = (distance, angle, power)
                        break
            yield None
        error = {"Cadet": (5, 7), "Veteran": (2, 3), "Expert": (.4, .8)}[self.skill]
        tank.angle = max(5, min(175, best[1] + self.rng.uniform(-error[0], error[0])))
        tank.power = max(10, min(100, best[2] + self.rng.uniform(-error[1], error[1])))
        # Limited ammunition is meaningful: use the biggest available shot.
        tank.weapon = next((w for w in (3, 1, 2, 0) if self.available(owner, w)), 0)
        return best[0]

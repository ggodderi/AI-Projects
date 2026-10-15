"""Scorched Earth / Python artillery edition. Original implementation and art."""
import argparse
from array import array
import math
import os
from pathlib import Path
from random import Random
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
try:
    import pygame
except ImportError:
    raise SystemExit("Pygame is missing. Run: python -m pip install -r requirements.txt")

from core import GRAVITY, SHOP, SKILLS, STEP, WEAPONS, WORLD_H, WORLD_W, Match, Tank, launch
from persistence import Store

W, H = 1200, 860
ARENA = pygame.Rect(40, 146, WORLD_W, WORLD_H)
BG = (13, 21, 29)
PANEL = (23, 34, 43)
EDGE = (54, 67, 74)
WHITE = (242, 235, 215)
MUTED = (158, 174, 178)
AMBER = (245, 184, 93)
TEAL = (111, 207, 206)
RED = (241, 116, 101)
COLORS = (AMBER, TEAL)


class Audio:
    def __init__(self):
        self.sounds = {}
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            rng = Random(55)
            for name, frequency, duration in (("click", 600, .05), ("fire", 180, .18),
                                               ("blast", 65, .55), ("buy", 880, .13),
                                               ("round", 440, .4)):
                samples = array("h")
                n = int(duration * 22050)
                for i in range(n):
                    t = i / 22050
                    wave = math.sin(math.tau * (frequency * t - frequency * .3 * t * t / duration))
                    if name in ("fire", "blast"):
                        wave = .35 * wave + .65 * rng.uniform(-1, 1)
                    envelope = min(1, i / 60) * (1 - i / n) ** 2
                    samples.append(int(9000 * envelope * wave))
                self.sounds[name] = pygame.mixer.Sound(buffer=samples)
        except pygame.error:
            pass

    def play(self, name, enabled):
        if enabled and name in self.sounds:
            self.sounds[name].play()


class GameApp:
    def __init__(self, store=None):
        pygame.display.init()
        pygame.font.init()
        self.window = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption("Scorched Earth | Python Artillery Edition")
        self.canvas = pygame.Surface((W, H))
        self.fonts = {n: pygame.font.Font(None, n) for n in (18, 20, 22, 24, 28, 32, 38, 48, 58, 76, 96)}
        self.store = store if store is not None else Store()
        self.audio = Audio()
        self.fx_rng = Random(21)
        self.match = Match(seed=42)
        self.screen = "menu"
        self.help_return = "menu"
        self.running = True
        self.buttons = []
        self.selected = 0
        self.viewport = pygame.Rect(0, 0, W, H)
        self.keys = set()
        self.drag = None
        self.accumulator = 0
        self.ai_job = None
        self.ai_time = 0
        self.settle_time = 0
        self.trails = []
        self.blasts = []
        self.particles = []
        self.cache_key = None
        self.terrain_image = None
        self.recorded = False
        self.notice = ""
        self.notice_time = 0
        self.sky = self.make_sky()
        icon = pygame.Surface((32, 32))
        icon.fill(BG)
        pygame.draw.rect(icon, AMBER, (3, 18, 26, 9), border_radius=4)
        pygame.draw.line(icon, AMBER, (16, 18), (25, 6), 4)
        pygame.display.set_icon(icon)

    def make_sky(self):
        surface = pygame.Surface(ARENA.size)
        top, bottom = (24, 37, 61), (152, 102, 82)
        for y in range(WORLD_H):
            f = y / WORLD_H
            color = tuple(int(a + (b - a) * f) for a, b in zip(top, bottom))
            pygame.draw.line(surface, color, (0, y), (WORLD_W, y))
        rng = Random(70)
        for _ in range(48):
            x, y = rng.randrange(WORLD_W), rng.randrange(180)
            pygame.draw.circle(surface, (157, 161, 163), (x, y), 1)
        pygame.draw.circle(surface, (197, 151, 113), (835, 108), 39)
        pygame.draw.circle(surface, (229, 176, 128), (835, 108), 31)
        for offset, color in ((0, (66, 67, 83)), (95, (55, 57, 69))):
            points = [(0, WORLD_H)]
            for x in range(0, WORLD_W + 25, 25):
                y = 255 + offset + 47 * math.sin(x / 130 + offset) + 24 * math.sin(x / 53)
                points.append((x, y))
            points.append((WORLD_W, WORLD_H))
            pygame.draw.polygon(surface, color, points)
        return surface

    def text(self, value, size, color, position, center=False):
        rendered = self.fonts[size].render(str(value), True, color)
        rect = rendered.get_rect(center=position) if center else rendered.get_rect(topleft=position)
        self.canvas.blit(rendered, rect)

    def panel(self, rect, color=PANEL):
        pygame.draw.rect(self.canvas, color, rect, border_radius=12)
        pygame.draw.rect(self.canvas, EDGE, rect, 1, border_radius=12)

    def button(self, label, rect, action, primary=False, enabled=True):
        rect = pygame.Rect(rect)
        focus = self.selected == len(self.buttons)
        color = AMBER if primary and enabled else (38, 53, 62)
        if not enabled:
            color = (28, 38, 45)
        pygame.draw.rect(self.canvas, color, rect, border_radius=8)
        pygame.draw.rect(self.canvas, WHITE if focus and enabled else EDGE, rect, 2 if focus else 1, border_radius=8)
        self.text(label, 24, BG if primary and enabled else WHITE if enabled else (93, 108, 114), rect.center, True)
        self.buttons.append((rect, action, enabled))

    def transition(self, screen):
        self.screen = screen
        self.selected = 0
        self.buttons = []
        self.keys.clear()
        self.drag = None
        self.accumulator = 0

    def toast(self, text):
        self.notice, self.notice_time = text, 2.5

    def new_match(self, seed=None):
        self.match = Match(seed, self.store.mode, self.store.skill, self.store.rounds)
        self.recorded = False
        self.reset_effects()
        self.transition("battle")

    def reset_effects(self):
        self.trails, self.blasts, self.particles = [], [], []
        self.ai_job, self.ai_time = None, 0
        self.settle_time = 0
        self.accumulator = 0

    @property
    def human_turn(self):
        return self.match.phase == "aim" and (self.match.mode == "Hotseat" or self.match.active == 0)

    def act(self, action):
        self.audio.play("click", self.store.sound)
        if action == "play":
            self.new_match()
        elif action == "mode":
            self.store.mode = "Hotseat" if self.store.mode == "Solo" else "Solo"
            self.store.save()
        elif action == "skill":
            self.store.skill = SKILLS[(SKILLS.index(self.store.skill) + 1) % len(SKILLS)]
            self.store.save()
        elif action == "rounds":
            self.store.rounds = {3: 5, 5: 7, 7: 3}[self.store.rounds]
            self.store.save()
        elif action == "sound":
            self.store.sound = not self.store.sound
            self.store.save()
        elif action == "effects":
            self.store.effects = not self.store.effects
            self.store.save()
        elif action == "quit":
            self.running = False
        elif action == "help":
            self.help_return = self.screen
            self.transition("help")
        elif action == "back":
            self.transition(self.help_return)
        elif action == "pause":
            self.transition("pause")
        elif action == "resume":
            self.transition("battle")
        elif action == "leave":
            self.transition("confirm")
        elif action == "cancel":
            self.transition("pause")
        elif action == "menu":
            self.transition("menu")
        elif action == "fire" and self.screen == "battle" and self.human_turn:
            self.match.fire()
            self.keys.clear()
        elif action == "weapon" and self.human_turn:
            self.match.select_weapon(1)
        elif action == "next":
            if self.match.match_over:
                self.transition("final")
            else:
                self.match.shop_player = 0
                self.transition("shop")
        elif action.startswith("buy:"):
            if self.match.buy(self.match.shop_player, int(action.split(":")[1])):
                self.audio.play("buy", self.store.sound)
                self.toast("Supplies added to next round's loadout.")
            else:
                self.toast("Not enough credits, or shield capacity reached.")
        elif action == "ready":
            if self.match.mode == "Hotseat" and self.match.shop_player == 0:
                self.match.shop_player = 1
                self.selected = 0
                self.toast("Pass the controls to COBALT.")
            else:
                if self.match.mode == "Solo":
                    self.match.ai_shop()
                self.match.start_round()
                self.reset_effects()
                self.transition("battle")

    def point(self, pos):
        return ((pos[0] - self.viewport.x) * W / self.viewport.width,
                (pos[1] - self.viewport.y) * H / self.viewport.height)

    def set_slider(self, name, point):
        tank = self.match.tanks[self.match.active]
        if name == "angle":
            tank.angle = round(max(5, min(175, 5 + (point[0] - 64) / 204 * 170)))
        else:
            tank.power = round(max(10, min(100, 10 + (point[0] - 312) / 204 * 90)))

    def event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.keys.clear()
            self.drag = None
            if self.screen == "battle":
                self.transition("pause")
        elif event.type == pygame.KEYUP:
            self.keys.discard(event.key)
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_F11:
                try:
                    if self.window.get_flags() & pygame.FULLSCREEN:
                        self.window = pygame.display.set_mode((W, H), pygame.RESIZABLE)
                    else:
                        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                except pygame.error:
                    self.window = pygame.display.set_mode((W, H), pygame.RESIZABLE)
                    self.toast("Fullscreen unavailable on this display.")
            elif key == pygame.K_m:
                self.act("sound")
            elif key in (pygame.K_F1, pygame.K_h) and self.screen in ("menu", "battle", "pause"):
                self.act("help")
            elif key == pygame.K_ESCAPE:
                if self.screen == "battle":
                    self.act("pause")
                elif self.screen == "pause":
                    self.act("resume")
                elif self.screen == "help":
                    self.act("back")
                elif self.screen == "confirm":
                    self.act("cancel")
            elif self.screen == "battle":
                if key == pygame.K_p:
                    self.act("pause")
                elif self.human_turn:
                    if key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.act("fire")
                    elif key == pygame.K_TAB:
                        self.act("weapon")
                    elif pygame.K_1 <= key <= pygame.K_4:
                        weapon = key - pygame.K_1
                        if self.match.available(self.match.active, weapon):
                            self.match.tanks[self.match.active].weapon = weapon
                    else:
                        self.keys.add(key)
            elif self.buttons:
                if key in (pygame.K_DOWN, pygame.K_TAB, pygame.K_s):
                    self.move_focus(1)
                elif key in (pygame.K_UP, pygame.K_w):
                    self.move_focus(-1)
                elif key in (pygame.K_RETURN, pygame.K_SPACE):
                    _, action, enabled = self.buttons[self.selected % len(self.buttons)]
                    if enabled:
                        self.act(action)
        elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            point = self.point(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drag = None
                return
            if event.type == pygame.MOUSEMOTION and self.drag and self.human_turn and self.screen == "battle":
                self.set_slider(self.drag, point)
                return
            click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            for i, (rect, action, enabled) in enumerate(self.buttons):
                if rect.collidepoint(point):
                    if enabled:
                        self.selected = i
                        if click:
                            self.act(action)
                    return
            if click and self.screen == "battle" and self.human_turn:
                if pygame.Rect(54, 750, 224, 35).collidepoint(point):
                    self.drag = "angle"
                    self.set_slider(self.drag, point)
                elif pygame.Rect(302, 750, 224, 35).collidepoint(point):
                    self.drag = "power"
                    self.set_slider(self.drag, point)
                elif ARENA.collidepoint(point):
                    tank = self.match.tanks[self.match.active]
                    dx, dy = point[0] - ARENA.x - tank.x, tank.y - 10 - point[1] + ARENA.y
                    tank.angle = max(5, min(175, math.degrees(math.atan2(dy, dx))))

    def move_focus(self, delta):
        for _ in self.buttons:
            self.selected = (self.selected + delta) % len(self.buttons)
            if self.buttons[self.selected][2]:
                break

    def collect_events(self):
        for kind, x, y, value in self.match.events:
            if kind == "fire":
                self.trails.clear()
                self.audio.play("fire", self.store.sound)
            elif kind == "blast":
                self.audio.play("blast", self.store.sound)
                self.blasts.append([x, y, value, 0])
                if self.store.effects:
                    for _ in range(42):
                        a = self.fx_rng.uniform(0, math.tau)
                        speed = self.fx_rng.uniform(40, 200)
                        self.particles.append([x, y, math.cos(a) * speed, math.sin(a) * speed - 80,
                                               self.fx_rng.uniform(.4, 1.1)])
        self.match.events.clear()

    def update(self, dt):
        dt = min(dt, .1)
        self.notice_time = max(0, self.notice_time - dt)
        if self.screen != "battle":
            return
        match = self.match
        if match.phase == "aim":
            if self.human_turn:
                tank = match.tanks[match.active]
                fine = pygame.K_LSHIFT in self.keys or pygame.K_RSHIFT in self.keys
                speed = 12 if fine else 45
                left = pygame.K_LEFT in self.keys or pygame.K_a in self.keys
                right = pygame.K_RIGHT in self.keys or pygame.K_d in self.keys
                up = pygame.K_UP in self.keys or pygame.K_w in self.keys
                down = pygame.K_DOWN in self.keys or pygame.K_s in self.keys
                tank.angle = max(5, min(175, tank.angle + (left - right) * speed * dt))
                tank.power = max(10, min(100, tank.power + (up - down) * speed * dt))
            else:
                self.ai_time += dt
                if self.ai_job is None:
                    self.ai_job = match.ai_search()
                try:
                    next(self.ai_job)
                except StopIteration:
                    if self.ai_time > 1.1:
                        match.fire()
                        self.ai_job, self.ai_time = None, 0
        elif match.phase == "flight":
            self.accumulator += dt
            while self.accumulator >= STEP and match.phase == "flight":
                match.tick()
                self.accumulator -= STEP
            for p in match.projectiles:
                self.trails.append((p.x, p.y, p.owner))
            self.trails = self.trails[-500:]
            self.settle_time = 0
        elif match.phase == "settle":
            self.settle_time += dt
            if self.settle_time >= 1:
                match.end_turn()
                self.accumulator = 0
                self.ai_job, self.ai_time = None, 0
                if match.phase == "round_over":
                    self.audio.play("round", self.store.sound)
                    if match.match_over and not self.recorded:
                        if match.mode == "Solo":
                            self.store.matches += 1
                            self.store.wins += int(match.winner == 0)
                            self.store.save()
                        self.recorded = True
                    self.transition("results")
        self.collect_events()
        for blast in self.blasts:
            blast[3] += dt
        self.blasts = [b for b in self.blasts if b[3] < .8]
        for p in self.particles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 260 * dt
            p[4] -= dt
        self.particles = [p for p in self.particles if p[4] > 0]

    def terrain_surface(self):
        terrain = self.match.terrain
        key = (id(terrain), terrain.revision)
        if key == self.cache_key:
            return self.terrain_image
        surface = pygame.Surface(ARENA.size, pygame.SRCALPHA)
        points = [(0, WORLD_H), *[(x, y) for x, y in enumerate(terrain.heights)], (WORLD_W, WORLD_H)]
        pygame.draw.polygon(surface, (94, 67, 56), points)
        for depth, color in ((20, (112, 78, 60)), (48, (82, 60, 53)), (95, (69, 54, 50))):
            points = [(0, WORLD_H)] + [(x, min(WORLD_H, y + depth + 5 * math.sin(x / 27)))
                      for x, y in enumerate(terrain.heights)] + [(WORLD_W, WORLD_H)]
            pygame.draw.polygon(surface, color, points)
        pygame.draw.lines(surface, (188, 139, 91), False, list(enumerate(terrain.heights)), 2)
        # Stable, generated sediment details; these never affect simulation.
        for x in range(7, WORLD_W, 23):
            y = int(terrain.heights[x])
            for depth in (34, 78, 128):
                if y + depth < WORLD_H:
                    pygame.draw.line(surface, (122, 85, 63), (x, y + depth), (x + 4, y + depth), 1)
        self.cache_key, self.terrain_image = key, surface
        return surface

    def draw_tank(self, tank, index):
        x, y = round(tank.x) + ARENA.x, round(tank.y) + ARENA.y
        color = COLORS[index] if tank.alive else (74, 71, 66)
        if tank.shield > 0 and tank.alive:
            pygame.draw.circle(self.canvas, TEAL, (x, y - 8), 27, 1)
        pygame.draw.rect(self.canvas, (25, 29, 30), (x - 19, y - 9, 38, 12), border_radius=6)
        for wx in (-12, -4, 4, 12):
            pygame.draw.circle(self.canvas, (99, 101, 91), (x + wx, y - 3), 3)
        pygame.draw.polygon(self.canvas, color, [(x - 15, y - 9), (x - 11, y - 17),
                                                (x + 9, y - 17), (x + 17, y - 9)])
        if tank.alive:
            mx, my = tank.muzzle()
            pygame.draw.line(self.canvas, color, (x, y - 11), (round(mx) + ARENA.x, round(my) + ARENA.y), 5)
            pygame.draw.circle(self.canvas, WHITE, (x, y - 13), 3)
            if self.match.active == index and self.match.phase == "aim":
                pygame.draw.polygon(self.canvas, color, [(x - 5, y - 51), (x + 5, y - 51), (x, y - 44)])
        else:
            pygame.draw.line(self.canvas, (37, 33, 32), (x - 9, y - 17), (x + 7, y - 4), 3)

    def draw_scene(self):
        self.canvas.blit(self.sky, ARENA)
        self.canvas.blit(self.terrain_surface(), ARENA)
        old_clip = self.canvas.get_clip()
        self.canvas.set_clip(ARENA)
        for x, y, owner in self.trails[::2]:
            pygame.draw.circle(self.canvas, (171, 143, 110) if owner == 0 else (112, 153, 161),
                               (round(x) + ARENA.x, round(y) + ARENA.y), 1)
        for i, tank in enumerate(self.match.tanks):
            self.draw_tank(tank, i)
        if self.screen == "battle" and self.human_turn:
            tank = self.match.tanks[self.match.active]
            p = launch(tank, tank.weapon, self.match.active)
            for i in range(1, 10):
                t = i * .055
                x = p.x + p.vx * t + .5 * self.match.wind * t * t
                y = p.y + p.vy * t + .5 * GRAVITY * t * t
                if x < 0 or x >= WORLD_W or y >= self.match.terrain.ground(x):
                    break
                pygame.draw.circle(self.canvas, COLORS[self.match.active],
                                   (round(x) + ARENA.x, round(y) + ARENA.y), 2)
        for p in self.match.projectiles:
            pygame.draw.circle(self.canvas, WHITE, (round(p.x) + ARENA.x, round(p.y) + ARENA.y), 3)
            pygame.draw.circle(self.canvas, AMBER, (round(p.x) + ARENA.x, round(p.y) + ARENA.y), 5, 1)
        for x, y, radius, age in self.blasts:
            progress = age / .8
            r = max(1, round(radius * min(1, progress * 3)))
            pos = (round(x) + ARENA.x, round(y) + ARENA.y)
            if progress < .5:
                pygame.draw.circle(self.canvas, (240, 149, 69), pos, r)
                pygame.draw.circle(self.canvas, (255, 222, 144), pos, max(1, round(r * .6)))
            pygame.draw.circle(self.canvas, (231, 173, 104), pos, r, max(1, round(4 * (1 - progress))))
        for x, y, vx, vy, life in self.particles:
            pygame.draw.circle(self.canvas, AMBER if life > .35 else (143, 96, 70),
                               (round(x) + ARENA.x, round(y) + ARENA.y), 2)
        self.canvas.set_clip(old_clip)
        pygame.draw.rect(self.canvas, EDGE, ARENA, 1)
        # Status plates remain readable against every generated landscape.
        for i, tank in enumerate(self.match.tanks):
            x = 58 if i == 0 else 924
            pygame.draw.rect(self.canvas, BG, (x, 161, 218, 73), border_radius=8)
            self.text(self.match.players[i].name, 22, COLORS[i], (x + 12, 171))
            self.text(f"{tank.hp:03d} HP", 20, WHITE, (x + 135, 173))
            pygame.draw.rect(self.canvas, EDGE, (x + 12, 200, 194, 5), border_radius=2)
            pygame.draw.rect(self.canvas, COLORS[i], (x + 12, 200, round(194 * tank.hp / 100), 5), border_radius=2)
            self.text(f"SHIELD {tank.shield:02d}   /   WINS {self.match.players[i].wins}", 18, MUTED, (x + 12, 214))
        if self.match.projectiles and all(p.y < 0 for p in self.match.projectiles):
            self.text("SHELL ABOVE THE HORIZON", 20, WHITE, (600, 164), True)

    def slider(self, name, x, value, low, high, label):
        self.panel(pygame.Rect(x, 704, 240, 104))
        self.text(label, 20, MUTED, (x + 16, 718))
        self.text(f"{value:05.1f}" + (" deg" if name == "angle" else " %"), 32, WHITE, (x + 16, 741))
        pygame.draw.line(self.canvas, EDGE, (x + 24, 781), (x + 228, 781), 4)
        ratio = (value - low) / (high - low)
        end = x + 24 + round(204 * ratio)
        pygame.draw.line(self.canvas, AMBER, (x + 24, 781), (end, 781), 4)
        pygame.draw.circle(self.canvas, WHITE, (end, 781), 6)

    def draw_battle(self):
        match, tank = self.match, self.match.tanks[self.match.active]
        self.text("SCORCHED EARTH", 38, WHITE, (40, 30))
        self.text("PYTHON ARTILLERY EDITION", 18, AMBER, (42, 70))
        self.text(f"ROUND {match.round:02d} / {match.rounds:02d}", 24, WHITE, (417, 33))
        self.text(f"TURN {match.turn:02d} / 40", 20, MUTED, (417, 65))
        self.panel(pygame.Rect(655, 27, 274, 65))
        direction = "CALM" if match.wind == 0 else ("RIGHT >>" if match.wind > 0 else "<< LEFT")
        self.text("WIND", 18, MUTED, (670, 37))
        self.text(f"{direction}   {abs(match.wind):02d}", 28, TEAL, (670, 57))
        self.button("Pause / Esc", (968, 31, 192, 56), "pause")
        self.text("BALLISTIC RANGE / DESTRUCTIBLE TERRAIN", 18, MUTED, (42, 118))
        self.text("HOTSEAT" if match.mode == "Hotseat" else "AI / " + match.skill.upper(), 18, MUTED, (959, 118))
        self.draw_scene()
        phase = (f"{match.players[match.active].name} / AIM & FIRE" if self.human_turn else
                 "OVERLORD / CALCULATING TRAJECTORY" if match.phase == "aim" else
                 "SHOT IN FLIGHT" if match.phase == "flight" else "ASSESSING THE IMPACT")
        self.text(phase, 22, COLORS[match.active], (42, 671))
        self.text(match.message, 20, MUTED, (590, 672))
        self.slider("angle", 40, tank.angle, 5, 175, "01 / BARREL ANGLE")
        self.slider("power", 288, tank.power, 10, 100, "02 / LAUNCH POWER")
        self.panel(pygame.Rect(536, 704, 325, 104))
        ammo = match.players[match.active].ammo[tank.weapon]
        ammo_label = "UNLIMITED" if ammo == -1 else f"{ammo} REMAINING"
        self.text("03 / ORDNANCE", 20, MUTED, (552, 718))
        self.button(WEAPONS[tank.weapon].name + "  /  " + ("INF" if ammo == -1 else str(ammo)),
                    (552, 743, 293, 36), "weapon", enabled=self.human_turn)
        self.text(ammo_label + "   /   TAB TO CYCLE", 18, MUTED, (553, 787))
        self.button("FIRE  /  SPACE", (877, 704, 283, 65), "fire", True, self.human_turn)
        self.text("SHIFT for precise adjustments", 18, MUTED, (889, 787))
        self.text("LEFT / RIGHT  Angle     UP / DOWN  Power     TAB / 1-4  Weapon     H  Help     M  Sound     F11  Fullscreen",
                  20, MUTED, (600, 837), True)

    def dim(self):
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        layer.fill((6, 12, 18, 220))
        self.canvas.blit(layer, (0, 0))

    def draw_menu(self):
        self.draw_scene()
        self.dim()
        self.text("CLASSIC ARTILLERY / REBUILT", 22, AMBER, (91, 198))
        self.text("SCORCHED", 96, WHITE, (85, 242))
        self.text("EARTH", 96, WHITE, (85, 319))
        self.text("One hillside. Two tanks. No second chances.", 28, MUTED, (91, 430))
        self.text("Read the wind. Shape the battlefield.", 24, MUTED, (91, 470))
        self.text("Spend your winnings. Take the next ridge.", 24, MUTED, (91, 500))
        pygame.draw.line(self.canvas, AMBER, (91, 559), (168, 559), 3)
        self.text("SOLO CAREER", 20, AMBER, (91, 591))
        self.text(f"{self.store.matches} matches completed  /  {self.store.wins} victories", 24, WHITE, (91, 621))
        self.text("Original code, procedural landscapes & synthesized sound.", 20, MUTED, (91, 720))
        self.panel(pygame.Rect(720, 180, 398, 558))
        self.text("MISSION SETUP", 24, WHITE, (749, 207))
        self.text("Choose your opponent and campaign.", 20, MUTED, (749, 241))
        entries = [("Deploy", "play", True),
                   ("Mode / " + ("Solo vs AI" if self.store.mode == "Solo" else "Two-player hotseat"), "mode", False),
                   ("AI / " + self.store.skill, "skill", False),
                   (f"Campaign / {self.store.rounds} rounds", "rounds", False),
                   ("Field manual", "help", False), ("Quit", "quit", False)]
        for i, (label, action, primary) in enumerate(entries):
            self.button(label, (748, 291 + i * 65, 342, 50), action, primary)
        self.text("TAB / ARROWS to select  /  ENTER to confirm", 18, MUTED, (919, 711), True)
        self.text("PYTHON + PYGAME  /  v1.0", 18, MUTED, (91, 801))

    def draw_help(self):
        self.dim()
        self.panel(pygame.Rect(140, 93, 920, 680))
        self.text("FIELD MANUAL", 48, WHITE, (179, 126))
        self.text("Aim high. Watch the wind. Leave a crater.", 24, AMBER, (180, 183))
        lines = [
            ("AIM & FIRE", "Left / Right rotate the barrel. Up / Down set power. Hold Shift for precision."),
            ("MOUSE", "Click the landscape to aim; drag the angle and power sliders; click FIRE."),
            ("ORDNANCE", "Tab cycles weapons. Keys 1-4 select Shell, Heavy, Cluster, Atomic."),
            ("BALLISTICS", "Angles are measured from the right: 45 fires right, 135 fires left."),
            ("THE WIND", "The wind pushes shells in the arrow's direction. It changes every turn."),
            ("DAMAGE", "Blasts damage both tanks. Craters cause falls. Shields absorb damage first."),
            ("CAMPAIGN", "Win rounds by surviving. After 40 turns, highest HP + shield wins the round."),
            ("SUPPLIES", "Earn 4 credits per damage, 400 per round, and a 700-credit victory bonus."),
            ("THE SHOP", "Ammo carries over. HP resets each round. Bought shields apply next round."),
            ("VICTORY", "Most round wins takes the match. Total enemy damage breaks ties."),
        ]
        for i, (label, line) in enumerate(lines):
            y = 231 + i * 42
            self.text(label, 18, TEAL, (180, y))
            self.text(line, 20, WHITE, (307, y))
        self.text("Esc / P pause  |  M sound  |  F11 fullscreen  |  Focus loss automatically pauses.",
                  20, MUTED, (180, 673))
        self.button("Return / Esc", (780, 713, 239, 42), "back", True)

    def draw_pause(self):
        self.dim()
        self.panel(pygame.Rect(370, 181, 460, 498))
        self.text("CEASE FIRE", 20, AMBER, (600, 223), True)
        self.text("Paused", 58, WHITE, (600, 270), True)
        self.text("The battlefield can wait.", 24, MUTED, (600, 316), True)
        for i, (label, action) in enumerate([
            ("Resume", "resume"), ("Field manual", "help"),
            ("Sound / " + ("On" if self.store.sound else "Off"), "sound"),
            ("Particles / " + ("On" if self.store.effects else "Off"), "effects"),
            ("Leave match", "leave")]):
            self.button(label, (410, 353 + i * 57, 380, 44), action, i == 0)

    def draw_confirm(self):
        self.dim()
        self.panel(pygame.Rect(350, 280, 500, 280))
        self.text("Leave this match?", 48, WHITE, (600, 333), True)
        self.text("Current campaign progress will be lost.", 24, MUTED, (600, 390), True)
        self.button("Keep playing", (386, 455, 202, 54), "cancel", True)
        self.button("Leave match", (610, 455, 202, 54), "menu")

    def result_cards(self, y):
        for i, player in enumerate(self.match.players):
            x = 230 + i * 390
            self.panel(pygame.Rect(x, y, 350, 174))
            self.text(player.name, 28, COLORS[i], (x + 24, y + 23))
            self.text(f"{player.wins:02d}", 58, WHITE, (x + 24, y + 60))
            self.text("ROUND WINS", 18, MUTED, (x + 116, y + 82))
            self.text(f"DAMAGE {player.damage}   /   CREDITS {player.cash:,}", 20, MUTED, (x + 24, y + 140))

    def draw_results(self, final=False):
        self.dim()
        match = self.match
        self.text("CAMPAIGN COMPLETE" if final else f"ROUND {match.round:02d} / AFTER-ACTION REPORT",
                  22, AMBER, (600, 183), True)
        winner = match.winner if final else match.round_winner
        heading = "A hard-fought draw." if winner is None else match.players[winner].name + (" wins the match." if final else " takes the ridge.")
        self.text(heading, 58, WHITE, (600, 247), True)
        self.text("Most wins, then total enemy damage." if final else "400 credits for deployment. 700 bonus for the round winner.",
                  24, MUTED, (600, 302), True)
        self.result_cards(358)
        if final:
            self.button("Deploy again", (370, 593, 220, 56), "play", True)
            self.button("Main menu", (610, 593, 220, 56), "menu")
            self.text("Solo career saved locally." if match.mode == "Solo" else "Hotseat results do not change your solo career.",
                      20, MUTED, (600, 701), True)
        else:
            self.button("View final results" if match.match_over else "Visit supply depot", (420, 592, 360, 58), "next", True)

    def draw_shop(self):
        self.dim()
        owner = self.match.shop_player
        player = self.match.players[owner]
        self.text("SUPPLY DEPOT", 48, WHITE, (120, 113))
        self.text(f"{player.name} / PREPARE FOR ROUND {self.match.round + 1}", 24, COLORS[owner], (122, 167))
        self.text(f"{player.cash:,} CREDITS", 32, AMBER, (851, 123))
        self.text("Full health next round. Ammo carries over. Shields protect one round.", 24, MUTED, (122, 217))
        for i, (name, price, description, kind) in enumerate(SHOP):
            y = 273 + i * 97
            self.panel(pygame.Rect(120, y, 960, 80))
            self.text(name, 28, WHITE, (143, y + 15))
            self.text(description, 20, MUTED, (143, y + 48))
            if i < 3:
                stock = f"OWNED {player.ammo[i + 1]}"
            else:
                stock = f"NEXT SHIELD {player.next_shield}/80"
            self.text(stock, 20, TEAL, (641, y + 31))
            enabled = player.cash >= price and (kind != "shield" or player.next_shield < 80)
            self.button(f"Buy / {price:,}", (867, y + 15, 190, 50), f"buy:{i}", enabled=enabled)
        label = "COBALT's supplies >>" if self.match.mode == "Hotseat" and owner == 0 else "Deploy next round >>"
        self.button(label, (740, 719, 340, 58), "ready", True)
        self.text("ENTER buys selected item. TAB / ARROWS change selection.", 20, MUTED, (120, 745))

    def render(self):
        self.canvas.fill(BG)
        self.buttons = []
        if self.screen == "menu":
            self.draw_menu()
        else:
            self.draw_battle()
            if self.screen != "battle":
                self.buttons = []
                if self.screen == "help":
                    self.draw_help()
                elif self.screen == "pause":
                    self.draw_pause()
                elif self.screen == "confirm":
                    self.draw_confirm()
                elif self.screen in ("results", "final"):
                    self.draw_results(self.screen == "final")
                elif self.screen == "shop":
                    self.draw_shop()
        if self.buttons and self.selected >= len(self.buttons):
            self.selected = 0
        if self.notice_time > 0:
            self.panel(pygame.Rect(310, 807, 580, 37))
            self.text(self.notice, 20, WHITE, (600, 826), True)
        if self.store.error:
            self.text(self.store.error, 20, RED, (600, 849), True)
        ww, wh = self.window.get_size()
        scale = min(ww / W, wh / H)
        size = (max(1, int(W * scale)), max(1, int(H * scale)))
        self.viewport = pygame.Rect((ww - size[0]) // 2, (wh - size[1]) // 2, *size)
        self.window.fill(BG)
        frame = self.canvas if size == (W, H) else pygame.transform.smoothscale(self.canvas, size)
        self.window.blit(frame, self.viewport)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        self.render()
        try:
            while self.running:
                dt = clock.tick(60) / 1000
                for event in pygame.event.get():
                    self.event(event)
                self.update(dt)
                self.render()
        finally:
            self.store.save()
            pygame.quit()


def smoke_test(output):
    """Drive real Pygame input and render the full match and shop flow."""
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        app = GameApp(Store(Path(directory) / "profile.json"))
        output.mkdir(parents=True, exist_ok=True)

        def shot(name):
            app.render()
            pygame.image.save(app.canvas, str(output / (name + ".png")))

        def key(value):
            app.event(pygame.event.Event(pygame.KEYDOWN, key=value))
            app.event(pygame.event.Event(pygame.KEYUP, key=value))

        try:
            shot("01-menu")
            app.act("help")
            shot("02-manual")
            key(pygame.K_ESCAPE)
            assert app.screen == "menu"
            app.render()
            key(pygame.K_RETURN)
            assert app.screen == "battle"
            app.new_match(seed=72)
            app.render()
            app.event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(185, 779), button=1))
            app.event(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(185, 779), button=1))
            assert 90 < app.match.tanks[0].angle < 120
            app.match.tanks[0].angle, app.match.tanks[0].power = 44, 65
            shot("03-battle")
            key(pygame.K_SPACE)
            assert app.match.phase == "flight"
            for _ in range(12):
                app.update(1 / 60)
            app.event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
            age = app.match.projectiles[0].age if app.match.projectiles else 0
            app.update(1)
            assert app.screen == "pause"
            assert not app.match.projectiles or app.match.projectiles[0].age == age
            shot("04-pause")
            key(pygame.K_ESCAPE)
            for _ in range(1000):
                app.update(1 / 60)
                if app.match.phase == "aim" and app.match.active == 1:
                    break
            assert app.match.active == 1
            for _ in range(300):
                app.update(1 / 60)
                if app.match.phase == "flight":
                    break
            assert app.match.phase == "flight", "AI must take its shot"
            for _ in range(1000):
                app.update(1 / 60)
                if app.match.phase != "flight":
                    break
            shot("05-impact")
            app.match.tanks[1].hp = 0
            app.match.projectiles = []
            app.match.phase = "settle"
            app.settle_time = 1
            app.update(1 / 60)
            assert app.screen == "results"
            shot("06-round-results")
            app.act("next")
            assert app.screen == "shop"
            ammo = app.match.players[0].ammo[1]
            app.render()
            app.event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(950, 310), button=1))
            assert app.match.players[0].ammo[1] == ammo + 3
            shot("07-depot")
            app.act("ready")
            assert app.match.round == 2 and app.screen == "battle"
            app.match.round = app.match.rounds
            app.match.tanks[1].hp = 0
            app.match.phase = "settle"
            app.settle_time = 1
            app.update(1 / 60)
            app.act("next")
            assert app.screen == "final" and app.store.matches == 1
            assert Store(app.store.path).matches == 1
            shot("08-campaign-results")
            app.window = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
            app.render()
            assert app.viewport.width <= 800 and app.viewport.height <= 600
            # A second player's shop and turn must remain human-controlled.
            app.store.mode = "Hotseat"
            app.new_match(seed=10)
            app.match.finish_round(0)
            app.transition("shop")
            app.act("ready")
            assert app.match.shop_player == 1 and app.screen == "shop"
            app.act("ready")
            assert app.match.round == 2 and app.match.active == 1 and app.human_turn
            app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
            previous_power = app.match.tanks[1].power
            app.update(.1)
            assert app.match.tanks[1].power > previous_power
            app.event(pygame.event.Event(pygame.KEYUP, key=pygame.K_UP))
            app.act("pause")
            app.act("leave")
            assert app.screen == "confirm"
            app.act("cancel")
            assert app.screen == "pause"
            app.act("resume")
            assert app.screen == "battle"
            # Verify letterboxed mouse coordinates still map to the right control.
            app.render()
            vx, vy, vw, vh = app.viewport
            mouse = (round(vx + 1018 * vw / W), round(vy + 737 * vh / H))
            app.event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=mouse, button=1))
            assert app.match.phase == "flight"
            app.event(pygame.event.Event(pygame.QUIT))
            assert not app.running
            print("PASS: rendering, keyboard, mouse, aiming, firing, pause, AI, results, shopping, next round, career save, hotseat, abandon confirmation, scaled input, resize, quit")
        finally:
            pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Scorched Earth / Python Artillery Edition")
    parser.add_argument("--smoke-test", type=Path, metavar="SCREENSHOT_DIR")
    args = parser.parse_args()
    if args.smoke_test:
        smoke_test(args.smoke_test)
    else:
        GameApp().run()


if __name__ == "__main__":
    main()

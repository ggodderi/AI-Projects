"""Classic Snake: run with Python 3.10+ and pygame 2.6.1."""
import argparse
from array import array
import math
import os
from pathlib import Path
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
try:
    import pygame
except ImportError:
    raise SystemExit("Pygame is missing. Run: python -m pip install -r requirements.txt")

from snake_core import DIFFICULTIES, SnakeGame
from storage import Store

WIDTH, HEIGHT = 1000, 820
CELL = 28
BOARD = pygame.Rect(80, 130, 840, 616)
BG = (11, 19, 22)
PANEL = (20, 31, 34)
TEXT = (232, 242, 235)
MUTED = (139, 161, 155)
GREEN = (177, 242, 112)
RED = (255, 124, 103)
KEYS = {pygame.K_UP: "up", pygame.K_w: "up", pygame.K_DOWN: "down", pygame.K_s: "down",
        pygame.K_LEFT: "left", pygame.K_a: "left", pygame.K_RIGHT: "right", pygame.K_d: "right"}


class Audio:
    def __init__(self):
        self.sounds = {}
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            for name, frequency, duration in [("eat", 740, .09), ("dead", 140, .28),
                                               ("click", 420, .045), ("won", 990, .35)]:
                samples = array("h")
                count = int(22050 * duration)
                for i in range(count):
                    envelope = min(1, i / 100) * (1 - i / count) ** 2
                    samples.append(int(6000 * envelope * math.sin(2 * math.pi * frequency * i / 22050)))
                self.sounds[name] = pygame.mixer.Sound(buffer=samples)
        except pygame.error:
            pass

    def play(self, name, enabled):
        if enabled and name in self.sounds:
            self.sounds[name].play()


class App:
    def __init__(self, store=None):
        pygame.display.init()
        pygame.font.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("SNAKE / Classic Arcade")
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.fonts = {size: pygame.font.Font(None, size) for size in (20, 23, 26, 30, 36, 48, 64, 96)}
        self.store = store if store is not None else Store()
        self.audio = Audio()
        self.game = SnakeGame()
        self.state = "menu"
        self.running = True
        self.accumulator = 0
        self.elapsed = 0
        self.buttons = []
        self.selected = 0
        self.new_best = False
        self.viewport = pygame.Rect(0, 0, WIDTH, HEIGHT)
        icon = pygame.Surface((32, 32))
        icon.fill(BG)
        pygame.draw.rect(icon, GREEN, (5, 5, 22, 22), border_radius=6)
        pygame.draw.circle(icon, BG, (21, 11), 2)
        pygame.display.set_icon(icon)

    def text(self, value, size, color, position, center=False):
        surface = self.fonts[size].render(str(value), True, color)
        rect = surface.get_rect(center=position) if center else surface.get_rect(topleft=position)
        self.canvas.blit(surface, rect)

    def transition(self, state):
        self.state = state
        self.selected = 0
        self.accumulator = 0
        self.buttons = []

    def start(self):
        self.game.reset()
        self.elapsed = 0
        self.new_best = False
        self.transition("playing")

    def perform(self, action):
        self.audio.play("click", self.store.sound)
        if action in ("start", "retry"):
            self.start()
        elif action == "resume":
            self.transition("playing")
        elif action == "menu":
            self.transition("menu")
        elif action == "difficulty":
            choices = list(DIFFICULTIES)
            self.store.difficulty = choices[(choices.index(self.store.difficulty) + 1) % len(choices)]
            self.store.save()
        elif action == "sound":
            self.store.sound = not self.store.sound
            self.store.save()
        elif action == "quit":
            self.running = False

    def mouse_position(self, position):
        return ((position[0] - self.viewport.x) * WIDTH / self.viewport.width,
                (position[1] - self.viewport.y) * HEIGHT / self.viewport.height)

    def event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.WINDOWFOCUSLOST and self.state == "playing":
            self.transition("paused")
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_F11:
                if self.window.get_flags() & pygame.FULLSCREEN:
                    self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                else:
                    self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            elif key == pygame.K_m:
                self.perform("sound")
            elif self.state == "playing":
                if key in KEYS:
                    self.game.turn(KEYS[key])
                elif key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
                    self.transition("paused")
            elif self.state == "paused" and key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
                self.perform("resume")
            elif key == pygame.K_ESCAPE:
                self.perform("quit" if self.state == "menu" else "menu")
            elif key == pygame.K_r and self.state == "over":
                self.start()
            elif key == pygame.K_SPACE and self.state in ("menu", "over"):
                self.start()
            elif self.buttons:
                if key in (pygame.K_DOWN, pygame.K_s, pygame.K_TAB):
                    self.selected = (self.selected + 1) % len(self.buttons)
                elif key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.buttons)
                elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.perform(self.buttons[self.selected][1])
                elif key in (pygame.K_LEFT, pygame.K_RIGHT) and self.state == "menu":
                    self.perform("difficulty")
        elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            point = self.mouse_position(event.pos)
            for index, (rect, action) in enumerate(self.buttons):
                if rect.collidepoint(point):
                    self.selected = index
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.perform(action)
                    break

    def update(self, dt):
        if self.state != "playing":
            return
        self.elapsed += dt
        self.accumulator += min(dt, .25)
        # A bounded increase rewards mastery without making the endgame impossible.
        interval = 1 / min(22, DIFFICULTIES[self.store.difficulty] + self.game.score // 50)
        while self.accumulator >= interval and self.state == "playing":
            self.accumulator -= interval
            result = self.game.step()
            if result in ("eat", "dead", "won"):
                self.audio.play(result, self.store.sound)
            if result in ("dead", "won"):
                name = self.store.difficulty
                self.new_best = self.game.score > self.store.best[name]
                self.store.best[name] = max(self.game.score, self.store.best[name])
                self.store.save()
                self.transition("over")

    def button(self, label, y, action, primary=False):
        rect = pygame.Rect(320, y, 360, 52)
        focused = len(self.buttons) == self.selected
        color = GREEN if primary else (39, 55, 53)
        pygame.draw.rect(self.canvas, color, rect, border_radius=10)
        if focused:
            pygame.draw.rect(self.canvas, TEXT, rect.inflate(6, 6), 2, border_radius=12)
        self.text(label, 26, BG if primary else TEXT, rect.center, True)
        self.buttons.append((rect, action))

    def draw_board(self):
        pygame.draw.rect(self.canvas, (16, 28, 29), BOARD, border_radius=8)
        for y in range(22):
            for x in range(30):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(self.canvas, (18, 31, 31),
                                     (BOARD.x + x * CELL, BOARD.y + y * CELL, CELL, CELL))
        pygame.draw.rect(self.canvas, (49, 70, 62), BOARD.inflate(4, 4), 2, border_radius=8)
        if self.game.food:
            x, y = self.game.food
            center = (BOARD.x + x * CELL + CELL // 2, BOARD.y + y * CELL + CELL // 2)
            pygame.draw.circle(self.canvas, (64, 37, 34), center, 13)
            pygame.draw.circle(self.canvas, RED, center, 9)
            pygame.draw.circle(self.canvas, (255, 197, 172), (center[0] - 3, center[1] - 3), 3)
        for i, (x, y) in enumerate(reversed(self.game.snake)):
            head = i == len(self.game.snake) - 1
            rect = pygame.Rect(BOARD.x + x * CELL + 2, BOARD.y + y * CELL + 2, CELL - 4, CELL - 4)
            pygame.draw.rect(self.canvas, GREEN if head else (108, 186, 87), rect, border_radius=6)
            if head:
                dx, dy = self.game.direction
                cx, cy = rect.center
                for side in (-1, 1):
                    eye = (cx + dx * 6 + abs(dy) * side * 5, cy + dy * 6 + abs(dx) * side * 5)
                    pygame.draw.circle(self.canvas, BG, eye, 2)

    def render(self):
        self.canvas.fill(BG)
        self.buttons = []
        self.text("S N A K E", 36, GREEN, (80, 37))
        self.text("CLASSIC ARCADE", 20, MUTED, (81, 77))
        self.text("SCORE", 20, MUTED, (570, 36))
        self.text(f"{self.game.score:04d}", 36, TEXT, (570, 60))
        self.text("BEST / " + self.store.difficulty.upper(), 20, MUTED, (730, 36))
        best = max(self.store.best[self.store.difficulty], self.game.score)
        self.text(f"{best:04d}", 36, GREEN, (730, 60))
        self.draw_board()
        self.text("ARROWS / WASD  Move     SPACE / P  Pause     M  Sound     F11  Fullscreen",
                  20, MUTED, (500, 779), True)
        if self.state != "playing":
            shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shade.fill((5, 12, 14, 205))
            self.canvas.blit(shade, (0, 0))
            panel = pygame.Rect(260, 170, 480, 500)
            pygame.draw.rect(self.canvas, PANEL, panel, border_radius=20)
            pygame.draw.rect(self.canvas, (49, 68, 60), panel, 1, border_radius=20)
            if self.state == "menu":
                self.text("THE ORIGINAL CHASE", 20, GREEN, (500, 211), True)
                self.text("SNAKE", 96, TEXT, (500, 269), True)
                self.text("Eat. Grow. Keep going.", 26, MUTED, (500, 325), True)
                self.button("Play", 366, "start", True)
                self.button("Difficulty   /   " + self.store.difficulty, 430, "difficulty")
                self.button("Sound   /   " + ("On" if self.store.sound else "Off"), 494, "sound")
                self.button("Quit", 558, "quit")
                self.text("Avoid the walls and your own tail.", 23, MUTED, (500, 643), True)
            elif self.state == "paused":
                self.text("TAKE A BREATHER", 20, GREEN, (500, 224), True)
                self.text("Paused", 64, TEXT, (500, 282), True)
                self.text("Your next move can wait.", 26, MUTED, (500, 336), True)
                self.button("Resume", 383, "resume", True)
                self.button("Sound   /   " + ("On" if self.store.sound else "Off"), 447, "sound")
                self.button("Main menu", 511, "menu")
                self.text("SPACE / P / ESC to resume", 23, MUTED, (500, 622), True)
            else:
                self.text("BOARD COMPLETE" if self.game.won else "ONE MORE ROUND?", 20, GREEN, (500, 220), True)
                self.text("You win!" if self.game.won else "Game over", 64, TEXT, (500, 277), True)
                self.text(f"{self.game.score:04d}", 64, GREEN, (500, 351), True)
                label = "NEW HIGH SCORE" if self.new_best else f"{self.store.difficulty}  /  {int(self.elapsed)} seconds"
                self.text(label, 23, MUTED, (500, 396), True)
                self.button("Play again", 445, "retry", True)
                self.button("Main menu", 509, "menu")
                self.text("R / SPACE to play again", 23, MUTED, (500, 621), True)
        if self.store.error:
            self.text(self.store.error, 20, RED, (500, 804), True)
        ww, wh = self.window.get_size()
        scale = min(ww / WIDTH, wh / HEIGHT)
        size = (max(1, int(WIDTH * scale)), max(1, int(HEIGHT * scale)))
        self.viewport = pygame.Rect((ww - size[0]) // 2, (wh - size[1]) // 2, *size)
        self.window.fill(BG)
        self.window.blit(pygame.transform.smoothscale(self.canvas, size), self.viewport)
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
    """Exercise real rendering, input, state transitions, audio, and resizing."""
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        app = App(Store(Path(directory) / "settings.json"))
        output.mkdir(parents=True, exist_ok=True)
        try:
            app.render()
            pygame.image.save(app.canvas, str(output / "menu.png"))
            app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
            assert app.state == "playing"
            app.game.food = (16, 11)
            app.update(.11)
            assert app.game.score == 10
            app.render()
            pygame.image.save(app.canvas, str(output / "playing.png"))
            app.event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
            assert app.state == "paused"
            head = app.game.snake[0]
            app.update(3)
            assert app.game.snake[0] == head
            app.render()
            pygame.image.save(app.canvas, str(output / "paused.png"))
            app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
            for _ in range(30):
                app.update(.15)
            assert app.state == "over"
            assert Store(app.store.path).best["Normal"] == 10
            app.render()
            pygame.image.save(app.canvas, str(output / "game-over.png"))
            app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
            assert app.state == "playing" and app.game.score == 0
            app.window = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
            app.render()
            assert app.viewport.width <= 640 and app.viewport.height <= 480
            app.event(pygame.event.Event(pygame.QUIT))
            assert not app.running
            print("PASS: menus, input, eating, pause, death, restart, persistence, resize, quit")
        finally:
            pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Classic Snake in Python and Pygame")
    parser.add_argument("--smoke-test", type=Path, metavar="SCREENSHOT_DIR")
    args = parser.parse_args()
    if args.smoke_test:
        smoke_test(args.smoke_test)
    else:
        App().run()


if __name__ == "__main__":
    main()

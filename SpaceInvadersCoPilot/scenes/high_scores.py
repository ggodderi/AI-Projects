import pygame

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, SMALL_FONT_SIZE, TITLE_FONT_SIZE
from systems.persistence import load_highscores


class HighScoresScene:
    def __init__(self, game) -> None:
        self.game = game
        self.title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
        self.font = pygame.font.SysFont(None, SMALL_FONT_SIZE + 4)
        self.scores = load_highscores()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                from scenes.menu import MenuScene
                self.game.set_scene(MenuScene(self.game))

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        title = self.title_font.render("High Scores", True, WHITE)
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

        if not self.scores:
            txt = self.font.render("No scores yet. Play a game!", True, WHITE)
            surface.blit(txt, (WINDOW_WIDTH // 2 - txt.get_width() // 2, 180))
            return

        y = 160
        for i, entry in enumerate(self.scores[:10], start=1):
            line = f"{i:2d}. {entry['initials']:<3}  {entry['score']:>6}"
            surf = self.font.render(line, True, WHITE)
            surface.blit(surf, (WINDOW_WIDTH // 2 - surf.get_width() // 2, y))
            y += 28

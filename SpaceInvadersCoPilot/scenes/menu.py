import pygame

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, GREEN, TITLE_FONT_SIZE, SMALL_FONT_SIZE
from scenes.gameplay import GameplayScene
from scenes.high_scores import HighScoresScene


class MenuScene:
    def __init__(self, game) -> None:
        self.game = game
        self.options = ["Start Game", "High Scores", "Quit"]
        self.index = 0
        self.title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
        self.menu_font = pygame.font.SysFont(None, SMALL_FONT_SIZE + 6)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.index = (self.index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate()

    def activate(self) -> None:
        option = self.options[self.index]
        if option == "Start Game":
            self.game.set_scene(GameplayScene(self.game))
        elif option == "High Scores":
            self.game.set_scene(HighScoresScene(self.game))
        elif option == "Quit":
            self.game.quit()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        title = self.title_font.render("Space Invaders", True, WHITE)
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 120))

        for i, text in enumerate(self.options):
            color = GREEN if i == self.index else WHITE
            surf = self.menu_font.render(text, True, color)
            x = WINDOW_WIDTH // 2 - surf.get_width() // 2
            y = 250 + i * 40
            surface.blit(surf, (x, y))

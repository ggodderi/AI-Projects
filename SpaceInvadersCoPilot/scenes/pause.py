import pygame

from settings import WHITE, SMALL_FONT_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, GREEN


class PauseScene:
    def __init__(self, game, gameplay_scene) -> None:
        self.game = game
        self.gameplay_scene = gameplay_scene
        self.font = pygame.font.SysFont(None, SMALL_FONT_SIZE + 8)
        self.options = ["Resume", "Quit to Menu"]
        self.index = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.index = (self.index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_p, pygame.K_ESCAPE):
                self.activate()

    def activate(self) -> None:
        option = self.options[self.index]
        if option == "Resume":
            self.game.set_scene(self.gameplay_scene)
        else:
            from scenes.menu import MenuScene
            self.game.set_scene(MenuScene(self.game))

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        for i, text in enumerate(self.options):
            color = GREEN if i == self.index else WHITE
            surf = self.font.render(text, True, color)
            x = WINDOW_WIDTH // 2 - surf.get_width() // 2
            y = WINDOW_HEIGHT // 2 - 20 + i * 40
            surface.blit(surf, (x, y))

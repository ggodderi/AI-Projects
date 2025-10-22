import sys
import pygame

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    TARGET_FPS,
    BLACK,
)
from systems.persistence import load_settings
from systems.audio import Audio

# Scene imports
from scenes.menu import MenuScene


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = Audio()
        self.settings = load_settings()

        self.scene = MenuScene(self)

    def set_scene(self, new_scene) -> None:
        self.scene = new_scene

    def quit(self) -> None:
        self.running = False

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.screen.fill(BLACK)
            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Game().run()

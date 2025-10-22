import pygame

from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, SMALL_FONT_SIZE, TITLE_FONT_SIZE, GREEN
from systems.persistence import submit_highscore, load_highscores


class GameOverScene:
    def __init__(self, game, score: int) -> None:
        self.game = game
        self.score = score
        self.title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
        self.font = pygame.font.SysFont(None, SMALL_FONT_SIZE + 4)

        # Simple high score check
        scores = load_highscores()
        if len(scores) < 10 or (scores and score > scores[-1]["score"]):
            self.need_initials = True
        else:
            self.need_initials = False
        self.initials = ""

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if self.need_initials:
                if event.key == pygame.K_BACKSPACE:
                    self.initials = self.initials[:-1]
                elif event.key == pygame.K_RETURN:
                    self.submit()
                else:
                    ch = event.unicode.upper()
                    if ch.isalpha() and len(self.initials) < 3:
                        self.initials += ch
            else:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    from scenes.menu import MenuScene
                    self.game.set_scene(MenuScene(self.game))

    def submit(self) -> None:
        if not self.initials:
            return
        submit_highscore(self.initials, self.score)
        from scenes.high_scores import HighScoresScene
        self.game.set_scene(HighScoresScene(self.game))

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        title = self.title_font.render("Game Over", True, WHITE)
        surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

        score_txt = self.font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_txt, (WINDOW_WIDTH // 2 - score_txt.get_width() // 2, 180))

        if self.need_initials:
            prompt = self.font.render("New High Score! Enter initials:", True, GREEN)
            surface.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 240))
            initials = self.title_font.render(self.initials or "_", True, WHITE)
            surface.blit(initials, (WINDOW_WIDTH // 2 - initials.get_width() // 2, 290))
        else:
            txt = self.font.render("Press Enter to return to menu", True, WHITE)
            surface.blit(txt, (WINDOW_WIDTH // 2 - txt.get_width() // 2, 260))

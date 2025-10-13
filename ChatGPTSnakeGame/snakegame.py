import sys
import random
import pygame

# -----------------------------
# Config
# -----------------------------
CELL_SIZE = 20
GRID_W, GRID_H = 32, 24           # 32*20 by 24*20 = 640x480 window
SCREEN_W, SCREEN_H = GRID_W*CELL_SIZE, GRID_H*CELL_SIZE
FPS = 12                           # movement speed; tweak for difficulty

BG_COLOR = (15, 18, 22)
SNAKE_COLOR = (70, 220, 120)
SNAKE_HEAD_COLOR = (90, 245, 150)
FOOD_COLOR = (240, 90, 90)
GRID_COLOR = (30, 34, 40)
TEXT_COLOR = (230, 230, 230)
SHADOW = (0, 0, 0)

# Directions as (dx, dy) in grid coords
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

def draw_cell(surf, x, y, color):
    r = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surf, color, r, border_radius=5)

def random_empty_cell(snake_body):
    taken = set(snake_body)
    while True:
        p = (random.randrange(0, GRID_W), random.randrange(0, GRID_H))
        if p not in taken:
            return p

def draw_grid(surf):
    # subtle grid for aesthetics
    for x in range(GRID_W):
        pygame.draw.line(surf, GRID_COLOR, (x*CELL_SIZE, 0), (x*CELL_SIZE, SCREEN_H))
    for y in range(GRID_H):
        pygame.draw.line(surf, GRID_COLOR, (0, y*CELL_SIZE), (SCREEN_W, y*CELL_SIZE))

def render_text(surf, font, txt, pos, color=TEXT_COLOR, shadow=True, center=False):
    t = font.render(txt, True, color)
    rect = t.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    if shadow:
        s = font.render(txt, True, SHADOW)
        srect = s.get_rect(center=rect.center)
        srect.x += 2; srect.y += 2
        surf.blit(s, srect)
    surf.blit(t, rect)

def main():
    pygame.init()
    pygame.display.set_caption("Snake – Pygame")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas,menlo,monaco,dejavusansmono", 22)
    bigfont = pygame.font.SysFont("consolas,menlo,monaco,dejavusansmono", 36)

    def reset():
        start = (GRID_W // 2, GRID_H // 2)
        snake = [start, (start[0]-1, start[1]), (start[0]-2, start[1])]
        direction = RIGHT
        food = random_empty_cell(snake)
        score = 0
        alive = True
        return snake, direction, food, score, alive

    snake, direction, food, score, alive = reset()
    pending_dir = direction  # buffer to avoid instant 180° turns within one frame

    while True:
        # ------------- Input -------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    pygame.quit(); sys.exit()
                if alive:
                    if event.key in (pygame.K_UP, pygame.K_w) and direction != DOWN:
                        pending_dir = UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != UP:
                        pending_dir = DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != RIGHT:
                        pending_dir = LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != LEFT:
                        pending_dir = RIGHT
                else:
                    if event.key in (pygame.K_r,):
                        snake, direction, food, score, alive = reset()
                        pending_dir = direction

        # ------------- Update -------------
        if alive:
            direction = pending_dir
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # wall collision = game over
            if not (0 <= new_head[0] < GRID_W and 0 <= new_head[1] < GRID_H):
                alive = False
            # self collision
            elif new_head in snake:
                alive = False
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    food = random_empty_cell(snake)
                else:
                    snake.pop()

        # ------------- Draw -------------
        screen.fill(BG_COLOR)
        draw_grid(screen)
        # draw food
        draw_cell(screen, food[0], food[1], FOOD_COLOR)
        # draw snake
        for i, (x, y) in enumerate(snake):
            c = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            draw_cell(screen, x, y, c)

        # UI
        render_text(screen, font, f"Score: {score}", (10, 8))
        render_text(screen, font, "R to Restart  •  Esc to Quit", (10, 34), color=(180, 180, 180))

        if not alive:
            render_text(screen, bigfont, "Game Over", (SCREEN_W//2, SCREEN_H//2 - 30), center=True)
            render_text(screen, font, "Press R to play again", (SCREEN_W//2, SCREEN_H//2 + 10), color=(200, 200, 200), center=True)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

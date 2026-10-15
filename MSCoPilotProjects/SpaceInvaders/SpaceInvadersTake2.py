import pygame
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Player setup
player_img = pygame.Surface((50, 30))
player_img.fill(WHITE)
player_x = WIDTH // 2
player_y = HEIGHT - 60
player_speed = 5

# Bullet setup
bullet_img = pygame.Surface((5, 10))
bullet_img.fill(WHITE)
bullets = []

# Enemy setup
enemy_img = pygame.Surface((40, 30))
enemy_img.fill((255, 0, 0))
enemy_speed = 2

# Wave system
wave = 1
enemy_count = 6

def spawn_enemies(count):
    new_enemies = []
    for _ in range(count):
        x = random.randint(0, WIDTH - 40)
        y = random.randint(50, 150)
        new_enemies.append([x, y])
    return new_enemies

enemies = spawn_enemies(enemy_count)

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - 50:
        player_x += player_speed
    if keys[pygame.K_SPACE]:
        bullets.append([player_x + 22, player_y])

    # Move bullets
    for bullet in bullets[:]:
        bullet[1] -= 7
        if bullet[1] < 0:
            bullets.remove(bullet)

    # Move enemies
    for enemy in enemies:
        enemy[1] += enemy_speed
        if enemy[1] > HEIGHT:
            enemy[1] = random.randint(50, 150)
            enemy[0] = random.randint(0, WIDTH - 40)

    # Collision detection
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if (enemy[0] < bullet[0] < enemy[0] + 40) and (enemy[1] < bullet[1] < enemy[1] + 30):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                break

    # Check for wave completion
    if not enemies:
        wave += 1
        enemy_count += 2
        enemy_speed += 0.5
        enemies = spawn_enemies(enemy_count)

    # Draw player
    screen.blit(player_img, (player_x, player_y))

    # Draw bullets
    for bullet in bullets:
        screen.blit(bullet_img, (bullet[0], bullet[1]))

    # Draw enemies
    for enemy in enemies:
        screen.blit(enemy_img, (enemy[0], enemy[1]))

    # Draw score and wave
    score_text = font.render(f"Score: {score}", True, WHITE)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(wave_text, (10, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
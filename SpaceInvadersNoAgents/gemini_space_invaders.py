import pygame
import random
import math
import sys

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Spider Invaders"
FPS = 60

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255) # Shooter/HUD color
PURPLE = (128, 0, 128) # Invader color
ORANGE = (255, 165, 0) # Bomb color

# --- Initialization ---
pygame.init()
pygame.mixer.init()
pygame.display.set_caption(TITLE)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Sound Setup ---
# NOTE: For sounds to work, you must have 'shoot.wav' and 'hit.wav' files
# in the same directory as this script.
try:
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    hit_sound = pygame.mixer.Sound("hit.wav")
except pygame.error as e:
    print(f"Warning: Could not load sound files (shoot.wav or hit.wav). Game will run without sound. Error: {e}")
    # Create silent placeholders if files are missing
    shoot_sound = pygame.mixer.Sound(b'\x00\x00\x00\x00')
    hit_sound = pygame.mixer.Sound(b'\x00\x00\x00\x00')


# --- Utility Functions ---

def draw_text(surf, text, size, x, y, color=WHITE):
    """Draws text onto a surface."""
    font_size = pygame.font.Font(None, size)
    text_surface = font_size.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)

def draw_spider_invader(surf, rect):
    """Draws a stylized spider invader."""
    # Body (Purple circle)
    pygame.draw.circle(surf, PURPLE, rect.center, rect.width // 3)
    # Legs (simple lines)
    for i in range(4):
        # Draw 4 pairs of simple legs extending from the body
        angle = math.pi / 4 + i * (math.pi / 2)
        leg_dx = math.cos(angle) * rect.width // 2
        leg_dy = math.sin(angle) * rect.width // 2
        
        # Left side
        pygame.draw.line(surf, PURPLE, rect.center, 
                         (rect.centerx - leg_dx, rect.centery + leg_dy), 2)
        # Right side
        pygame.draw.line(surf, PURPLE, rect.center, 
                         (rect.centerx + leg_dx, rect.centery + leg_dy), 2)


# --- Game Classes ---

class Shooter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 40  # Constraint 21: Shooter width <= Invader width (Invader width is 40)
        self.height = 30
        self.image = pygame.Surface([self.width, self.height])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 30
        self.speed = 5
        self.hidden = False

    def draw_tank(self, surf):
        """Draws a simple tank shape."""
        # Base (main body)
        base_rect = pygame.Rect(self.rect.left, self.rect.top + 10, self.width, self.height - 10)
        pygame.draw.rect(surf, CYAN, base_rect, border_radius=5)
        
        # Turret (top)
        turret_rect = pygame.Rect(self.rect.centerx - 8, self.rect.top, 16, 12)
        pygame.draw.rect(surf, CYAN, turret_rect, border_radius=3)
        
        # Cannon (line)
        pygame.draw.line(surf, CYAN, self.rect.center, (self.rect.centerx, self.rect.top), 3)

    def update(self):
        if self.hidden:
            return

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Keep within bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def hide(self):
        """Hides the shooter upon game over."""
        self.hidden = True
        self.rect.center = (-100, -100) # Move off-screen

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([4, 10])
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10 # Moves up

    def update(self):
        self.rect.y += self.speed
        # Kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([8, 8])
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 3 # Moves down

    def update(self):
        self.rect.y += self.speed
        # Kill if it moves off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Invader(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 40
        self.image = pygame.Surface([self.width, self.height])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.drop_rate = 0 # Base bomb drop chance (modified by GameController)
        self.move_counter = 0

    def update(self, direction, speed_modifier):
        """Updates invader position based on direction and speed modifier."""
        self.move_counter += 1
        
        # Calculate speed with modifier (faster when fewer invaders are left)
        current_speed = int(2 * speed_modifier) 
        
        # Move only when counter reaches speed (creates the classic step-wise movement)
        if self.move_counter >= max(1, 20 - current_speed):
            self.rect.x += direction * 10
            self.move_counter = 0

    def draw(self, surf):
        """Custom draw method to display the spider."""
        draw_spider_invader(surf, self.rect)

    def move_down(self):
        """Moves the invader one row down."""
        self.rect.y += 30

class GameController:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.invaders = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.invader_bombs = pygame.sprite.Group()
        self.shooter = Shooter()
        self.all_sprites.add(self.shooter)

        self.game_state = "MENU"
        self.score = 0
        self.level = 0
        self.max_levels = 12

        self.invader_direction = 1 # 1 for right, -1 for left
        self.invader_move_delay = 50 # Lower is faster
        self.invader_move_timer = 0
        self.invader_drop_chance = 0.005 # Base chance for a bomb to drop per frame

        self.max_active_bullets = 5 # Constraint 8
        self.bullets_remaining = 0 # Constraint 15
        self.max_bullets_per_level = 170
        self.can_shoot = True

    def start_new_game(self):
        """Initializes game state for a new game."""
        self.game_state = "PLAYING"
        self.score = 0
        self.level = 0
        self.bullets_remaining = self.max_bullets_per_level
        self.shooter = Shooter()
        self.all_sprites.empty()
        self.player_bullets.empty()
        self.invader_bombs.empty()
        self.all_sprites.add(self.shooter)
        self.start_new_level()

    def start_new_level(self):
        """Sets up the next level of invaders."""
        if self.level >= self.max_levels:
            self.game_state = "WIN"
            return

        self.level += 1
        
        # Reset movement for new level
        self.invader_direction = 1
        self.bullets_remaining = self.max_bullets_per_level
        self.can_shoot = True
        self.invaders.empty()
        self.player_bullets.empty()
        self.invader_bombs.empty()

        # Level difficulty scaling: more invaders, faster movement
        base_cols = 6
        base_rows = 3
        # Increase invaders by 1 column and 1 row every 3 levels
        cols = min(10, base_cols + (self.level - 1) // 3)
        rows = min(6, base_rows + (self.level - 1) // 3)

        # Invader spacing and offset
        invader_gap = 50
        start_x = (SCREEN_WIDTH - cols * invader_gap) // 2
        start_y = 50

        # Faster initial movement (lower move delay is faster)
        self.invader_move_delay = max(5, 50 - (self.level * 3))

        # Create invaders
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * invader_gap
                y = start_y + row * invader_gap
                invader = Invader(x, y)
                self.invaders.add(invader)
                self.all_sprites.add(invader)

    def handle_input(self):
        """Handles user input for movement and shooting."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = "QUIT"
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "PLAYING":
                    if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and self.can_shoot:
                        self.shoot()
                elif self.game_state == "GAME_OVER" or self.game_state == "WIN":
                    if event.key == pygame.K_RETURN:
                        self.start_new_game()
                elif self.game_state == "MENU":
                    if event.key == pygame.K_RETURN:
                        self.start_new_game()
            
    def shoot(self):
        """Creates a player bullet, respecting limits."""
        if len(self.player_bullets) < self.max_active_bullets and self.bullets_remaining > 0:
            bullet = Bullet(self.shooter.rect.centerx, self.shooter.rect.top)
            self.all_sprites.add(bullet)
            self.player_bullets.add(bullet)
            shoot_sound.play()
            self.bullets_remaining -= 1
            if self.bullets_remaining <= 0:
                self.can_shoot = False

    def check_collisions(self):
        """Handles all game object collisions."""
        # 1. Player Bullet vs Invader (Constraint 4)
        hits = pygame.sprite.groupcollide(self.invaders, self.player_bullets, True, True)
        for invader in hits:
            self.score += 10
            hit_sound.play()
            # If an invader is hit, the bullet is automatically killed (removed from group)
            # by the `pygame.sprite.groupcollide` using the `dokill` flag `True` for bullets.

        # 2. Player Bullet vs Invader Bomb (Constraint 20)
        bomb_hits = pygame.sprite.groupcollide(self.invader_bombs, self.player_bullets, True, True)
        if bomb_hits:
            hit_sound.play() # Use hit sound for bomb explosion

        # 3. Invader vs Shooter (Constraint 5)
        # Invaders hitting the shooter
        if pygame.sprite.spritecollide(self.shooter, self.invaders, False):
            self.game_over()
        
        # 4. Invader vs Ground (Constraint 5)
        for invader in self.invaders:
            if invader.rect.bottom >= SCREEN_HEIGHT - 30: # 30 is ground level/shooter Y
                self.game_over()
                break

        # 5. Invader Bomb vs Shooter (Constraint 19)
        if pygame.sprite.spritecollide(self.shooter, self.invader_bombs, True):
            self.game_over()

    def update_invaders(self):
        """Moves invaders and handles level-clear, speed-up (Constraint 13)."""
        if not self.invaders:
            self.start_new_level()
            return
        
        # Speed modifier based on remaining invaders (Constraint 13)
        # Fewer invaders = higher modifier = faster step-wise movement
        initial_count = self.level * 18 # approximation of initial count
        current_count = len(self.invaders)
        # The modifier ranges from 1.0 (full health) to approx 2.0 (few left)
        speed_modifier = 1 + (1 - (current_count / initial_count)) 
        speed_modifier = max(1.0, speed_modifier)

        self.invader_move_timer += 1
        
        # Check if it's time for the invaders to move
        if self.invader_move_timer >= self.invader_move_delay:
            self.invader_move_timer = 0
            
            should_drop = False
            # Check for edge collision first
            for invader in self.invaders:
                if invader.rect.right >= SCREEN_WIDTH - 10 and self.invader_direction == 1:
                    should_drop = True
                    self.invader_direction = -1
                    break
                elif invader.rect.left <= 10 and self.invader_direction == -1:
                    should_drop = True
                    self.invader_direction = 1
                    break
            
            # Apply movement/drop
            for invader in self.invaders:
                if should_drop:
                    invader.move_down()
                invader.update(self.invader_direction, speed_modifier)

        # Bomb drop logic (Constraint 19)
        if random.random() < self.invader_drop_chance * len(self.invaders):
            try:
                # Randomly select a living invader to drop a bomb
                bomber = random.choice(list(self.invaders))
                bomb = Bomb(bomber.rect.centerx, bomber.rect.bottom)
                self.invader_bombs.add(bomb)
                self.all_sprites.add(bomb)
            except IndexError:
                # No invaders left, ignore bomb drop attempt
                pass


    def game_over(self):
        """Triggers Game Over state (Constraint 10)."""
        self.game_state = "GAME_OVER"
        self.shooter.hide()
        self.invaders.empty()
        self.invader_bombs.empty()
        self.player_bullets.empty()

    def show_menu(self):
        """Displays the start menu."""
        screen.fill(BLACK)
        draw_text(screen, TITLE, 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, CYAN)
        draw_text(screen, "Press ENTER to Start", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "Move: A/Left Arrow | Shoot: Space/Up Arrow", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        pygame.display.flip()

    def show_game_over_screen(self):
        """Displays the game over screen (Constraint 10, 11)."""
        screen.fill(BLACK)
        draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, RED)
        draw_text(screen, f"Final Score: {self.score}", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        draw_text(screen, "Press ENTER to Play Again", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3, GREEN)
        pygame.display.flip()
        
    def show_win_screen(self):
        """Displays the victory screen after 12 levels (Constraint 12)."""
        screen.fill(BLACK)
        draw_text(screen, "VICTORY!", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, GREEN)
        draw_text(screen, "You cleared all 12 levels!", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        draw_text(screen, f"Final Score: {self.score}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 + 40, WHITE)
        draw_text(screen, "Press ENTER to Play Again", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4, GREEN)
        pygame.display.flip()

    def run_game_loop(self):
        """Main game loop."""
        while self.game_state != "QUIT":
            self.handle_input()
            
            if self.game_state == "MENU":
                self.show_menu()
                continue
            
            if self.game_state == "GAME_OVER":
                self.show_game_over_screen()
                continue
                
            if self.game_state == "WIN":
                self.show_win_screen()
                continue

            # --- Update Phase (Game State == PLAYING) ---
            self.all_sprites.update()
            self.update_invaders()
            self.check_collisions()

            # --- Drawing Phase ---
            screen.fill(BLACK)

            # Draw Ground Line (Shooter's Level)
            pygame.draw.line(screen, GREEN, (0, SCREEN_HEIGHT - 60), (SCREEN_WIDTH, SCREEN_HEIGHT - 60), 2)
            
            # Draw Shooter (using custom drawing)
            if not self.shooter.hidden:
                 self.shooter.draw_tank(screen)
            
            # Draw Invaders (using custom drawing)
            for invader in self.invaders:
                invader.draw(screen)

            # Draw other sprites (bullets, bombs)
            for sprite in self.all_sprites:
                if isinstance(sprite, Bullet) or isinstance(sprite, Bomb):
                    screen.blit(sprite.image, sprite.rect)

            # Draw HUD (Score and Bullet Count - Constraints 9, 16)
            draw_text(screen, f"SCORE: {self.score}", 30, 80, 20, CYAN)
            draw_text(screen, f"LEVEL: {self.level}/{self.max_levels}", 30, SCREEN_WIDTH // 2, 20, CYAN)
            draw_text(screen, f"BULLETS: {self.bullets_remaining}", 30, SCREEN_WIDTH - 120, 20, CYAN)
            if not self.can_shoot:
                 draw_text(screen, "NO AMMO!", 30, SCREEN_WIDTH - 120, 50, RED)

            pygame.display.flip()

            # Maintain frame rate
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameController()
    game.run_game_loop()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Gameplay
STARTING_LIVES = 3
EXTRA_LIFE_SCORE = 1500
MAX_PLAYER_BULLETS = 5

# Invaders
INVADER_ROWS = 5
INVADER_COLS = 11
INVADER_POINTS_TOP = 30
INVADER_POINTS_MIDDLE = 20
INVADER_POINTS_BOTTOM = 10
INVADER_STEP_DOWN_AMOUNT = 20
INVADER_HORIZONTAL_SPEED = 50.0  # pixels per second
INVADER_BASE_STEP_INTERVAL = 0.6  # seconds between steps

# Bombs (Invader Projectiles)
BOMB_SPEED = 150.0  # pixels per second downward
BOMB_SPAWN_INTERVAL_BASE = 2.0  # seconds between bomb spawn attempts
BOMB_MAX_COUNT_BASE = 2  # base max active bombs
BOMB_MAX_COUNT_PER_WAVE = 1  # additional bombs per wave

# Bunkers (Shields)
BUNKER_COUNT = 4
BUNKER_WIDTH = 80
BUNKER_HEIGHT = 60
BUNKER_DAMAGE_RADIUS = 8  # radius of damage when hit

# Controls (pygame key constants names; resolved at runtime)
KEY_BINDINGS = {
	"move_left": "K_LEFT",
	"move_right": "K_RIGHT",
	"fire": "K_SPACE",
	"pause": "K_p",
	"back": "K_ESCAPE",
}

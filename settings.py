"""
settings.py
קובץ של הגדרות קבועות + ציור רקע ואדמה.
"""

# גודל חלון
WIDTH, HEIGHT = 1000, 600

# FPS = כמה פעמים בשניה מעדכנים את המשחק
FPS = 60

# גובה האדמה
GROUND_Y = HEIGHT - 80

# צבעים
BG_TOP = (20, 20, 50)         # צבע שמיים למעלה
BG_BOTTOM = (20, 100, 40)     # צבע למטה (גרדיאנט)
GROUND_COLOR = (70, 50, 30)

PLAYER_COLOR = (80, 160, 255)
ENEMY_COLOR = (255, 120, 120)

PLAYER_BASE_COLOR = (40, 80, 160)
ENEMY_BASE_COLOR = (160, 60, 60)

HP_BAR_BG = (40, 40, 40)
HP_GOOD = (60, 220, 60)
HP_MED = (230, 200, 40)
HP_BAD = (220, 60, 60)

TEXT_COLOR = (240, 240, 240)


# =========================
# Tunable gameplay constants
# כל הערכים האלו ניתנים לשינוי כאן כדי להתאים את המשחק
# =========================

# Base (player / enemy)
PLAYER_BASE_MAX_HP = 1000
ENEMY_BASE_MAX_HP = 1000
PLAYER_BASE_WIDTH = 150
ENEMY_BASE_WIDTH = 150
BASE_HIT_FLASH_DURATION = 220

# Unit (soldier)
UNIT_WIDTH = 26
UNIT_HEIGHT = 40
UNIT_MAX_HP = 100
UNIT_SPEED = 90.0  # pixels per second
UNIT_ATTACK_RANGE = 40
UNIT_ATTACK_DAMAGE = 12
UNIT_ATTACK_COOLDOWN = 600  # milliseconds
UNIT_ATTACK_ANIM_DURATION = 160  # ms for attack animation
UNIT_HIT_FLASH_DURATION = 160
UNIT_RECOIL_AMOUNT = 6

# Economy / spawn
UNIT_COST = 35
MONEY_PER_SECOND = 8
XP_PER_SECOND = 2
MONEY_MAX = 9999
XP_MAX = 99999
ENEMY_SPAWN_INTERVAL = 3000  # ms between enemy spawns

# Base turret (levels)
BASE_TURRET_MAX_LEVEL = 3
BASE_TURRET_XP_COSTS = [0, 50, 120, 250]
BASE_TURRET_RANGES = [0, 200, 250, 300]
BASE_TURRET_DAMAGES = [0, 10, 16, 24]
BASE_TURRET_COOLDOWNS = [0, 900, 650, 450]

# Screen / effects defaults
DEFAULT_SCREEN_SHAKE_DURATION = 300
DEFAULT_SCREEN_SHAKE_MAGNITUDE = 10


# Note: rendering helpers and fonts were moved to visuals.py

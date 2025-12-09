import pygame
from settings import WIDTH, HEIGHT, GROUND_Y, BG_TOP, BG_BOTTOM, GROUND_COLOR


# Fonts (create after pygame.init() is called in main)
font = None


def ensure_fonts():
    """Ensure font objects are created after pygame.init()."""
    global font
    if font is None:
        try:
            font = pygame.font.SysFont("arial", 20)
        except Exception:
            # fallback: pygame not initialized yet
            font = None


def draw_gradient_background(surface):
    """Draw vertical gradient background (moved from settings)."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_ground(surface):
    """Draw ground rectangle at the bottom (moved from settings)."""
    pygame.draw.rect(surface, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

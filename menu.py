import pygame
from settings import WIDTH, HEIGHT, TEXT_COLOR
from visuals import draw_gradient_background, draw_ground


class Menu:
    def __init__(self, options, title="Mini Age of War"):
        self.options = options
        self.title = title
        self.selected = 0
        self.title_font = pygame.font.SysFont("arial", 56)
        self.opt_font = pygame.font.SysFont("arial", 28)

    def draw(self, surface):
        draw_gradient_background(surface)
        draw_ground(surface)

        # Title
        title_surf = self.title_font.render(self.title, True, (250, 220, 120))
        surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 140))

        # Options
        start_y = HEIGHT // 2 - 20
        gap = 48
        for i, opt in enumerate(self.options):
            color = (240, 240, 100) if i == self.selected else TEXT_COLOR
            opt_surf = self.opt_font.render(opt, True, color)
            x = WIDTH // 2 - opt_surf.get_width() // 2
            y = start_y + i * gap
            surface.blit(opt_surf, (x, y))

    def handle_key(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return self.options[self.selected]
        return None

    def handle_mouse(self, pos):
        start_y = HEIGHT // 2 - 20
        gap = 48
        for i, opt in enumerate(self.options):
            opt_surf = self.opt_font.render(opt, True, TEXT_COLOR)
            x = WIDTH // 2 - opt_surf.get_width() // 2
            y = start_y + i * gap
            rect = pygame.Rect(x, y, opt_surf.get_width(), opt_surf.get_height())
            if rect.collidepoint(pos):
                self.selected = i
                return opt
        return None


def draw_game_over_menu(surface, message):
    # פשוט overlay שמבקש לחזור לתפריט או לצאת
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    big = pygame.font.SysFont("arial", 48).render(message, True, (255, 255, 255))
    small = pygame.font.SysFont("arial", 22).render("Enter - Back to Menu    R - Restart    Q or ESC - Quit", True, (230, 230, 230))

    surface.blit(big, (WIDTH // 2 - big.get_width() // 2, HEIGHT // 2 - 40))
    surface.blit(small, (WIDTH // 2 - small.get_width() // 2, HEIGHT // 2 + 20))

import sys
import pygame
from settings import WIDTH, HEIGHT, FPS, draw_gradient_background, draw_ground, font, TEXT_COLOR
from game import Game
from music import start_music

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


def main():
    pygame.init()

    # נסיון להפעיל מוזיקה (אם יש בעיה נמשיך בלי)
    try:
        start_music()
    except Exception:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini Age of War - Pygame (OOP)")
    clock = pygame.time.Clock()

    game = Game()

    # menu instance
    menu = Menu(["Start Game", "Quit"])

    state = "menu"  # 'menu' or 'playing'
    running = True

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "menu":
                if event.type == pygame.KEYDOWN:
                    res = menu.handle_key(event.key)
                    if res == "Start Game":
                        game.reset()
                        state = "playing"
                    elif res == "Quit":
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    res = menu.handle_mouse(event.pos)
                    if res == "Start Game":
                        game.reset()
                        state = "playing"
                    elif res == "Quit":
                        running = False
            elif state == "playing":
                if event.type == pygame.KEYDOWN:
                    if not game.game_over:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        if event.key == pygame.K_SPACE:
                            game.spawn_player_unit()
                        if event.key == pygame.K_1:
                            game.upgrade_base_turret()
                        # R: reset while playing
                        if event.key == pygame.K_r:
                            game.reset()
                            state = "playing"
                    else:
                        # when game over, allow returning to menu, restarting or quitting
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            state = "menu"
                        elif event.key == pygame.K_r:
                            game.reset()
                            state = "playing"
                        elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                            running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game.game_over:
                    # click anywhere after game over -> return to menu (optional)
                    state = "menu"

        # draw/update per state
        if state == "menu":
            menu.draw(screen)
        elif state == "playing":
            if not game.game_over:
                game.update(dt)
            # draw the game (Game.draw already shows the overlay + message when game_over)
            game.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
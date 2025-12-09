import sys
import pygame
from settings import WIDTH, HEIGHT, FPS, TEXT_COLOR
from visuals import draw_gradient_background, draw_ground, ensure_fonts
from game import Game
from music import play_background_music

from menu import Menu, draw_game_over_menu


def main():
    pygame.init()
    # ensure visuals fonts are created after pygame.init()
    ensure_fonts()

    # נסיון להפעיל מוזיקה (אם יש בעיה נמשיך בלי)
    try:
        play_background_music()
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

import sys
import pygame
from constants import *
from menu import Menu
from game import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Fonts
    font_big   = pygame.font.SysFont('monospace', 72, bold=True)
    font_med   = pygame.font.SysFont('monospace', 42, bold=True)
    font_small = pygame.font.SysFont('monospace', 22, bold=True)
    fonts = (font_big, font_med, font_small)

    scene = 'MENU'
    menu = Menu(screen, fonts)
    game = None

    round_end_timer = 0

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if scene == 'GAME':
                    scene = 'MENU'
                    menu = Menu(screen, fonts)
                    game = None
                else:
                    pygame.quit()
                    sys.exit()

            if scene == 'MENU':
                menu.handle_event(event)

            elif scene == 'GAME' and game is not None:
                if event.type == pygame.KEYDOWN:
                    if game.match_state == 'GAME_OVER':
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            game = Game(game.mode, game.difficulty, screen, fonts)
                        elif event.key == pygame.K_ESCAPE:
                            scene = 'MENU'
                            menu = Menu(screen, fonts)
                            game = None

        # Scene logic
        if scene == 'MENU':
            if menu.result:
                mode, difficulty = menu.result
                game = Game(mode, difficulty, screen, fonts)
                scene = 'GAME'
            menu.draw()

        elif scene == 'GAME' and game is not None:
            if game.match_state == 'ROUND_END' and game.result is None:
                round_end_timer += 1
                if round_end_timer >= 180:
                    game.next_round()
                    round_end_timer = 0
            else:
                round_end_timer = 0

            if game.match_state == 'FIGHTING':
                game.update(keys)

            game.draw()

        pygame.display.flip()


if __name__ == '__main__':
    main()

import pygame
from styles import draw_background, getProp, colors
from game_elements import Gameboard
from effects import Score, Shooter, initialize_window

if __name__ == "__main__":
    window, clock = initialize_window(getProp('window-width'), getProp('window-height'), "Bubble Buster")

    gameboard = Gameboard( 1 ) # level 1
    running = True
    first_text = Score(20)
    shooter = Shooter()
    shooter.set_bubble(gameboard.bubbles_queue.pop(0))

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shooter.update_angle(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                gameboard.use_shooter(shooter, window, first_text)
                shooter = Shooter()
                shooter.set_bubble(gameboard.bubbles_queue.pop(0))

        shooter.update_angle(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        draw_background(window)
        gameboard.draw(window)
        first_text.draw(window)
        shooter.draw(window)

        pygame.display.flip()
        clock.tick(getProp('FPS'))

    pygame.quit()

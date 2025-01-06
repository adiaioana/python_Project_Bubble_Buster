import pygame

from scenes import beginning_screen, show_instructions, level_complete_screen, draw_next_bubble, game_over_screen
from styles import draw_background, getProp
from game_elements import Gameboard
from effects import Score, Shooter, initialize_window

def end_game(window, clock):
    """Handles the game over logic and asks the user whether to quit or restart."""
    game_result = game_over_screen(window, clock)
    if game_result == 'restart':
        return True  # Return True to restart the game
    else:
        return False  # Return False to quit the game

def init_game():
    current_level = 1
    gameboard = Gameboard(current_level)
    first_text = Score(20)
    shooter = Shooter()
    shooter.set_bubble(gameboard.bubbles_queue.pop(0))
    next_bubble = gameboard.bubbles_queue[0]
    return current_level, gameboard, shooter, next_bubble, first_text

if __name__ == "__main__":
    window, clock = initialize_window(getProp('window-width'), getProp('window-height'), "Bubble Buster")

    current_level, gameboard, shooter, next_bubble, first_text = init_game()
    running = True

    # Intro screens
    beginning_screen(window, clock)
    show_instructions(window, clock)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    running = True
                    current_level, gameboard, shooter, next_bubble, first_text = init_game()
                elif event.key == pygame.K_q:
                    running = end_game(window, clock)
                    if running:
                        current_level, gameboard, shooter, next_bubble, first_text = init_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shooter.update_angle(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                # Check if the bubble went below the gameboard
                if not gameboard.use_shooter(shooter, window, first_text):
                    running = end_game(window, clock)  # End the game if the bubble went below
                    if running:
                        current_level, gameboard, shooter, next_bubble, first_text = init_game()

                # Update the shooter bubble and next bubble
                if gameboard.bubbles_queue:
                    shooter = Shooter()
                    shooter.set_bubble(gameboard.bubbles_queue.pop(0))
                    next_bubble = gameboard.bubbles_queue[0] if gameboard.bubbles_queue else None

                # Check for level completion
                if gameboard.is_empty():
                    level_complete_screen(window, clock)
                    current_level += 1
                    gameboard = Gameboard(current_level)
                    shooter = Shooter()
                    shooter.set_bubble(gameboard.bubbles_queue.pop(0))
                    next_bubble = gameboard.bubbles_queue[0]

        shooter.update_angle(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        draw_background(window)
        gameboard.draw(window)
        first_text.draw(window)
        shooter.draw(window)

        if next_bubble:
            draw_next_bubble(window, next_bubble)

        pygame.display.flip()
        clock.tick(getProp('FPS'))

    pygame.quit()

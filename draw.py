import pygame

# Importing custom modules for various game components and utilities
from scenes import beginning_screen, show_instructions, level_complete_screen, draw_next_bubble, game_over_screen
from styles import draw_background, getProp
from game_elements import Gameboard
from effects import Score, Shooter, initialize_window


def end_game(the_window, the_clock):
    """Handles the game over logic and asks the user whether to quit or restart."""
    game_result = game_over_screen(the_window, the_clock)  # Show the game over screen and get the player's choice
    if game_result == 'restart':
        return True  # Return True to restart the game
    else:
        return False  # Return False to quit the game


def init_game():
    """Initializes the game state for a new game or level."""
    the_current_level = 1  # Starting with level 1
    the_gameboard = Gameboard(the_current_level)  # Create the gameboard for the current level
    the_first_text = Score(20)  # Create the score object to track and display the score
    the_shooter = Shooter()  # Create the shooter object
    the_shooter.set_bubble(the_gameboard.bubbles_queue.pop(0))  # Assign the first bubble from the queue to the shooter
    the_next_bubble = the_gameboard.bubbles_queue[0]  # Peek at the next bubble in the queue
    return the_current_level, the_gameboard, the_shooter, the_next_bubble, the_first_text


if __name__ == "__main__":
    # Initialize the game window and clock with dimensions and title
    window, clock = initialize_window(getProp('window-width'), getProp('window-height'), "Bubble Buster")

    # Initialize game state variables
    current_level, gameboard, shooter, next_bubble, first_text = init_game()
    running = True  # Game running state
    no_iter = 0
    # Display the introduction screens
    beginning_screen(window, clock)  # Show the beginning screen
    show_instructions(window, clock)  # Show the instructions screen

    # Main game loop
    while running:
        no_iter += 1


        for event in pygame.event.get():  # Process all events in the event queue
            if event.type == pygame.QUIT:  # Handle window close event
                running = False
                no_iter = 0
            elif event.type == pygame.KEYDOWN:  # Handle key press events

                if event.key == pygame.K_r:  # Restart the game on pressing 'R'
                    running = True
                    no_iter = 0
                    current_level, gameboard, shooter, next_bubble, first_text = init_game()
                elif event.key == pygame.K_q:  # Quit or restart on pressing 'Q'
                    running = end_game(window, clock)  # Determine if the player wants to quit or restart
                    if running:  # If restarting, reinitialize the game state
                        no_iter = 0
                        current_level, gameboard, shooter, next_bubble, first_text = init_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Handle left mouse button click
                # Update the shooter's angle based on the mouse position
                shooter.update_angle(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                # Use the shooter to fire a bubble and check if it went below the gameboard
                if not gameboard.use_shooter(shooter, window, first_text):
                    running = end_game(window, clock)  # End the game if the bubble goes below
                    if running:  # If restarting, reinitialize the game state
                        current_level, gameboard, shooter, next_bubble, first_text = init_game()

                # Update the shooter bubble and the next bubble in the queue
                if gameboard.bubbles_queue:
                    shooter = Shooter()
                    shooter.set_bubble(gameboard.bubbles_queue.pop(0))  # Assign the next bubble to the shooter
                    next_bubble = gameboard.bubbles_queue[0] if gameboard.bubbles_queue else None

                # Check if the current level is complete
                if gameboard.is_empty():
                    level_complete_screen(window, clock)  # Show the level complete screen
                    current_level += 1  # Move to the next level
                    gameboard = Gameboard(current_level)  # Create a new gameboard for the new level
                    shooter = Shooter()
                    shooter.set_bubble(gameboard.bubbles_queue.pop(0))  # Assign the first bubble of the new level
                    next_bubble = gameboard.bubbles_queue[0]  # Peek at the next bubble in the queue

                if no_iter % 8 == 0 and gameboard.update_gameboard():
                    running = end_game(window, clock)
                    if running:  # If restarting, reinitialize the game state
                        current_level, gameboard, shooter, next_bubble, first_text = init_game()

        # Continuously update the shooter's angle based on the mouse position
        shooter.update_angle(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

        # Render the game screen
        draw_background(window)  # Draw the background
        gameboard.draw(window)  # Draw the gameboard and bubbles
        first_text.draw(window)  # Draw the score text
        shooter.draw(window)  # Draw the shooter

        # Draw the next bubble if available
        if next_bubble:
            draw_next_bubble(window, next_bubble)

        # Update the display and set the frame rate
        pygame.display.flip()
        clock.tick(getProp('FPS'))

    pygame.quit()  # Quit the game when the loop ends

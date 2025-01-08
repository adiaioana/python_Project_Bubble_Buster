import pygame

# Import custom modules for styles and drawing utilities
from styles import getProp, colors, draw_background

def beginning_screen(window, clock):
    """
    Displays the beginning screen with a title and a "Play Game" button.
    """
    font = pygame.font.Font(None, 50)  # Load the default font with size 50
    title_text = font.render("Bubble Buster", True, colors()['white'])  # Render the title text in white
    button_text = font.render("Play Game", True, colors()['black'])  # Render the button text in black

    # Define the position and size of the "Play Game" button
    button_rect = pygame.Rect(
        getProp('window-width') // 2 - 100,  # Centered horizontally
        getProp('window-height') // 2,  # Vertically placed in the middle
        200,  # Button width
        50  # Button height
    )

    running = True
    while running:
        for event in pygame.event.get():  # Process events
            if event.type == pygame.QUIT:  # Exit if the window is closed
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                # Start the game if the button is clicked
                running = False

        draw_background(window)  # Draw the background on the window

        # Draw the title text at the top
        window.blit(
            title_text,
            (getProp('window-width') // 2 - title_text.get_width() // 2, getProp('window-height') // 2 - 100)
        )

        # Draw the button and its text
        pygame.draw.rect(window, colors()['white'], button_rect)  # Button rectangle
        window.blit(
            button_text,
            (button_rect.x + button_rect.width // 2 - button_text.get_width() // 2, button_rect.y + 10)
        )

        pygame.display.flip()  # Update the screen
        clock.tick(getProp('FPS'))  # Limit frame rate

def show_instructions(window, clock):
    """
    Displays the instructions screen with guidelines for playing the game.
    """
    font = pygame.font.Font(None, 36)  # Load the default font with size 36
    text_lines = [
        "REMOVE COLORED BUBBLES",
        "FROM THE PLAYING FIELD.",
        "LAUNCH EACH NEW BUBBLE",
        "TOWARD BUBBLES OF",
        "THE SAME COLOR."
    ]  # Instruction lines to display

    running = True
    while running:
        for event in pygame.event.get():  # Process events
            if event.type == pygame.QUIT:  # Exit if the window is closed
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Start the game when the ENTER key is pressed
                running = False

        draw_background(window)  # Draw the background

        # Display each line of instructions on the screen
        for i, line in enumerate(text_lines):
            text_surface = font.render(line, True, colors()['brown'])
            window.blit(
                text_surface,
                (getProp('window-width') // 2 - text_surface.get_width() // 2, 150 + i * 40)
            )

        # Display the "Press ENTER to start" message
        instruction_text = font.render("Press ENTER to start", True, colors()['brown'])
        window.blit(
            instruction_text,
            (getProp('window-width') // 2 - instruction_text.get_width() // 2, 500)
        )

        pygame.display.flip()  # Update the screen
        clock.tick(getProp('FPS'))  # Limit frame rate

def level_complete_screen(window, clock):
    """
    Displays the "Level Complete" screen with instructions to continue.
    """
    font = pygame.font.Font(None, 30)  # Load the default font with size 30
    message_text = font.render("Level Complete!", True, colors()['brown'])  # Render the level complete message
    instruction_text = font.render("Press ENTER to continue", True, colors()['brown'])  # Render instructions

    running = True
    while running:
        for event in pygame.event.get():  # Process events
            if event.type == pygame.QUIT:  # Exit if the window is closed
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Continue to the next level when the ENTER key is pressed
                running = False

        draw_background(window)  # Draw the background

        # Display the "Level Complete" message and instructions
        window.blit(
            message_text,
            (getProp('window-width') // 2 - message_text.get_width() // 2, getProp('window-height') // 2 - 50)
        )
        window.blit(
            instruction_text,
            (getProp('window-width') // 2 - instruction_text.get_width() // 2, getProp('window-height') // 2 + 50)
        )

        pygame.display.flip()  # Update the screen
        clock.tick(getProp('FPS'))  # Limit frame rate

def draw_next_bubble(window, next_bubble):
    """
    Draw the next bubble in the queue on the screen.
    """
    # Define the position of the next bubble display area
    bar_height = 80
    bar_y = getProp('window-height') - bar_height
    pygame.draw.rect(window, colors()['background'], (0, bar_y, getProp('window-width'), bar_height))  # Background bar

    # Display "Next Bubble" text
    text_font = pygame.font.Font(None, 36)
    text_surface = text_font.render("Next Bubble:", True, colors()['white'])
    text_x = 20
    text_y = bar_y + (bar_height // 2 - text_surface.get_height() // 2)
    window.blit(text_surface, (text_x, text_y))

    # Draw the next bubble
    bubble_x = text_x + text_surface.get_width() + 50
    bubble_y = bar_y + bar_height // 2
    pygame.draw.circle(window, next_bubble.outline, (bubble_x, bubble_y), next_bubble.radius)  # Outline
    pygame.draw.circle(window, next_bubble.fillcolor, (bubble_x, bubble_y), next_bubble.radius - next_bubble.outline_width)  # Fill color

def game_over_screen(window, clock):
    """
    Display the Game Over screen with options to quit or restart.
    """
    font = pygame.font.Font(None, 74)  # Large font for the "Game Over" message
    text = font.render("Game Over", True, (255, 0, 0))  # Render in red
    text_rect = text.get_rect(center=(getProp('window-width') // 2, getProp('window-height') // 3))

    restart_font = pygame.font.Font(None, 36)  # Smaller font for restart options
    restart_text = restart_font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(getProp('window-width') // 2, getProp('window-height') // 2))

    window.fill((0, 0, 0))  # Fill the screen with black
    window.blit(text, text_rect)  # Display the "Game Over" message
    window.blit(restart_text, restart_rect)  # Display the restart instructions

    pygame.display.flip()  # Update the screen

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exit the game if the window is closed
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_r:  # Restart the game
                    return 'restart'

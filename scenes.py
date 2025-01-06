import pygame

from styles import getProp, colors, draw_background


def beginning_screen(window, clock):
    font = pygame.font.Font(None, 50)
    title_text = font.render("Bubble Buster", True, colors()['white'])
    button_text = font.render("Play Game", True, colors()['black'])

    button_rect = pygame.Rect(getProp('window-width') // 2 - 100, getProp('window-height') // 2, 200, 50)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                running = False

        draw_background(window)

        window.blit(title_text, (getProp('window-width') // 2 - title_text.get_width() // 2, getProp('window-height') // 2 - 100))
        pygame.draw.rect(window, colors()['white'], button_rect)
        window.blit(button_text, (button_rect.x + button_rect.width // 2 - button_text.get_width() // 2, button_rect.y + 10))

        pygame.display.flip()
        clock.tick(getProp('FPS'))

def show_instructions(window, clock):
    font = pygame.font.Font(None, 36)
    text_lines = [
        "REMOVE COLORED BUBBLES FROM THE PLAYING FIELD.",
        "LAUNCH EACH NEW BUBBLE TOWARD BUBBLES OF THE SAME COLOR."
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False

        draw_background(window)

        for i, line in enumerate(text_lines):
            text_surface = font.render(line, True, colors()['brown'])
            window.blit(text_surface, (getProp('window-width') // 2 - text_surface.get_width() // 2, 150 + i * 40))

        instruction_text = font.render("Press ENTER to start", True, colors()['brown'])
        window.blit(instruction_text, (getProp('window-width') // 2 - instruction_text.get_width() // 2, 300))

        pygame.display.flip()
        clock.tick(getProp('FPS'))

def level_complete_screen(window, clock):
    font = pygame.font.Font(None, 30)
    message_text = font.render("Level Complete!", True, colors()['brown'])
    instruction_text = font.render("Press ENTER to continue", True, colors()['brown'])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False

        draw_background(window)

        window.blit(message_text, (getProp('window-width') // 2 - message_text.get_width() // 2, getProp('window-height') // 2 - 50))
        window.blit(instruction_text, (getProp('window-width') // 2 - instruction_text.get_width() // 2, getProp('window-height') // 2 + 50))

        pygame.display.flip()
        clock.tick(getProp('FPS'))

def draw_next_bubble(window, next_bubble):
    """
    Draw the next bubble in the queue on the screen.
    """
    # Define the position of the next bubble display area
    bar_height = 80
    bar_y = getProp('window-height') - bar_height
    pygame.draw.rect(window, colors()['background'], (0, bar_y, getProp('window-width'), bar_height))

    text_font = pygame.font.Font(None, 36)
    text_surface = text_font.render("Next Bubble:", True, colors()['white'])
    text_x = 20
    text_y = bar_y + (bar_height // 2 - text_surface.get_height() // 2)
    window.blit(text_surface, (text_x, text_y))

    # Position of the next bubble
    bubble_x = text_x + text_surface.get_width() + 50
    bubble_y = bar_y + bar_height // 2

    # Draw the next bubble
    pygame.draw.circle(window, next_bubble.outline, (bubble_x, bubble_y), next_bubble.radius)
    pygame.draw.circle(window, next_bubble.fillcolor, (bubble_x, bubble_y), next_bubble.radius - next_bubble.outline_width)


def game_over_screen(window, clock):
    """
    Display the Game Over screen with options to quit or restart.
    """
    font = pygame.font.Font(None, 74)  # You can change the font and size here
    text = font.render("Game Over", True, (255, 0, 0))  # Red color for Game Over text
    text_rect = text.get_rect(center=(getProp('window-width') // 2, getProp('window-height') // 3))

    restart_font = pygame.font.Font(None, 36)  # Smaller font for the restart option
    restart_text = restart_font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(getProp('window-width') // 2, getProp('window-height') // 2))

    # Draw the background color (black in this case)
    window.fill((0, 0, 0))

    # Draw the "Game Over" text and restart instructions
    window.blit(text, text_rect)
    window.blit(restart_text, restart_rect)

    # Update the screen
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Press Q to quit
                    pygame.quit()
                    exit()

                elif event.key == pygame.K_r:  # Press R to restart
                    return 'restart'  # Return 'restart' to indicate restart

    return 'quit'  # Default return value in case of quit event

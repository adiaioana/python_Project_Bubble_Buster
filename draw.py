import pygame
from styles import draw_background, getProp, colors
from game_elements import Gameboard
from effects import Score, Shooter, initialize_window

def beginning_screen(window, clock):
    font = pygame.font.Font(None, 50)
    title_text = font.render("Bubble Blaster", True, colors()['white'])
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
        "REMOVE COLORED BUBBLES",
        "FROM THE PLAYING FIELD.",
        "LAUNCH EACH NEW BUBBLE",
        "TOWARD BUBBLES",
        "OF THE SAME COLOR."
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
        window.blit(instruction_text, (getProp('window-width') // 2 - instruction_text.get_width() // 2, 500))

        pygame.display.flip()
        clock.tick(getProp('FPS'))

if __name__ == "__main__":
    window, clock = initialize_window(getProp('window-width'), getProp('window-height'), "Bubble Buster")

    beginning_screen(window, clock)
    show_instructions(window, clock)

    gameboard = Gameboard(1)  # level 1
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

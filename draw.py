import pygame
from styles import draw_background, getProp
from game_elements import Score


def initialize_window(width, height, title):
    """Initialize the game window."""
    pygame.init()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    MAINFONT = pygame.font.SysFont(getProp('font'), getProp('font-size'))
    DISPLAYRECT = window.get_rect()
    return window, pygame.time.Clock()

def main():
    window, clock = initialize_window(getProp('window-width'), getProp('window-height'), "Bubble Buster")

    running = True
    first_text = Score(20)
    while running:

        for event in pygame.event.get(): # handle user input
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                first_text.update([1,2,3])

        draw_background(window)
        first_text.draw(window)
        pygame.display.flip()
        clock.tick(getProp('FPS'))

    pygame.quit()


if __name__ == "__main__":
    main()

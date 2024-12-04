import math
import pygame

from small_math import get_line_end
from styles import getProp, randomItemFrom, darker_colors, colors

def initialize_window(width, height, title):
    """Initialize the game window."""
    pygame.init()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    return window, pygame.time.Clock()

def draw_dotted_line(window, start_pos, end_pos, color, dot_length, gap_length):
    """
    Dotted line from start_pos to end_pos.

    :param window: Pygame window to draw on
    :param start_pos: Starting position of the line (x, y)
    :param end_pos: Ending position of the line (x, y)
    :param color: Color of the line (R, G, B)
    :param dot_length: Length of each dot
    :param gap_length: Length of the gap between dots
    """
    x1, y1 = start_pos
    x2, y2 = end_pos
    total_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    dx = (x2 - x1) / total_length
    dy = (y2 - y1) / total_length

    current_length = 0
    while current_length < total_length:
        start_x = x1 + dx * current_length
        start_y = y1 + dy * current_length
        end_x = x1 + dx * (current_length + dot_length)
        end_y = y1 + dy * (current_length + dot_length)

        pygame.draw.line(window, color, (start_x, start_y), (end_x, end_y), 2)
        current_length += dot_length + gap_length

# works
class Score:
    def __init__(self, score):
        self.score = score
        self.font = pygame.font.SysFont(getProp('font'), getProp('font_size'))
        self.render = self.font.render('Score: ' + str(self.score), True, colors()['black'], colors()['white'])
        self.rect = self.render.get_rect()
        self.rect.left = 10
        self.rect.bottom = getProp('window-height') - 10

    def update(self, deletelist):
        self.score += len(deletelist) * 15
        self.render = self.font.render('Score: ' + str(self.score), True, randomItemFrom(darker_colors()), colors()['white'])

    def draw(self, window):
        window.blit(self.render, self.rect)

class Shooter:
    def __init__(self):
        self.dot_length=5
        self.gap_length=3
        self.angle = 90
        self.position = (getProp('window-width') // 2, getProp('window-height') - 50)


    def draw(self, window):
        """Draw the shooter as a dotted line."""
        end_x , end_y = get_line_end(200, self.angle, self.position)
        draw_dotted_line(window, self.position, (end_x, end_y), colors()['red'], dot_length=10, gap_length=5)

    def update_angle(self, mousex, mousey):
        dx = mousex - self.position[0]
        dy = self.position[1] - mousey
        shooter_angle = math.degrees(math.atan2(dy, dx))

        self.angle = max(0, min(180, shooter_angle))

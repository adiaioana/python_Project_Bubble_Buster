import math
import pygame

from game_elements import Bubble
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
        self.render = self.font.render('Score: ' + str(self.score), True, randomItemFrom(darker_colors(colors())), colors()['white'])

    def draw(self, window):
        window.blit(self.render, self.rect)

class Shooter:
    def __init__(self):
        self.dot_length = 60
        self.gap_length = 3
        self.angle = 90
        self.position = (getProp('window-width') // 2, getProp('window-height') - 50)

    def set_bubble(self, Bub):
        self.bubble = Bub
        self.bubble.set_coord(self.position[0], self.position[1])

    def draw(self, window):
        """Draw the shooter as a dotted line."""
        trajectory_points = self.calculate_reflection_path(500)
        for start, end in zip(trajectory_points, trajectory_points[1:]):
            draw_dotted_line(window, start, end, colors()['red'], dot_length=10, gap_length=5)
        if self.bubble:  # Only draw the bubble if it exists
            self.bubble.draw(window)

    def update_angle(self, mousex, mousey):
        dx = mousex - self.position[0]
        dy = self.position[1] - mousey
        self.angle = max(0, min(180, math.degrees(math.atan2(dy, dx))))

    def shoot(self):
        # Convert the angle to a unit vector
        dx = math.cos(math.radians(self.angle))
        dy = -math.sin(math.radians(self.angle))  # Negative because screen y-coordinates are inverted
        return dx, dy

    def calculate_reflection_path(self, max_length):
        WINDOW_WIDTH = getProp('window-width')
        """Calculate the path of the line with reflections."""
        points = [self.position]
        dx, dy = self.shoot()
        x, y = self.position
        remaining_length = max_length

        while remaining_length > 0:
            if dx > 0:  # Moving right
                t_x = (WINDOW_WIDTH - x) / dx
            elif dx < 0:  # Moving left
                t_x = -x / dx
            else:  # Vertical line, no horizontal movement
                t_x = float('inf')

            t_y = remaining_length / math.sqrt(dx ** 2 + dy ** 2)

            # Choose the shortest time to collision with a wall
            t = min(t_x, t_y)

            # Compute the endpoint
            end_x = x + t * dx
            end_y = y + t * dy

            # If hitting a vertical wall
            if t == t_x:
                dx = -dx  # Reflect horizontally
                end_x = max(0, min(WINDOW_WIDTH, end_x))  # Ensure it stays in bounds

            # Append the endpoint
            points.append((end_x, end_y))

            # Update position and remaining length
            x, y = end_x, end_y
            remaining_length -= t * math.sqrt(dx ** 2 + dy ** 2)

            # Break if we reach the top boundary
            if y <= 0:
                break

        return points

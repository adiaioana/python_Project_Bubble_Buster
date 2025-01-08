import math
import pygame

from game_elements import Bubble
from small_math import get_line_end
from styles import getProp, randomItemFrom, darker_colors, colors

def initialize_window(width, height, title):
    """
    Initialize the game window.

    Args:
        width (int): The width of the game window.
        height (int): The height of the game window.
        title (str): The title of the game window.

    Returns:
        tuple: A tuple containing the Pygame window and clock objects.
    """
    pygame.init()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    return window, pygame.time.Clock()

def draw_dotted_line(window, start_pos, end_pos, color, dot_length, gap_length):
    """
    Draw a dotted line from start_pos to end_pos.

    Args:
        window (pygame.Surface): Pygame window to draw on.
        start_pos (tuple): Starting position of the line (x, y).
        end_pos (tuple): Ending position of the line (x, y).
        color (tuple): Color of the line (R, G, B).
        dot_length (int): Length of each dot.
        gap_length (int): Length of the gap between dots.
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

class Score:
    """
    Represents the game score and its display.

    Attributes:
        score (int): Current score of the game.
        font (pygame.font.Font): Font used for rendering the score.
        render (pygame.Surface): Rendered score text.
        rect (pygame.Rect): Position of the score on the window.
    """
    def __init__(self, score):
        """
        Initialize the Score object.

        Args:
            score (int): Initial score value.
        """
        self.score = score
        self.font = pygame.font.SysFont(getProp('font'), getProp('font_size'))
        self.render = self.font.render('Score: ' + str(self.score), True, colors()['black'], colors()['white'])
        self.rect = self.render.get_rect()
        self.rect.left = 10
        self.rect.bottom = getProp('window-height') - 10

    def update(self, deletelist):
        """
        Update the score based on the number of deleted bubbles.

        Args:
            deletelist (list): List of bubbles removed.
        """
        self.score += len(deletelist) * 15
        self.render = self.font.render('Score: ' + str(self.score), True, randomItemFrom(darker_colors(colors())), colors()['white'])

    def draw(self, window):
        """
        Draw the score on the game window.

        Args:
            window (pygame.Surface): The game window.
        """
        window.blit(self.render, self.rect)

class Shooter:
    """
    Represents the bubble shooter.

    Attributes:
        dot_length (int): Length of the dots in the trajectory line.
        gap_length (int): Gap between the dots in the trajectory line.
        angle (float): Current angle of the shooter in degrees.
        position (tuple): Position of the shooter (x, y).
    """
    def __init__(self):
        """
        Initialize the Shooter object.
        """
        self.dot_length = 60
        self.gap_length = 3
        self.angle = 90
        self.position = (getProp('window-width') // 2, getProp('window-height') - 100)

    def set_bubble(self, Bub):
        """
        Assign a bubble to the shooter.

        Args:
            Bub (Bubble): The bubble to assign to the shooter.
        """
        self.bubble = Bub
        self.bubble.set_coord(self.position[0], self.position[1])

    def draw(self, window):
        """
        Draw the shooter as a dotted line and its bubble.

        Args:
            window (pygame.Surface): The game window.
        """
        trajectory_points = self.calculate_reflection_path(500)
        for start, end in zip(trajectory_points, trajectory_points[1:]):
            draw_dotted_line(window, start, end, colors()['red'], dot_length=10, gap_length=5)
        if self.bubble:
            self.bubble.draw(window)

    def update_angle(self, mousex, mousey):
        """
        Update the shooter's angle based on mouse position.

        Args:
            mousex (int): X-coordinate of the mouse.
            mousey (int): Y-coordinate of the mouse.
        """
        dx = mousex - self.position[0]
        dy = self.position[1] - mousey
        self.angle = max(0, min(180, math.degrees(math.atan2(dy, dx))))

    def shoot(self):
        """
        Calculate the direction vector for shooting.

        Returns:
            tuple: A unit vector (dx, dy) representing the shooting direction.
        """
        dx = math.cos(math.radians(self.angle))
        dy = -math.sin(math.radians(self.angle))  # Negative because screen y-coordinates are inverted
        return dx, dy

    def calculate_reflection_path(self, max_length):
        """
        Calculate the trajectory of the bubble with wall reflections.

        Args:
            max_length (int): Maximum length of the trajectory.

        Returns:
            list: A list of (x, y) points representing the trajectory path.
        """
        WINDOW_WIDTH = getProp('window-width')
        points = [self.position]
        dx, dy = self.shoot()
        x, y = self.position
        remaining_length = max_length

        while remaining_length > 0:
            if dx > 0:
                t_x = (WINDOW_WIDTH - x) / dx
            elif dx < 0:
                t_x = -x / dx
            else:
                t_x = float('inf')

            t_y = remaining_length / math.sqrt(dx ** 2 + dy ** 2)
            t = min(t_x, t_y)

            end_x = x + t * dx
            end_y = y + t * dy

            if t == t_x:
                dx = -dx
                end_x = max(0, min(WINDOW_WIDTH, end_x))

            points.append((end_x, end_y))
            x, y = end_x, end_y
            remaining_length -= t * math.sqrt(dx ** 2 + dy ** 2)

            if y <= 0:
                break

        return points
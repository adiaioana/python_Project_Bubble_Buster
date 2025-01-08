import math
import random

import pygame

import styles
from small_math import calculate_bubble_position, directions_for_pos, wdtcol_percentages_for_level
from styles import colors, getProp, randomItemFrom, darker_colors, ligther_colors, window_size, bubble_window_size

# Get window dimensions for the game
WINDOW_WIDTH, WINDOW_HEIGHT = window_size()

class Bubble:
    """
    Represents an individual bubble in the game.
    Attributes:
        - fillcolor: Color used to fill the bubble.
        - outline: Color for the bubble's outline.
        - outline_width: Thickness of the bubble's outline.
        - radius: Radius of the bubble.
        - xCoord, yCoord: Coordinates of the bubble's center.
    """
    def __init__(self, state, colorset, i, j):
        """
        Initializes a bubble's attributes.

        Args:
            state (str): Initial state of the bubble ('clear' or other).
            colorset (list): A set of colors available for the bubble.
            i (int): Row index of the bubble.
            j (int): Column index of the bubble.
        """
        self.fillcolor, self.outline = colors()['background'], colors()['background']
        self.outline_width = 3  # Thickness of the bubble's outline
        if state != 'clear':
            self.set_col(colorset)  # Set a random color if state is not clear
        self.radius = styles.getGenProp('bubble-radius')  # Set the bubble radius
        self.xCoord = calculate_bubble_position(i, j)[0] + getProp('margin-left')  # X-coordinate
        self.yCoord = calculate_bubble_position(i, j)[1] + getProp('margin-top')  # Y-coordinate

    def set_exact_col(self, fillc, outc):
        self.fillcolor = fillc
        self.outline = outc
    def set_coord(self, xc, yc):
        """
        Updates the bubble's coordinates.

        Args:
            xc (int): New x-coordinate.
            yc (int): New y-coordinate.
        """
        self.xCoord, self.yCoord = xc, yc

    def is_clear(self):
        """
        Checks if the bubble is in a clear state.

        Returns:
            bool: True if the bubble is clear, False otherwise.
        """
        return True if self.fillcolor == self.outline else False

    def set_col(self, colorset):
        """
        Assigns a random color to the bubble from a given color set.

        Args:
            colorset (list): A set of colors available for the bubble.
        """
        self.fillcolor, self.outline = randomItemFrom(ligther_colors(colorset)), randomItemFrom(darker_colors(colorset))

    def set_style(self, fillC, outC):
        """
        Sets specific colors for the bubble.

        Args:
            fillC (tuple): Color for the fill.
            outC (tuple): Color for the outline.
        """
        self.fillcolor, self.outline = fillC, outC

    def set_clear(self):
        """
        Clears the bubble, resetting its color to the background color.
        """
        self.fillcolor = self.outline = colors()['background']

    def draw(self, window):
        """
        Renders the bubble on the game window.

        Args:
            window (pygame.Surface): The window surface where the bubble is drawn.
        """
        center = (self.xCoord, self.yCoord)
        pygame.draw.circle(window, self.outline, center, self.radius)  # Draw outline
        pygame.draw.circle(window, self.fillcolor, center, self.radius - self.outline_width)  # Draw fill


class Gameboard:
    """
    Represents the entire gameboard.
    Attributes:
        - height, width: Dimensions of the board in terms of bubbles.
        - level: Current game level.
        - colorSet: Color palette for the current level.
        - matrix: 2D list of Bubble objects representing the gameboard.
        - bubbles_queue: Queue of bubbles for the shooter.
    """
    def __init__(self, lvlcount):
        """
        Initializes the gameboard with bubbles and level-specific settings.

        Args:
            lvlcount (int): Current game level.
        """
        self.height, self.width = bubble_window_size()  # Dimensions of the board
        self.level = lvlcount  # Current level
        self.colorSet = styles.colorForLevel(lvlcount)  # Color set for the level
        # Create a matrix of bubbles initialized as 'clear'
        self.matrix = [[Bubble('clear', self.colorSet, i, j) for j in range(self.height)] for i in range(self.width)]

        wdth_percentage, col_percentage = wdtcol_percentages_for_level(lvlcount)

        self.random_init(0.4, 0.3)  # Populate board with random bubbles
        self.bubbles_queue = [Bubble('active', self.colorSet, 0, 0) for _ in range(100)]  # Shooter's bubble queue

    def find_cluster(self, start_i, start_j, color, outcol):
        """
        Finds all connected bubbles of the same color starting from a given bubble.

        Args:
            start_i (int): Row index of the starting bubble.
            start_j (int): Column index of the starting bubble.
            color (tuple): Color to match.
            outcol (tuple): Outline color to match.

        Returns:
            list: A list of (row, column) tuples representing the cluster of bubbles.
        """
        visited = set()
        cluster = []
        stack = [(start_i, start_j)]  # Stack for depth-first search

        while stack:
            i, j = stack.pop()
            if (i, j) in visited:
                continue
            visited.add((i, j))

            if 0 <= i < self.width and 0 <= j < self.height:
                bubble = self.matrix[i][j]
                if bubble.fillcolor == color and bubble.outline == outcol and not bubble.is_clear():
                    cluster.append((i, j))  # Add bubble to the cluster
                    # Add neighboring bubbles to the stack
                    neighbors = self.get_neighbors(i, j)
                    stack.extend(neighbors)

        return cluster

    def get_neighbors(self, i, j):
        """
        Retrieves neighboring bubbles for the given (i, j) position.

        Args:
            i (int): Row index of the bubble.
            j (int): Column index of the bubble.

        Returns:
            list: A list of (row, column) tuples representing neighbors.
        """
        return [(i + di, j + dj) for di, dj in directions_for_pos(i)
                if 0 <= i + di < self.width and 0 <= j + dj < self.height]

    def remove_cluster(self, cluster):
        """
        Clears all bubbles in the given cluster.

        Args:
            cluster (list): List of (row, column) tuples representing the cluster.
        """
        for i, j in cluster:
            self.matrix[i][j].set_clear()

    def update_after_hit(self, i, j, score):
        """
        Updates the gameboard after a bubble is placed.

        Args:
            i (int): Row index of the placed bubble.
            j (int): Column index of the placed bubble.
            score (object): The score object to be updated.
        """
        bubble = self.matrix[i][j]
        color = bubble.fillcolor

        # Find connected bubbles of the same color
        cluster = self.find_cluster(i, j, color, bubble.outline)

        # Remove the cluster if it meets the minimum size
        if len(cluster) >= 3:  # Minimum cluster size
            self.remove_cluster(cluster)
            score.update(cluster)

        self.remove_floating_bubbles()  # Clear floating bubbles

    def remove_floating_bubbles(self):
        """
        Clears bubbles that are not connected to the top row.
        """
        visited = set()
        floating = set()

        stack = [(0, j) for j in range(self.height) if not self.matrix[0][j].is_clear()]

        while stack:
            i, j = stack.pop()
            if (i, j) in visited:
                continue
            visited.add((i, j))

            neighbors = self.get_neighbors(i, j)
            for ni, nj in neighbors:
                if not self.matrix[ni][nj].is_clear() and (ni, nj) not in visited:
                    stack.append((ni, nj))

        for i in range(self.width):
            for j in range(self.height):
                if (i, j) not in visited and not self.matrix[i][j].is_clear():
                    floating.add((i, j))

        for i, j in floating:
            self.matrix[i][j].set_clear()

    def random_init(self, wdtpercentage, colpercentage):
        """
        Randomly initializes bubbles on the board for the level.

        Args:
            wdtpercentage (float): Percentage of width to fill with bubbles.
            colpercentage (float): Percentage of columns to fill.
        """
        no_lines = int(self.height * colpercentage) +(0 if self.level==1 else 1)

        for i in range(no_lines):
            for j in range(len(self.matrix[i])):
                self.matrix[i][j].set_col(self.colorSet)

        for i in range(no_lines):
            no_randoms = max(int(self.width / 2), int(wdtpercentage * (no_lines - 2 * i)))
            who_to_col = random.choices(range(self.width), k=no_randoms)
            for j in who_to_col:
                self.matrix[i][j].set_clear()

    def draw(self, window):
        """
        Renders the gameboard and its bubbles.

        Args:
            window (pygame.Surface): The window surface where the gameboard is drawn.
        """
        for x in range(self.width):
            for y in range(self.height):
                if not self.matrix[x][y].is_clear():
                    self.matrix[x][y].draw(window)

        bubble_diam = styles.getGenProp('bubble-radius') * 2
        pygame.draw.line(window, colors()['brown'], (0, bubble_diam * self.height + 15),
                         (getProp('window-width'), bubble_diam * self.height + 15), 3)

    def is_bubble_below_board(self, y_position):
        """
        Checks if a bubble is below the gameboard.

        Args:
            y_position (int): The y-coordinate of the bubble.

        Returns:
            bool: True if the bubble is below the board, False otherwise.
        """
        return y_position >= self.height

    def find_target_row(self, col, dx, dy):
        """
        Find the last free row in the specified column (col) along the trajectory
        defined by dx and dy.

        Args:
            col (int): The target column index.
            dx (float): The horizontal direction component.
            dy (float): The vertical direction component.

        Returns:
            int: The row index of the target cell.
        """
        x = self.width // 2  # Example, can be set to shooter's x position
        y = 0  # Starting from the top row

        while 0 <= x < self.width and 0 <= y < self.height:  # Iterate along the path
            if int(x) == col:
                if self.matrix[col][int(y)].is_clear():
                    return int(y + 1)
            x += dx * 5
            y += dy * 5

        return int(y - 1)

    def update_gameboard(self):
        '''
        Updates the game board by pushing another row of bubbles on top
        Argument: The gameboard itself
        :return: True if the game has ended, False if not
        '''

        for y in range(self.height):
            if not self.matrix[self.width-1][y].is_clear():
                return True

        for x in range(self.width-1,1,-1):
            for y in range(self.height):
                self.matrix[x][y].set_exact_col(self.matrix[x-2][y].fillcolor, self.matrix[x-2][y].outline)
                self.matrix[x-2][y].set_clear()

        for y in range(self.height):
            self.matrix[0][y].set_col(self.colorSet)
            self.matrix[1][y].set_col(self.colorSet)
        return False

    def use_shooter(self, shooter, window, score):
        """
        Simulates the shooter bubble's trajectory and updates the game state.

        Args:
            shooter (object): The shooter object controlling the bubble.
            window (pygame.Surface): The game window for rendering.
            score (object): The score object for tracking points.

        Returns:
            bool: True if the bubble is successfully shot, False otherwise.
        """
        dx, dy = shooter.shoot()
        x, y = shooter.position[0], shooter.position[1]
        bubble_radius = shooter.bubble.radius
        bubble_outline = shooter.bubble.outline_width
        hit = False
        target_cell = None
        no_iter = 0

        while not hit:
            no_iter += 1
            x += dx * 5
            y += dy * 5

            if x <= 0:
                x = 0
                dx = -dx
            elif x >= getProp('window-width'):
                x = getProp('window-width')
                dx = -dx
            elif y <= 0:
                y = 0
                target_cell = self.find_closest_free_top(x)
                hit = True

            if not hit:
                for i in range(self.width):
                    for j in range(self.height):
                        bubble_x, bubble_y = self.matrix[i][j].xCoord, self.matrix[i][j].yCoord
                        distance = math.sqrt((x - bubble_x) ** 2 + (y - bubble_y) ** 2)
                        if distance <= 2 * bubble_radius + 2 * bubble_outline and not self.matrix[i][j].is_clear():
                            target_cell = self.find_intersecting_neighbor(i, j, dx, dy, x, y)
                            if i == self.width - 1:
                                return False
                            hit = True
                            break

            if not hit and no_iter%6 == 0:
                shooter.bubble.set_coord(int(x), int(y))
                shooter.bubble.draw(window)

            pygame.display.update()
            pygame.time.delay(10)

        if hit:
            if target_cell is None:
                if self.check_last_row_collision(shooter.position[0], shooter.position[1], dx, dy):
                    return False
                target_cell = (0, 0) if dx < 0 else (0, self.width - 1)

            i, j = target_cell
            self.matrix[i][j].set_style(shooter.bubble.fillcolor, shooter.bubble.outline)
            self.update_after_hit(i, j, score)
            return True

        return False

    def check_last_row_collision(self, x, y, dx, dy):
        """
        Checks if the bubble's trajectory intersects with the last row.

        Args:
            x (float): The x-coordinate of the bubble.
            y (float): The y-coordinate of the bubble.
            dx (float): The horizontal direction component.
            dy (float): The vertical direction component.

        Returns:
            bool: True if a collision occurs, False otherwise.
        """
        bubble_radius = self.matrix[0][0].radius
        bubble_outline = self.matrix[0][0].outline_width

        while y < getProp('window-height'):
            if x <= 0:
                x = 0
                dx = -dx
            elif x >= getProp('window-width'):
                x = getProp('window-width')
                dx = -dx

            if y >= (self.height - 1) * bubble_radius:
                for i in range(self.width):
                    if not self.matrix[i][self.height - 1].is_clear():
                        bubble_x, bubble_y = self.matrix[i][self.height - 1].xCoord, self.matrix[i][self.height - 1].yCoord
                        distance = math.sqrt((x - bubble_x) ** 2 + (y - bubble_y) ** 2)
                        if distance <= 2 * bubble_radius + 2 * bubble_outline:
                            return True
                break

            x += dx * 5
            y += dy * 5

        return False

    def find_intersecting_neighbor(self, i, j, dx, dy, shooter_x, shooter_y):
        """
        Finds the first clear neighbor of a bubble that intersects with the shooter's trajectory.

        Args:
            i (int): Row index of the bubble.
            j (int): Column index of the bubble.
            dx (float): The horizontal direction component of the trajectory.
            dy (float): The vertical direction component of the trajectory.
            shooter_x (float): X-coordinate of the shooter bubble.
            shooter_y (float): Y-coordinate of the shooter bubble.

        Returns:
            tuple or None: Coordinates of the intersecting neighbor as (row, column),
            or None if no valid neighbor is found.
        """

        # Hexagonal neighbor offsets
        neighbors = [(-1, 0), (-1, 1), (0, -1),(0, 1), (1, 0), (1, 1)] \
            if i%2 == 0 else [(-1, 0), (-1, -1), (0, -1), (0, 1), (1, 0), (1, -1)]

        neighbors.reverse()

        for di, dj in neighbors:
            ni, nj = i + di, j + dj

            # Ensure the neighbor is within bounds
            if 0 <= ni < self.width and 0 <= nj < self.height:
                neighbor = self.matrix[ni][nj]

                # Check if the neighbor is clear
                if neighbor.is_clear():
                    # Calculate the projection of the shooter's trajectory onto the neighbor
                    neighbor_x, neighbor_y = neighbor.xCoord, neighbor.yCoord
                    distance_to_trajectory = abs(
                        (neighbor_y - shooter_y) * dx - (neighbor_x - shooter_x) * dy) / math.sqrt(dx ** 2 + dy ** 2)

                    # If the neighbor intersects the trajectory, return it
                    if distance_to_trajectory <= self.matrix[ni][nj].radius + self.matrix[ni][nj].outline_width:
                        return (ni, nj)

        # If no valid neighbor is found, return None
        return None

    def find_closest_free_top(self, x):
        """
        Finds the closest free position in the top row based on the x-coordinate.

        Args:
            x (float): The x-coordinate of the bubble.

        Returns:
            tuple or None: Coordinates of the closest free bubble in the top row as (row, column),
            or None if no free position is available.
        """
        closest_cell = None
        min_distance = float("inf")

        for j in range(self.height):
            if self.matrix[0][j].is_clear():
                bubble_x = self.matrix[0][j].xCoord
                distance = abs(x - bubble_x)
                if distance < min_distance:
                    closest_cell = (0, j)
                    min_distance = distance

        return closest_cell

    def is_empty(self):
        """
        Checks if the gameboard is completely empty.

        Returns:
            bool: True if all bubbles on the board are clear, False otherwise.
        """

        for i in range(self.width):
            for j in range(self.height):
                if not self.matrix[i][j].is_clear():
                    return False

        return True
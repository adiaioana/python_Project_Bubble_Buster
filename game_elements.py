import math
import random

import pygame
from numpy.ma.extras import intersect1d

import styles
from small_math import calculate_bubble_position
from styles import colors, getProp, randomItemFrom, darker_colors, ligther_colors, window_size, bubble_window_size

WINDOW_WIDTH, WINDOW_HEIGHT = window_size()

class Bubble:

    def __init__(self, state, colorSet, i,j):
        self.fillcolor, self.outline = colors()['background'], colors()['background']
        self.outline_width = 3
        if state != 'clear':
            self.set_col(colorSet)
        self.radius = styles.getGenProp('bubble-radius')
        self.xCoord = calculate_bubble_position(i, j)[0] + getProp('margin-left')
        self.yCoord = calculate_bubble_position(i, j)[1] + getProp('margin-top')

    def set_coord(self, xC, yC):
        self.xCoord, self.yCoord = xC, yC
    def is_clear(self):
        return True if self.fillcolor == self.outline else False
    def set_col(self, colorSet):
        self.fillcolor, self.outline = randomItemFrom(ligther_colors(colorSet)), randomItemFrom(darker_colors(colorSet))
    def set_style(self,fillC, outC):
        self.fillcolor, self.outline = fillC, outC
    def set_clear(self):
        self.fillcolor = self.outline = colors()['background']

    def draw(self, window):
        center = (self.xCoord, self.yCoord)
        pygame.draw.circle(window, self.outline, center, self.radius )
        pygame.draw.circle(window, self.fillcolor, center, self.radius - self.outline_width)


class Gameboard:
    def __init__(self, lvlCount):
        self.height, self.width = bubble_window_size()
        self.level = lvlCount
        self.colorSet = styles.colorForLevel(lvlCount)
        self.matrix = [[Bubble('clear', self.colorSet, i, j) for j in range(self.height)] for i in range(self.width)]
        self.random_init(0.4, 0.3)
        self.bubbles_queue = [Bubble('active', self.colorSet, 0, 0) for _ in range(100)]  # Queue of bubbles for shooter

    def find_cluster(self, start_i, start_j, color, outcol):
        """
        Find all bubbles connected to the (start_i, start_j) bubble of the same color.
        """
        visited = set()
        cluster = []
        stack = [(start_i, start_j)]

        while stack:
            i, j = stack.pop()
            if (i, j) in visited:
                continue
            visited.add((i, j))

            # Ensure the bubble matches the color
            if 0 <= i < self.width and 0 <= j < self.height:
                bubble = self.matrix[i][j]
                if bubble.fillcolor == color and bubble.outline == outcol and not bubble.is_clear():
                    cluster.append((i, j))

                    # Add neighbors to the stack
                    neighbors = self.get_neighbors(i, j)
                    stack.extend(neighbors)

        return cluster

    def get_neighbors(self, i, j):
        """
        Get neighbors of a bubble at (i, j), considering the staggered grid.
        """
        neighbors = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)] if i % 2 == 0 else [(-1, 0), (-1, -1), (0, -1), (0, 1), (1, 0), (1, -1)]
        return [(i + di, j + dj) for di, dj in neighbors if 0 <= i + di < self.width and 0 <= j + dj < self.height]

    def remove_cluster(self, cluster):
        """
        Remove all bubbles in the given cluster and set them to 'clear'.
        """
        for i, j in cluster:
            self.matrix[i][j].set_clear()

    def update_after_hit(self, i, j, score):
        """
        Update the gameboard after a bubble is placed.
        - Find clusters connected to (i, j).
        - Remove them if they meet the criteria.
        - Update the score.
        """
        bubble = self.matrix[i][j]
        color = bubble.fillcolor

        # Find the connected cluster of the same color
        cluster = self.find_cluster(i, j, color, bubble.outline)

        # Remove the cluster if it meets the minimum size
        if len(cluster) >= 3:  # Adjust the minimum size as needed
            self.remove_cluster(cluster)
            score.update(cluster)

        # Optional: Remove floating bubbles
        self.remove_floating_bubbles()

    def remove_floating_bubbles(self):
        """
        Remove all bubbles that are not connected to the top row.
        """
        visited = set()
        floating = set()

        # Perform a BFS/DFS from all bubbles in the top row
        stack = [(0, j) for j in range(self.height) if not self.matrix[0][j].is_clear()]

        while stack:
            i, j = stack.pop()
            if (i, j) in visited:
                continue
            visited.add((i, j))

            # Add neighbors
            neighbors = self.get_neighbors(i, j)
            for ni, nj in neighbors:
                if not self.matrix[ni][nj].is_clear() and (ni, nj) not in visited:
                    stack.append((ni, nj))

        # Identify floating bubbles (not visited but not clear)
        for i in range(self.width):
            for j in range(self.height):
                if (i, j) not in visited and not self.matrix[i][j].is_clear():
                    floating.add((i, j))

        # Clear floating bubbles
        for i, j in floating:
            self.matrix[i][j].set_clear()


    def random_init(self, wdtpercentage, colpercentage):
        no_lines = int(self.height * colpercentage)

        for i in range(no_lines):
            for j in range(len(self.matrix[i])):
                self.matrix[i][j].set_col(self.colorSet)
        for i in range(no_lines):
            no_randoms = max(int(self.width/3),int(wdtpercentage * (no_lines-2*i)))
            who_to_col = random.choices(range(self.width), k=no_randoms)
            for j in who_to_col:
               self.matrix[i][j].set_clear()


    def draw(self,window):

        for x in range(self.width):
            for y in range(self.height):
                if not self.matrix[x][y].is_clear():
                    self.matrix[x][y].draw(window)
        bubble_diam = styles.getGenProp('bubble-radius') * 2
        pygame.draw.line(window, colors()['brown'], (0, bubble_diam * self.height + 15), (getProp('window-width'), bubble_diam * self.height + 15), 3)

    def is_bubble_below_board(self, y_position):
        return y_position >= self.height

    def find_target_row(self, col, dx, dy):
        """
        Find the last free row in the specified column (col) along the trajectory
        defined by dx and dy. Returns the row index of the target cell.
        """
        # Starting position (the shooter's position)
        x = self.width // 2  # Example, can be set to shooter's x position
        y = 0  # Starting from the top row

        while 0 <= x < self.width and 0 <= y < self.height:  # Iterate along the path
            # If the bubble intersects with the current column (col)
            if int(x) == col:
                # Check if the current position is free
                if self.matrix[col][int(y)].is_clear():
                    return int(y+1)  # The first free row is the target position

            # Move the bubble along the trajectory (adjust based on dx, dy)
            x += dx * 5  # Move horizontally
            y += dy * 5  # Move vertically

        return int(y-1) # If no intersection occurs, return the last row

    def use_shooter(self, shooter, window, score):
        dx, dy = shooter.shoot()  # Direction vector of the bubble
        x, y = shooter.position[0], shooter.position[1]  # Starting position of the shooter
        bubble_radius = shooter.bubble.radius
        bubble_outline = shooter.bubble.outline_width
        hit = False
        target_cell = None
        while not hit:
            # Move the bubble along the trajectory (apply dx, dy)
            x += dx * 5
            y += dy * 5

            # Check for collision with the edges of the gameboard (reflect off the edges)
            if x <= 0:  # Left margin
                x = 0  # Snap to the left edge
                dx = -dx  # Reflect horizontally
            elif x >= getProp('window-width'):  # Right margin
                x = getProp('window-width')  # Snap to the right edge
                dx = -dx  # Reflect horizontally
            elif y <= 0:  # Top margin
                y = 0  # Snap to the top margin
                target_cell = self.find_closest_free_top(x)  # Find first free spot
                hit = True  # Bubble hit the top, find target position


            # Check for collisions with other bubbles on the board
            if not hit:
                for i in range(self.width):
                    for j in range(self.height):
                        bubble_x, bubble_y = self.matrix[i][j].xCoord, self.matrix[i][j].yCoord
                        distance = math.sqrt((x - bubble_x) ** 2 + (y - bubble_y) ** 2)
                        if distance <= 2 * bubble_radius + 2 * bubble_outline and not self.matrix[i][j].is_clear():
                            target_cell = self.find_intersecting_neighbor(i, j, dx, dy, x, y)
                            if i == self.width-1:
                                return False
                            hit = True
                            break

            # If the shot hasn't hit a target yet, continue moving the bubble
            if not hit:
                shooter.bubble.set_coord(int(x), int(y))  # Update the bubble's position
                shooter.bubble.draw(window)

            pygame.display.update()
            pygame.time.delay(10)

        if hit:
            # Set the target position if no intersection found
            if target_cell is None:
                if self.check_last_row_collision(shooter.position[0], shooter.position[1], dx, dy):
                    return False
                target_cell = (0, 0) if dx < 0 else (0, self.width - 1)

            i, j = target_cell
            self.matrix[i][j].set_style(shooter.bubble.fillcolor, shooter.bubble.outline)
            self.update_after_hit(i, j, score)
            return True

        return False  # Return False if the bubble is successfully shot

    def check_last_row_collision(self, x, y, dx, dy):
        """
        Checks if the trajectory of the bubble intersects with the last row,
        considering reflections off the left and right walls.
        Returns True if the bubble intersects the last row, False otherwise.
        """
        bubble_radius = self.matrix[0][0].radius
        bubble_outline = self.matrix[0][0].outline_width

        # Simulate the movement of the bubble considering reflection
        while y < getProp('window-height'):  # Continue moving until the bubble goes off screen
            # If the bubble hits the left or right margin, reflect it
            if x <= 0:  # Left margin
                x = 0
                dx = -dx  # Reflect horizontally
            elif x >= getProp('window-width'):  # Right margin
                x = getProp('window-width')
                dx = -dx  # Reflect horizontally

            # If the bubble has reached or is about to reach the last row
            if y >= (self.height - 1) * bubble_radius:  # Check if it intersects with the last row
                for i in range(self.width):
                    if not self.matrix[i][self.height - 1].is_clear():  # Check if there's a bubble in the last row
                        bubble_x, bubble_y = self.matrix[i][self.height - 1].xCoord, self.matrix[i][
                            self.height - 1].yCoord
                        distance = math.sqrt((x - bubble_x) ** 2 + (y - bubble_y) ** 2)
                        if distance <= 2 * bubble_radius + 2 * bubble_outline:
                            return True  # Return True if there's a collision with a bubble in the last row
                break  # Break the loop if we are not intersecting with the last row

            # Move the bubble along the trajectory (apply dx, dy)
            x += dx * 5
            y += dy * 5

        return False  # Return False if no collision with the last row

    def find_intersecting_neighbor(self, i, j, dx, dy, shooter_x, shooter_y):
        """
        Find the first clear neighbor of the (i, j) bubble that intersects with the shooter's trajectory.
        """
        # Hexagonal neighbor offsets
        neighbors = [(-1, 0), (-1, 1), (0, -1),(0, 1), (1, 0), (1, 1)] if i%2 == 0 else [(-1, 0), (-1, -1), (0, -1), (0, 1), (1, 0), (1, -1)]

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
        """Find the closest free position in the top row based on the x-coordinate."""
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

        for i in range(self.width):
            for j in range(self.height):
                if not self.matrix[i][j].is_clear():
                    return False

        return True
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

        for x in range(0, self.width):
            for y in range(0, self.height):
                if not self.matrix[x][y].is_clear():
                    self.matrix[x][y].draw(window)

    def use_shooter(self, shooter, window, score):
        dx, dy = shooter.shoot()  # Direction vector of the bubble
        x, y = shooter.position[0], shooter.position[1]  # Starting position of the shooter
        bubble_radius = shooter.bubble.radius
        bubble_outline = shooter.bubble.outline_width
        hit = False
        target_cell = None

        while not hit:
            x += dx * 5  # Move the bubble along the trajectory
            y += dy * 5

            # Check for collision with the edges of the gameboard
            if x < 0 or x > WINDOW_WIDTH:
                dx = -dx  # Reflect horizontally
                x = max(0, min(WINDOW_WIDTH, x))  # Ensure x stays within bounds

            # Check for collision with the top margin
            if y <= 0:
                y = 0  # Snap to the top margin
                # Find the nearest empty cell in the top row
                for j in range(self.height):
                    if self.matrix[0][j].is_clear():
                        bubble_x, bubble_y = self.matrix[0][j].xCoord, self.matrix[0][j].yCoord
                        if abs(x - bubble_x) <= bubble_radius + bubble_outline:
                            target_cell = (0, j)
                            hit = True
                            break
                break  # Stop the loop if a top row position is found

            dmin = 2 * bubble_radius + 2 * bubble_outline + 1

            # Check for collision with existing bubbles on the gameboard
            for i in range(self.width - 1, -1, -1):
                for j in range(self.height):
                    bubble_x, bubble_y = self.matrix[i][j].xCoord, self.matrix[i][j].yCoord

                    # If the current gameboard bubble is not clear
                    if not self.matrix[i][j].is_clear():
                        # Calculate the distance between the moving bubble and the gameboard bubble
                        distance = math.sqrt((x - bubble_x) ** 2 + (y - bubble_y) ** 2)

                        # If the moving bubble is close enough to this bubble, it hits
                        if distance <= 2 * bubble_radius + 2 * bubble_outline:
                            # Parse the neighbors of this bubble
                            if distance < dmin:
                                target_cell = self.find_intersecting_neighbor(i, j, dx, dy, x, y)
                                dmin = distance
                            hit = True
                            break

            if not hit:
                shooter.bubble.set_coord(int(x), int(y))  # Update the bubble's position
                shooter.bubble.draw(window)

            pygame.display.update()
            pygame.time.delay(10)

        if hit and target_cell:
            i, j = target_cell
            self.matrix[i][j].set_style(shooter.bubble.fillcolor, shooter.bubble.outline)
            self.update_after_hit(i, j, score)

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

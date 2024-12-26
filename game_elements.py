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
        self.matrix = [[Bubble('clear', self.colorSet,i,j) for j in range(self.height)] for i in range(self.width)]
        self.bubbles_queue = [Bubble('color',self.colorSet,-1,-1) for _ in range(10)]
        self.random_init(0.4,0.3)

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

    def use_shooter(self, shooter, window):
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
            if x < 0 or x > WINDOW_WIDTH or y < 0 or y > WINDOW_HEIGHT:
                break
            dmin = 2 * bubble_radius + 2 * bubble_outline + 1
            # Check for collision with existing bubbles on the gameboard
            for i in range(self.width-1,-1,-1):
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
                            break ### hard to say if i should break here, depands on game mode i guess


            # Draw the moving bubble
            window.fill(styles.colors()['background'])  # Clear the screen
            self.draw(window)  # Redraw the gameboard
            pygame.display.update()
            if not hit:
                shooter.bubble.set_coord(int(x), int(y))  # Update the bubble's position
                shooter.bubble.draw(window)
            pygame.display.update()
            pygame.time.delay(10)

        # Place the bubble on the snapped gameboard position
        if hit and target_cell:
            window.fill(styles.colors()['background'])  # Clear the screen
            self.draw(window)
            pygame.time.delay(10)
            i, j = target_cell
            self.matrix[i][j].set_style(shooter.bubble.fillcolor, shooter.bubble.outline)
            self.matrix[i][j].draw(window)
            pygame.display.update()
            pygame.time.delay(10)

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

    '''
    def use_shooter(self, shooter, window):
        dx, dy = shooter.shoot()  # Direction vector of the bubble
        x, y = shooter.position[0], shooter.position[1]  # Starting position of the shooter
        bubble_radius = shooter.bubble.radius
        hit = False
        target_cell = None

        while not hit:
            x += dx * 5  # Move the bubble along the trajectory
            y += dy * 5

            # Check for collision with the edges of the gameboard
            if x < 0 or x > WINDOW_WIDTH or y < 0 or y > WINDOW_HEIGHT:
                break

            # Check for collision with existing bubbles on the gameboard
            for i in range(self.width):
                for j in range(self.height):
                    bubble_x, bubble_y = self.matrix[i][j].xCoord, self.matrix[i][j].yCoord

                    # If the current gameboard bubble is not clear
                    if not self.matrix[i][j].is_clear():
                        # Calculate the distance between the moving bubble and the gameboard bubble
                        distance = math.sqrt((x - bubble_x) ** 2 + (y - bubble_y) ** 2)

                        # If the moving bubble is close enough to this bubble, it hits
                        if distance <= 2 * bubble_radius:
                            # Find the first clear cell next to this bubble along the trajectory
                            target_cell = self.get_adjacent_clear_cell(i, j, dx, dy)
                            hit = True
                            break
                if hit:
                    break

            # Draw the moving bubble
            window.fill(styles.colors()['background'])  # Clear the screen
            self.draw(window)  # Redraw the gameboard
            shooter.bubble.set_coord(int(x), int(y))  # Update the bubble's position
            shooter.bubble.draw(window)
            pygame.display.update()
            pygame.time.delay(10)

        # Place the bubble on the snapped gameboard position
        if hit and target_cell:
            i, j = target_cell
            self.matrix[i][j].set_style(shooter.bubble.fillcolor, shooter.bubble.outline)
            self.matrix[i][j].draw(window)
            pygame.display.update()

    def get_adjacent_clear_cell(self, i, j, dx, dy):
        """
        Find the first clear cell next to the (i, j) bubble along the trajectory direction,
        prioritizing alignment with the trajectory and neighbors closer vertically (lower rows).
        """
        # Hexagonal neighbor offsets
        neighbors = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]

        # Sort neighbors by:
        # 1. Alignment with the trajectory (dot product with direction vector)
        # 2. Row preference (lower rows have higher di values)
        neighbors.sort(key=lambda d: (-(d[0] * dx + d[1] * dy), d[0]), reverse=True)

        # Check each neighbor for a clear cell
        for di, dj in neighbors:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.width and 0 <= nj < self.height and self.matrix[ni][nj].is_clear():
                return (ni, nj)

        # If no clear cell is found, return the original cell
        return (i, j)
'''
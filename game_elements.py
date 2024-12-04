import random

import pygame
import styles
from small_math import calculate_bubble_position
from styles import colors, getProp, randomItemFrom, darker_colors, ligther_colors, window_size, bubble_window_size

WINDOW_WIDTH, WINDOW_HEIGHT = window_size()

class Bubble:
    def __init__(self, state):
        self.fillcolor, self.outline = colors()['background'], colors()['background']
        if state != 'clear':
            self.set_col()
        self.radius = styles.getGenProp('bubble-radius')

    def is_clear(self):
        return True if self.fillcolor == self.outline else False
    def set_col(self):
        self.fillcolor, self.outline = randomItemFrom(ligther_colors()), randomItemFrom(darker_colors())

    def draw(self, window, center):
        outline_width = 3
        center = (center[0] + getProp('margin-left') , center[1] + getProp('margin-top') )
        pygame.draw.circle(window, self.outline, center, self.radius )
        pygame.draw.circle(window, self.fillcolor, center, self.radius - outline_width)


class Gameboard:
    def __init__(self):
        self.height, self.width = bubble_window_size()
        self.matrix = [[Bubble('clear') for _ in range(self.height)] for _ in range(self.width)]
        self.random_init(0.4,0.3)

    def random_init(self, wdtpercentage, colpercentage):
        no_lines = int(self.height * colpercentage)
        for i in range(no_lines):
            no_randoms = max(int(self.width/3),int(wdtpercentage * (no_lines-2*i)))
            who_to_col = random.choices(range(self.width), k=no_randoms)
            for j in who_to_col:
                self.matrix[i][j].set_col()


    def draw(self,window):

        for x in range(0, self.width):
            for y in range(0, self.height):
                if not self.matrix[x][y].is_clear():
                    self.matrix[x][y].draw(window, calculate_bubble_position(x, y))
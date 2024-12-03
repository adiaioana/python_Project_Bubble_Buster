import pygame

import styles
from styles import colors, getProp, randomItemFrom, darker_colors, ligther_colors, window_size, bubble_window_size

WINDOW_WIDTH, WINDOW_HEIGHT = window_size()

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

class Bubble():
    def __init__(self, state):
        if state == 'clear':
            self.fillcolor = self.contour_color = colors()['background']
        else:
            self.fillcolor,  self.contour_color = randomItemFrom(ligther_colors()), randomItemFrom(darker_colors())
        self.radius = getProp('bubble-radius')

    def is_clear(self):
        return True if self.fillcolor == self.contour_color else False


class Gameboard():
    def __init__(self, np=None):
        self.height, self.width = bubble_window_size()
        self.matrix = np.zeros((self.width, self.height))

        for x in range(0, self.width):
            for y in range(0, self.height):
                self.matrix[x][y] = Bubble('clear')

        for x in range(0, self.width):
            self.matrix[x][x] = Bubble('col')



    def draw(self):
        print('TBD')


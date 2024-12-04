import math

from styles import getGenProp


def calculate_bubble_position(x, y):
    bubradius = getGenProp('bubble-radius')
    xcoord = bubradius + y * 2 * bubradius + (0 if x % 2 == 1 else bubradius)
    ycoord = x * 2 * bubradius + bubradius
    return xcoord, ycoord

def get_line_end(length, angle, pos):
    end_x = pos[0] + length * math.cos(math.radians(angle))
    end_y = pos[1] - length * math.sin(math.radians(angle))
    return end_x, end_y
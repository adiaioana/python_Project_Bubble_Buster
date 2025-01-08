import math  # Import the math module for mathematical functions and calculations

from styles import getGenProp  # Import a utility function to get general properties


def directions_for_pos(i):
    '''
    Calculate the neighbors directions for a bubble in line i
    Args:
        i (int): The row number of the bubble (0-indexed).
    Returns:
        A list containing tuples of direction vectors to be added to a position (i,j)
    '''
    neighbors =[(-1, 0), (0, -1), (0, 1), (1, 0)]
    return neighbors + [(-1, 1),(1, 1)] \
        if i % 2 == 0 else neighbors + [(-1, -1), (1, -1)]

def calculate_bubble_position(x, y):
    """
    Calculate the pixel coordinates of a bubble on the game grid based on its row and column.

    Args:
        x (int): The row number of the bubble (0-indexed).
        y (int): The column number of the bubble (0-indexed).

    Returns:
        tuple: A tuple (xcoord, ycoord) representing the pixel coordinates of the bubble.
    """
    bubradius = getGenProp('bubble-radius')  # Get the radius of the bubbles from a general property
    # Calculate the x-coordinate based on the column number, bubble radius, and row parity (for staggering rows)
    xcoord = bubradius + y * 2 * bubradius + (0 if x % 2 == 1 else bubradius)
    # Calculate the y-coordinate based on the row number and bubble radius
    ycoord = x * 2 * bubradius + bubradius
    return xcoord, ycoord  # Return the calculated coordinates as a tuple

def get_line_end(length, angle, pos):
    """
    Calculate the endpoint of a line given its starting position, length, and angle.

    Args:
        length (float): The length of the line.
        angle (float): The angle of the line in degrees, measured clockwise from the positive x-axis.
        pos (tuple): The starting position of the line as a tuple (x, y).

    Returns:
        tuple: A tuple (end_x, end_y) representing the endpoint of the line.
    """
    # Calculate the x-coordinate of the endpoint using trigonometry
    end_x = pos[0] + length * math.cos(math.radians(angle))
    # Calculate the y-coordinate of the endpoint (subtract because y-coordinates increase downward)
    end_y = pos[1] - length * math.sin(math.radians(angle))
    return end_x, end_y  # Return the calculated endpoint coordinates as a tuple

def wdtcol_percentages_for_level(lvl):
    '''
    Returns the percentage
    :param lvl: The current level (int)
    :return: A tuple of two floats (smaller than 1)
    '''
    wdth_col_percentage_map = {1:(0.4,0.3), 2: (0.5,0.4), 3: (0.6,0.5)}
    if lvl in wdth_col_percentage_map.keys():
        return wdth_col_percentage_map[lvl]
    return (0.6,0.6)
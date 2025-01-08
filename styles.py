import random
import pygame

def getProp(prop):
    """
    Retrieve a predefined property based on its name.

    Args:
        prop (str): The name of the property.

    Returns:
        Various: The value of the requested property.
    """
    prop = prop.replace('_', '-')

    allProps = {
        'font': 'Helvetica',
        'font-size': 20,
        'window-width': 400,
        'margin-left': 10,
        'margin-right': 10,
        'margin-bottom': 10,
        'margin-top': 10,
        'window-height': 600,
        'FPS': 60,
        'bubble-number': 12
    }
    return allProps[prop]

def getGenProp(prop):
    """
    Retrieve dynamically generated properties based on the current window and bubble settings.

    Args:
        prop (str): The name of the property.

    Returns:
        float: The value of the generated property.
    """
    prop = prop.replace('_', '-')
    allGenProps = {
        'bubble-radius': (min(
            (actual_window_size()[0] / (bubble_window_size()[0] + 1)),
            (actual_window_size()[1] / (bubble_window_size()[1] + 1))
        ) / 2)
    }
    return allGenProps[prop]

def bubble_window_size():
    """
    Get the dimensions of the bubble grid in terms of the number of bubbles.

    Returns:
        tuple: A tuple (width, height) representing the grid dimensions.
    """
    return getProp('bubble-number'), getProp('bubble-number')

def actual_window_size():
    """
    Get the actual usable window size after accounting for margins.

    Returns:
        tuple: A tuple (width, height) representing the usable window dimensions.
    """
    return (getProp('window-width') - (getProp('margin-left') + getProp('margin-right')),
            getProp('window-height') - (getProp('margin-bottom') + getProp('margin-top')))

def window_size():
    """
    Get the total window size.

    Returns:
        tuple: A tuple (width, height) representing the total window dimensions.
    """
    return getProp('window-width'), getProp('window-height')

def colors():
    """
    Retrieve a dictionary of predefined color names and their corresponding hex values.

    Returns:
        dict: A dictionary mapping color names to hex values.
    """
    colorsMap = {
        "background": "#B8BEE0",
        "grey": "#738290",
        "white": "#FFFCF7",
        "black": "#0A0908",
        "brown": "#2E282A",
        "purple": "#8b43cc",
        "yellow": "#e8d915",
        "blue": "#A1B5D8",
        "orange": "#F38D68",
        "cyan": "#43b4a4",
        "lightgreen": "#E4F0D0",
        "green": "#C2D8B9",
        "red": "#E5625E",
        "pink": "#FFB8D1"
    }

    return colorsMap

def darker_colors(fromColors):
    """
    Filter and return darker colors from a given dictionary of colors.

    Args:
        fromColors (dict): A dictionary of color names and their hex values.

    Returns:
        list: A list of hex values representing darker colors.
    """
    return [fromColors[col] for col in fromColors.keys() if is_color_dark(fromColors[col])]

def ligther_colors(fromColors):
    """
    Filter and return lighter colors from a given dictionary of colors.

    Args:
        fromColors (dict): A dictionary of color names and their hex values.

    Returns:
        list: A list of hex values representing lighter colors.
    """
    return [fromColors[col] for col in fromColors.keys() if not is_color_dark(fromColors[col])]

def randomItemFrom(someList):
    """
    Select a random item from a list or iterable.

    Args:
        someList (iterable): The list or iterable to select from.

    Returns:
        Various: A random item from the list.
    """
    return random.choice(list(someList))

def hex_to_rgb(hex):
    """
    Convert a hex color string to an RGB tuple.

    Args:
        hex (str): The hex color string.

    Returns:
        tuple: A tuple (R, G, B) representing the RGB values.
    """
    hex = hex if hex.find('#') < 0 else hex[hex.find('#') + 1:]
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    """
    Convert RGB values to a hex color string.

    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).

    Returns:
        str: A hex color string.
    """
    return ('{:02X}' * 3).format(r, g, b)

def gradientRect(window, top_colour, bottom_colour, target_rect):
    """
    Draw a vertical gradient-filled rectangle.

    Args:
        window (pygame.Surface): The Pygame window to draw on.
        top_colour (tuple): RGB color of the gradient's top.
        bottom_colour (tuple): RGB color of the gradient's bottom.
        target_rect (pygame.Rect): The rectangle area to fill.
    """
    colour_rect = pygame.Surface((2, 2))

    pygame.draw.line(colour_rect, top_colour, (0, 0), (1, 0))
    pygame.draw.line(colour_rect, bottom_colour, (0, 1), (1, 1))

    colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.width, target_rect.height))
    window.blit(colour_rect, target_rect)

def draw_background(window):
    """
    Draw a gradient background on the game window.

    Args:
        window (pygame.Surface): The Pygame window.
    """
    background_color = hex_to_rgb(colors()['background'])
    blue_color = hex_to_rgb(colors()['white'])
    gradientRect(window, background_color, blue_color, pygame.Rect(0, 0, window_size()[0], window_size()[1]))

def is_color_dark(hex_color: str) -> bool:
    """
    Determine if a given color is dark based on its luminance.

    Args:
        hex_color (str): The hex color string.

    Returns:
        bool: True if the color is dark, False otherwise.
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0

    def to_linear(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r = to_linear(r)
    g = to_linear(g)
    b = to_linear(b)

    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return luminance < 0.5

def levelK_colors(lvl):
    """
    Select colors for a given level.

    Args:
        lvl (int): The level index.

    Returns:
        dict: A dictionary of selected color names and their hex values.
    """
    allCols = colors()
    allCols.pop('background')
    choose_sum = random.choices(list(allCols.keys()), k=min(4 + lvl, len(list(allCols.keys()))))
    print(f"Chose some colors> {choose_sum}")
    return {col: allCols[col] for col in choose_sum}

def colorForLevel(lvlIndex):
    """
    Get colors for a specific level.

    Args:
        lvlIndex (int): The level index.

    Returns:
        dict: A dictionary of colors for the level.
    """
    return levelK_colors(lvlIndex)

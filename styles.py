import random
import pygame

def getProp(prop):
    prop = prop.replace('_','-')

    allProps = {
        'font':'Helvetica',
        'font-size':20,
        'window-width':600,
        'window-height':800,
        'FPS' : 60,
        'bubble-number':12
    }
    # Auto - generated from previous props
    allProps += {
        'bubble-radius': int( min (
            int( window_size()[0]/(bubble_window_size()[0]+1) ),
            int( window_size()[1]/(bubble_window_size()[1]+1) )
        ) / 2 )
    }

    return allProps[prop]

def bubble_window_size():
    return getProp('bubble-number'), getProp('bubble-number')


def window_size():
    return getProp('window-width'), getProp('window-height')

def colors():
    colorsMap = {
        "background": "#B8BEE0",
        "grey": "#738290",
        "white": "#FFFCF7",
        "black":"#0A0908",
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

def darker_colors():
    return [colors()[col] for col in colors().keys() if is_color_dark(colors()[col])]
def ligther_colors():
    return [colors()[col] for col in colors().keys() if not is_color_dark(colors()[col])]

def randomItemFrom(someList):
    return random.choice(list(someList))

def hex_to_rgb(hex):
    hex=hex if hex.find('#')<0 else hex[hex.find('#')+1:]
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
  return ('{:02X}' * 3).format(r, g, b)


def gradientRect(window, top_colour, bottom_colour, target_rect):
    """Draw a vertical-gradient filled rectangle with RGB colors covering target_rect."""
    colour_rect = pygame.Surface((2, 2))

    pygame.draw.line(colour_rect, top_colour, (0, 0), (1, 0))
    pygame.draw.line(colour_rect, bottom_colour, (0, 1), (1, 1))

    colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.width, target_rect.height))
    window.blit(colour_rect, target_rect)


def draw_background(window):
    """Draw the gradient background."""
    background_color = hex_to_rgb(colors()['background'])
    blue_color = hex_to_rgb(colors()['blue'])
    gradientRect(window, background_color, blue_color, pygame.Rect(0, 0, window_size()[0], window_size()[1]))

def is_color_dark(hex_color: str) -> bool:

    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
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

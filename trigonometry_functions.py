# DON`T ASK ME IT`S FROM ANOTHER PROJECT BUT TRUST ME IT WORKS!!!
import math


def sin_to_a(cosin, sinus):
    a = math.asin(sinus) * 180 / math.pi
    if cosin * sinus > 0:
        if cosin > 0:
            return a
        else:
            return (180 - a) % 360
    elif cosin * sinus == 0:
        if cosin == 0:
            return a
        else:
            return a
    else:
        if cosin > 0:
            return (360 + a) % 360
        else:
            return (180 - a) % 360


def arctan(dx, dy):
    if dy != 0:
        if dx * dy <= 0:
            return math.pi - math.atan(dy / dx)
        else:
            return math.atan(dy / dx)


def point_spin(x, y, alfa, direction):
    if direction != 1:
        dx = math.cos(alfa) * x - math.sin(alfa) * y
        dy = math.sin(alfa) * x + math.cos(alfa) * y
    else:
        dx = math.cos(alfa) * x + math.sin(alfa) * y
        dy = -math.sin(alfa) * x + math.cos(alfa) * y
    ans = (dx, dy)
    return ans

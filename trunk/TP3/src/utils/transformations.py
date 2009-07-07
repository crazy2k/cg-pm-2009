
from math import sin, cos, pi
from numpy import identity, matrix

IDENTITY_3 = identity(3, float)
IDENTITY_4 = identity(4, float)


def translation(xyz):
    x, y, z = xyz
    return matrix([[1, 0, 0, x],
                   [0, 1, 0, y],
                   [0, 0, 1, z],
                   [0, 0, 0, 1]], float)

def rotation(a, axis):
    if axis == 'X':
        return matrix([[1, 0, 0, 0],
                       [0, cos(a), -sin(a), 0],
                       [0, sin(a), cos(a), 0],
                       [0, 0, 0, 1]], float)
    elif axis == 'Y':
        return matrix([[cos(a), 0, sin(a), 0],
                       [0, 1, 0, 0],
                       [-sin(a), 0, cos(a), 0],
                       [0, 0, 0, 1]], float)

    elif axis == 'Z':
        return matrix([[cos(a), -sin(a), 0, 0],
                       [sin(a), cos(a), 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]], float)

        



from math import sin, cos, pi
from numpy import identity, matrix, float64

IDENTITY_3 = identity(3, float64)
IDENTITY_4 = identity(4, float64)

def my_matrix(data):
    return matrix(data, float64)

def translation(xyz):
    x, y, z = xyz
    return my_matrix([[1, 0, 0, x],
                   [0, 1, 0, y],
                   [0, 0, 1, z],
                   [0, 0, 0, 1]])

def rotation(a, axis):
    if axis == 'X':
        return my_matrix([[1, 0, 0, 0],
                       [0, cos(a), -sin(a), 0],
                       [0, sin(a), cos(a), 0],
                       [0, 0, 0, 1]])
    elif axis == 'Y':
        return matrix([[cos(a), 0, sin(a), 0],
                       [0, 1, 0, 0],
                       [-sin(a), 0, cos(a), 0],
                       [0, 0, 0, 1]], float)

    elif axis == 'Z':
        return my_matrix([[cos(a), -sin(a), 0, 0],
                       [sin(a), cos(a), 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]])

def degree2radians(degree):
    return degree*pi/180
        
def twodseq_to_4x1vector(seq):
    """Transform a two-dimensional sequence into a 4x1 matrix. The third
    coordinate is set to 0, and the fourth to 1."""
    point = (seq[0], seq[1], 0, 1)
    m = my_matrix(point)
    return m.transpose()

def threedseq_to_4x1vector(seq):
    """Transform a three-dimensional sequence into a 4x1 matrix. The fourth
    coordinate is set 1."""
    point = (seq[0], seq[1], seq[2], 1)
    m = my_matrix(point)
    return m.transpose()

def int_col_to_fp(col):
    return tuple([float(x)/255 for x in col])

def fp_col_to_int(col):
    return tuple([int(x*255) for x in col])

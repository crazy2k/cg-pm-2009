
IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

def transformed_point(point, transformation):
    v = (point[0], point[1], 1)
    result = [0]*3

    for i in range(3):
        result[i] = multiply_vectors(transformation[i], v)

    return result[:2]

def multiply_vectors(v1, v2):
     return int(round(v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2])) 

def multiply_matrices(m1, m2):
    m3 = [[0,0,0],[0,0,0],[0,0,0]]
    for i in range(3):
        for j in range(3):
            columna_j = [m2[x][j] for x in range(3)]
            m3[i][j] = multiply_vectors(m1[i], columna_j)
    return m3

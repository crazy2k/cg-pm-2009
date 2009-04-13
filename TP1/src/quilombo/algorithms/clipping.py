
class ViewPort:
    def __init__(self, refpoint, width, height):
        self.refpoint = refpoint
        self.width = width
        self.height = height

def clip(viewport, vertices):
    rp = viewport.refpoint
    width = viewport.width
    height = viewport.height
    vertices = clipping(vertices, (rp, (rp[0] + width, rp[1])))
    vertices = clipping(vertices, ((rp[0] + width, rp[1]),
        (rp[0] + width, rp[1] + height)))
    vertices = clipping(vertices, ((rp[0] + width, rp[1] + height),
        (rp[0], rp[1] + height)))
    vertices = clipping(vertices, ((rp[0], rp[1] + height), rp))

    return vertices
    

def clipping(vertices, boundary):
    """polpoints es la lista de puntos del poligono; se encuentra ordenada."""
    vertices_out = []
    for i in range(len(vertices)):
        p = vertices[i]
        pnext = vertices[(i+1) % len(vertices)]
        if is_inside(pnext, boundary):
            if is_inside(p, boundary):
                vertices_out.append(pnext)
            else:
                inter = intersection(boundary, p, pnext)
                vertices_out.append(inter)
                vertices_out.append(pnext)
        elif is_inside(p, boundary):
            inter = intersection(boundary, p, pnext)
            vertices_out.append(inter)
    return vertices_out


def intersection(boundary, p1, p2):

    x1, y1 = boundary[0][0], boundary[0][1]
    x2, y2 = boundary[1][0], boundary[1][1]

    x3, y3 = p1[0], p1[1]
    x4, y4 = p2[0], p2[1]
   
    x12 = x1 - x2
    x34 = x3 - x4
    y12 = y1 - y2
    y34 = y3 - y4

    c = x12 * y34 - y12 * x34

    a = x1 * y2 - y1 * x2;
    b = x3 * y4 - y3 * x4;

    x = float(a * x34 - b * x12) / c;
    y = float(a * y34 - b * y12) / c;

    return (int(round(x)), int(round(y)))


# boundary es la frontera de cliping, representada por los vertices de ese
# lado de derecha a izquierda
def is_inside(point, boundary):
    px = point[0]
    py = point[1]
    b1x = boundary[0][0]
    b1y = boundary[0][1]
    b2x = boundary[1][0]
    b2y = boundary[1][1]
    if b1x == b2x: # linea vertical
        if b2y > b1y: # linea hacia abajo
            return px <= b1x
            
        else: # linea hacia arriba
            return px >= b1x

    else: # linea horizontal
        if b2x > b1x: # linea hacia la derecha
            return py >= b1y
            
        else: # linea hacia la izquierda
            return  py <= b1y
            




class ViewPort:
    def __init__(self, refpointx, refpointy, width, height):
        self.refpointx = refpointx
        self.refpointy = refpointy
        self.width = width
        self.height = height


def clip(viewport, polpoints):
    """polpoints es la lista de puntos del poligono; se encuentra ordenada."""
    polpoints_c = polpoints[:]
    for i in range(len(polpoints_c)):
        p = polpoints_c[i]
        pnext = polpoints_c[i+1]
        if is_in_viewport(viewport, p[0], p[1]) and \
            not is_in_viewport(viewport, pnext[0], pnext[1]):

            pi = intersection(viewport, p[0], p[1], pnext[0], pnext[1])
            polpoints_c[i+1] = pi
        elif not is_in_viewport(viewport, p[0], p[1]) and \
            is_in_viewport(viewport, pnext[0], pnext[1]):
            
            pi = intersection(viewport, p[0], p[1], pnext[0], pnext[1])
            polpoints_c[i] = pi
    
    newpolpoints = polpoints_c[:]
    for p in polpoints_c:
        if is_in_viewport(viewport, p[0], p[1]):
            newpolpoints.add(p)

    return newpolpoints
        
#def intersection(viewport, px1, py1, px2, py2):
#    pass


def intersection(px1, py1, px2, py2, px3, py3, px4, py4):
    a = px3 - px4 - px1 + px2
    c = px1 - px3
    
    x = c/a
    
    y = (px1 - px2)*x + px1

    return (x, y) 

def is_in_viewport(viewport, px, py):
    return px > refpointx and px < refpointx + width and py > refpointy and \
        py < refpointy + height


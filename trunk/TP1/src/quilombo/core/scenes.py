from algorithms.scan import PolygonScanAlgorithm
from utils.transformations import transformed_point
from algorithms.windowing import WindowingMatrix

from algorithms import bresenham, clipping, curvas

class Scene:

    def transform(self, transformation):
        raise NotImplementedError

    def get_colour(self):
        return self.colour

    def set_colour(self, colour):
        self.colour = colour
        
    def window(self, old_viewport, new_viewport):
        self.transform(WindowingMatrix(old_viewport, new_viewport))

class CompositeScene(Scene):
    
    def __init__(self):
        self.__children = []
        # si el color es None, entonces el color dependera de las
        # escenas children
        self.colour = None

    def set_colour(self, colour):
        Scene.set_colour(self, colour)
        for s in self.__children:
            s.colour = colour

    def add_child(self, child):
        self.__children.append(child)
        
    def draw(self, putpixel):
        for s in self.__children:
            s.draw(putpixel)

    def transform(self, transformation):
        for s in self.__children:
            s.transform(transformation)
            
    def window(self, old_viewport, new_viewport):
        for s in self.__children:
            s = s.window(old_viewport, new_viewport)

    def clip(self, viewport):
        for s in self.__children:
            s = s.clip(viewport)

    def imprimite(self):
        for s in self.__children:
            s.imprimite()

class LineSegment(Scene):
    def __init__(self, endpoint1, endpoint2,
        draw_segment_function = bresenham.draw_segment, colour = (0, 0, 0)):

        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2
        self.colour = colour
        self.draw_segment = draw_segment_function
        

    def draw(self, putpixel):
        endpoint1 = self.endpoint1
        endpoint2 = self.endpoint2

        self.draw_segment(endpoint1, endpoint2, putpixel,
            self.colour)

    def transform(self, transformation):
        self.endpoint1 = transformed_point(self.endpoint1, transformation)
        self.endpoint2 = transformed_point(self.endpoint2, transformation)

class Polygon(Scene):
    def __init__(self, vertices, colour = (0, 0, 0)):
        self.vertices = vertices
        self.colour = colour

    def draw(self, putpixel):
        if len(self.vertices) == 0:
            return
        algorithm = PolygonScanAlgorithm()
        algorithm.scan(self.vertices, bresenham.draw_segment, putpixel, self.colour)

    def transform(self, transformation):
        for i in range(len(self.vertices)):
            self.vertices[i] = transformed_point(self.vertices[i],
                transformation)

    def clip(self, viewport):
        self.vertices = clipping.clip(viewport, self.vertices)

    def imprimite(self):
        print self.vertices


class Curve(Scene):
    def __init__(self, control_points, algorithm = bresenham, draw_cp = True):
        self.c_points = control_points
        self.algorithm = algorithm

    def draw(self, putpixel):
        b_size = (3, 3)
        alter_size = lambda p: [p[0] - b_size[0]/2, p[1] - b_size[1]/2]
        cs = CompositeScene()
        for p in self.c_points:
            p = alter_size(p)
            pol = Polygon([(p[0], p[1]), (p[0] + b_size[0], p[1]),
                (p[0] + b_size[0], p[1] + b_size[1]),
                (p[0], p[1] + b_size[1])], (255, 0, 0))
            cs.add_child(pol)
        cs.draw(putpixel)

        

class BezierCurve(Curve):
    def __init__(self, control_points, algorithm = bresenham):
        Curve.__init__(self, control_points, algorithm)

    def draw(self, putpixel):
        Curve.draw(self, putpixel)
        curvas.Bezier(self.c_points, 100, self.algorithm.draw_segment,
            putpixel)


class NotUniformBSplineCurve(Curve):
    def __init__(self, control_points, knots, algorithm = bresenham):
        Curve.__init__(self, control_points, algorithm)
        self.knots = knots

    def draw(self, putpixel):
        Curve.draw(self, putpixel)
        curvas.bsplines_no_uniforme(self.c_points, self.knots, 50, len(self.knots) - len(self.c_points),
            self.algorithm.draw_segment, putpixel)


class BSplineCurve(Curve):
    def __init__(self, control_points, algorithm = bresenham):
        Curve.__init__(self, control_points, algorithm)

    def draw(self, putpixel):
        Curve.draw(self, putpixel)
        curvas.bsplines(self.c_points, 50, self.algorithm.draw_segment,
            putpixel)


class PolyBezierCurve(Curve):
    def __init__(self, control_points, algorithm = bresenham):
        Curve.__init__(self, control_points, algorithm)

    def draw(self, putpixel):
        Curve.draw(self, putpixel)
        curvas.BezierMenorGrado(self.c_points, 100,
        self.algorithm.draw_segment, putpixel)

    

from algorithms.scan import PolygonScanAlgorithm
from utils.transformations import transformed_point
from algorithms.windowing import WindowingMatrix

from algorithms import bresenham, clipping

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

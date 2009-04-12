from algorithms.bresenham import draw_segment
from algorithms.scan import PolygonScanAlgorithm
from utils.transformations import transformed_point

class Scene:

    def transform(self, transformation):
        raise NotImplementedError

    def get_colour(self):
        return self.colour

    def set_colour(self, colour):
        self.colour = colour

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


class LineSegment(Scene):
    def __init__(self, endpoint1, endpoint2):
        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2
        self.colour = (0, 0, 0)
        

    def draw(self, putpixel):
        endpoint1 = self.endpoint1
        endpoint2 = self.endpoint2

        draw_segment(endpoint1, endpoint2, putpixel, self.colour)

    def transform(self, transformation):
        self.endpoint1 = transformed_point(self.endpoint1, transformation)
        self.endpoint2 = transformed_point(self.endpoint2, transformation)

class Triangle(Scene):
    def __init__(self, vertex1, vertex2, vertex3, colour = (0, 0, 0)):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3
        self.colour = colour

    def draw(self, putpixel):
        algorithm = PolygonScanAlgorithm()

        algorithm.scan([self.vertex1, self.vertex2, self.vertex3],
            draw_segment, putpixel, self.colour)

    def transform(self, transformation):
        self.vertex1 = transformed_point(self.vertex1, transformation)
        self.vertex2 = transformed_point(self.vertex2, transformation)
        self.vertex3 = transformed_point(self.vertex3, transformation)

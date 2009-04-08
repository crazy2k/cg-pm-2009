from algorithms.bresenham import draw_segment
from algorithms.scan import TriangleScanAlgorithm

class CompositeScene:
    def __init__(self):
        self.__children = []

    def draw(self, putpixel):
        for s in __children:
            s.draw(putpixel)

    def add_child(self, child):
        self.__children.append(child)

        
class LineSegment:
    def __init__(self, endpoint1, endpoint2):
        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2

    def draw(self, putpixel):
        endpoint1 = self.endpoint1
        endpoint2 = self.endpoint2

        draw_segment(endpoint1, endpoint2, putpixel)

class Triangle:
    def __init__(self, vertex1, vertex2, vertex3):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3

        self.colour = (0, 0, 0)

    def draw(self, putpixel):
        algorithm = TriangleScanAlgorithm()

        algorithm.scan(self.vertex1, self.vertex2, self.vertex3,
            draw_segment, putpixel)

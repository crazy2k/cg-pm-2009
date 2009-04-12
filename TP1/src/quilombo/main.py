import wx
from windows import GenericWindow

import random
from scenes import CompositeScene, Triangle

from utils import transformations

import time
import copy
from algorithms import scan
from algorithms import bresenham

import clipping

class PolygonWindow(GenericWindow):
    
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Poligono", size,
            GenericWindow.AUTO_REFRESHING)
    
    def draw(self, putpixel):
        algorithm = scan.PolygonScanAlgorithm()
        #algorithm.scan([(10,10), (100,50), (120,70), (120,100)], bresenham.draw_segment, putpixel, (0, 0, 0))
        vertices = [(10,10), (100,50), (120,70), (120,100)]
        vertices = clipping.clip(clipping.ViewPort((40,30), 40, 20), vertices)
        algorithm.scan(vertices, bresenham.draw_segment, putpixel, (0, 0, 0))
        


class SnowWindow(GenericWindow):

    BALLS = 30
    
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Nieve", size,
            GenericWindow.AUTO_REFRESHING)
            
        # creacion de la bola
        self.__ball = CompositeScene()
        
        small_ball = CompositeScene()

        tr1 = Triangle((-2, 1), (0, -2), (2, 1))
        small_ball.add_child(tr1)

        tr2 = Triangle((-2, 1), (0, -2), (2, 1))
        t_rotate = [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]
        tr2.transform(t_rotate)
        small_ball.add_child(tr2)

        small_ball.set_colour((226, 225, 255))
        
        big_ball = copy.deepcopy(small_ball)  
        big_ball.set_colour((133, 131, 203))
        t_bigger = [[2, 0, 0], [0, 2, 0], [0, 0, 1]]
        big_ball.transform(t_bigger)
        
        self.__ball.add_child(big_ball)
        self.__ball.add_child(small_ball)
        
        # fin

        self.__yes = [random.randint(0, 500) for x in range(self.BALLS)]
        
        self.__t_down = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        
        self.__history = [transformations.IDENTITY]*self.BALLS
        
        self.__p = 0       
        self.__y = 0
        self.__a = 0

        self.__frames = 1

    def draw(self, putpixel):
        t_rotate = [[0.866025403784439, 0.5, 0], [-0.5, 0.866025403784439, 0], [0, 0, 1]]
        self.__ball.transform(t_rotate)
        ball = copy.deepcopy(self.__ball)
        t_move = [[1, 0, 80], [0, 1, 80], [0, 0, 1]]
        ball.transform(t_move)
        self.__t_down = [[1, 0, 0], [0, 1, self.__y], [0, 0, 1]] 
        ball.transform(self.__t_down)
        
        balls = []
        for x in range(self.BALLS):
            balls.append(copy.deepcopy(ball))
        
        t_pos = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.scene = CompositeScene()
        i = 0
        for b in balls:
            b.transform(t_pos)

            t_pos[0][2] = t_pos[0][2] + 35
            t_pos[1][2] = self.__yes[i]
            
            if self.__a == 0:
                r = random.randint(0,1)
                if r == 0:
                    t_dance = [[1, 0, 1], [0, 1, 0], [0, 0, 1]]
                else:
                    t_dance = [[1, 0, -1], [0, 1, 0], [0, 0, 1]]
            else:           
                 t_dance = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                 
            self.__history[i] = transformations.multiply_matrices(t_dance,
                self.__history[i])
                
            b.transform(self.__history[i])
            self.__p = (self.__p + 1) % 50
            self.scene.add_child(b)
            i = i + 1
        scene_big_balls = copy.deepcopy(self.scene)
        t_bigger = [[2, 0, 0], [0, 2, 0], [0, 0, 1]]
        scene_big_balls.transform(t_bigger)
        self.scene.add_child(scene_big_balls)

        #if self.__frames > 10:
           # pol = Polygon([


        self.scene.draw(putpixel)

        self.__y = self.__y + 1
        self.__frames = self.__frames + 1
        
class OurWindow(GenericWindow):
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Nuestra escena", size,
            GenericWindow.AUTO_REFRESHING)

        self.__r = 0
        self.__g = 0
        self.__b = 0

        self.__dr = 1
        self.__dg = -1
        self.__db = 1

        self.__tr = Triangle((200, 300), (250, 200), (300, 300))
        self.__t = [[1, 0, 1], [0, 1, -1], [0, 0, 1]]

    def draw(self, putpixel):

        tr = self.__tr

        t = self.__t

        
        scene = CompositeScene()

        scene.add_child(tr)

        if self.__r == 255:
            self.__dr = -1
        if self.__g == 255:
            self.__dg = -1
        if self.__b == 255:
            self.__db = -1

        if self.__r == 0:
            self.__dr = 1
        if self.__g == 0:
            self.__dg = 1
        if self.__b == 0:
            self.__db = 1

        v = random.randint(0, 2)
        if v == 0:
            self.__r = self.__r + self.__dr
        elif v == 1:
            self.__g = self.__g + self.__dg
        elif v == 2:
            self.__b = self.__b + self.__db

        
        tr.colour = (self.__r, self.__g, self.__b)
        tr.transform(self.__t)

        if tr.vertex2[1] == 0:
            self.__t[1] = [0, 1, 1]
            print time.time()
        if tr.vertex3[0] == self.GetSize().Get()[0] - 1:
            self.__t[0] = [1, 0, -1]
            print time.time()
        if tr.vertex1[0] == 0:
            self.__t[0] = [1, 0, 1]
            print time.time()
        if tr.vertex3[1] == self.GetSize().Get()[1] - 1:
            self.__t[1] = [0, 1, -1]
            print time.time()

        scene.draw(putpixel)


if __name__ == "__main__":
    app = wx.App()
    #OurWindow((500, 600))
    SnowWindow((500, 300))
    #PolygonWindow((800, 600))
    app.MainLoop()

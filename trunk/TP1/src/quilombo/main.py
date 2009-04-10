import wx
from windows import GenericWindow

import random
from scenes import CompositeScene, Triangle

from utils import transformations

import time
import copy

class SnowWindow(GenericWindow):
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Nieve", size,
            GenericWindow.AUTO_REFRESHING)
            
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
        
        #balls = []
        #for x in range(20):
        #    balls.append(copy.deepcopy(self.__ball))
        
        #t_pos = [[1, 0, 30], [0, 1, 0], [0, 0, 1]]
        #self.scene = CompositeScene()
        #for b in balls:
        #    t_pos[0][2] = t_pos[0][2] + 30
        #    b.transform(t_pos)
        #    self.scene.add_child(b)
        
        self.__t_down = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        
        self.__p = 0  
        self.__a = 0     
        self.__y = 0

    def draw(self, putpixel):
        
        t_rotate = [[0.866025404, 0.5, 0], [-0.5, 0.866025404, 0], [0, 0, 1]]
        self.__ball.transform(t_rotate)
        ball = copy.deepcopy(self.__ball)
        t_bigger = [[3, 0, 0], [0, 3, 0], [0, 0, 1]]
        ball.transform(t_bigger)
        t_move = [[1, 0, 80], [0, 1, 80], [0, 0, 1]]
        ball.transform(t_move)
        self.__t_down = [[1, 0, 0], [0, 1, self.__y], [0, 0, 1]] 
        ball.transform(self.__t_down)
        
        if True: #self.__p == 0:
            #self.__a = (self.__a + 1) % 5
            if self.__a == 0:
                r = random.randint(0,1)
                if r == 0:
                    self.__t_dance = [[1, 0, 1], [0, 1, 0], [0, 0, 1]]
                else:
                    self.__t_dance = [[1, 0, -1], [0, 1, 0], [0, 0, 1]]
            else:           
                self.__t_dance = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        ball.transform(self.__t_dance)
        self.__p = (self.__p + 1) % 50
        
        ball.draw(putpixel)
        self.__y = self.__y + 1
        
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
    SnowWindow((800, 600))
    app.MainLoop()

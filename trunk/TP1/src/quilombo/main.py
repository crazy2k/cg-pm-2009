import wx
import random
import time
import copy

from core.windows import GenericWindow
from core.scenes import CompositeScene, Polygon

from utils import transformations
from algorithms import scan, bresenham, clipping

class SnowWindow(GenericWindow):

    # numero de bolas que tendran movimiento independiente de las demas
    BALLS = 30
    # frame a partir del cual se comienza a mostrar el poligono que se
    # recorta
    POLYGON_START_AT = 10

    def __create_small_ball(self):
        small_ball = CompositeScene()

        tr1 = Polygon([(-2, 1), (0, -2), (2, 1)])
        small_ball.add_child(tr1)

        tr2 = Polygon([(-2, 1), (0, -2), (2, 1)])
        t_rotate = [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]
        tr2.transform(t_rotate)
        small_ball.add_child(tr2)

        small_ball.set_colour((226, 225, 255))

        return small_ball
 
    def __create_big_ball(self, small_ball):
        big_ball = copy.deepcopy(small_ball)  
        big_ball.set_colour((133, 131, 203))

        t_bigger = [[2, 0, 0], [0, 2, 0], [0, 0, 1]]
        big_ball.transform(t_bigger)
        return big_ball

    
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Nieve", size,
            GenericWindow.AUTO_REFRESHING)
            
        # creacion de la bola/estrella compuesta (la que se ve cayendo por
        # toda la pantalla); consta de dos bolas/estrellas: una chica, y una
        # grande
        self.__ball = CompositeScene()
        
        small_ball = self.__create_small_ball()
        big_ball = self.__create_big_ball(small_ball)

        # ambas bolas forman la bola compuesta
        self.__ball.add_child(big_ball)
        self.__ball.add_child(small_ball)
        

        # valores de y en los que se ubicaran las bolas
        self.__yes = [random.randint(0, 500) for x in range(self.BALLS)]
        
        self.__t_down = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        
        self.__history = [transformations.IDENTITY]*self.BALLS
        
        self.__p = 0       
        self.__y = 0
        self.__a = 0

        self.__pr = 255
        self.__pg = 255
        self.__pb = 255

        self.__pdr = -2
        self.__pdg = -2
        self.__pdb = -1

        self.__clip_height = 65


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

        if self.__frames > self.POLYGON_START_AT:
            pol_colour = (self.__pr, self.__pg, self.__pb)

            self.__polv = [(-2, -1), (-0.75, -1), (0, -2), (0.75, -1),
                (2, -1), (1.25, 0), (2, 1), (0.75, 1), (0, 2), (-0.75, 1),
                (-2, 1), (-1.25, 0)]
            pol = Polygon(self.__polv, pol_colour)

            t_bigger = [[20, 0, 0], [0, 20, 0], [0, 0, 1]]
            pol.transform(t_bigger)

            size = self.GetSize().Get()
            t_move = [[1, 0, size[0]/2], [0, 1, size[1]/2], [0, 0, 1]]
            pol.transform(t_move)

            self.scene.add_child(pol)

            if self.__pb > 200:
                self.__pr = self.__pr + self.__pdr
                self.__pg = self.__pg + self.__pdg
                self.__pb = self.__pb + self.__pdb

            elif self.__clip_height > 0:
                pol.vertices = clipping.clip(clipping.ViewPort((210, 110), 200,
                    self.__clip_height), self.__polv)
                self.__clip_height = self.__clip_height - 1

                if self.__clip_height == 1:
                    self.__pr = 255
                    self.__pg = 255
                    self.__pb = 255
                    self.__clip_height = 65

        self.scene.draw(putpixel)

        self.__y = self.__y + 1
        self.__frames = self.__frames + 1
        

if __name__ == "__main__":
    app = wx.App()
    SnowWindow((500, 300))
    app.MainLoop()

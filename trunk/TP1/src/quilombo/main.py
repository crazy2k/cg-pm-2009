import wx
import random
import time
import copy

from core.windows import GenericWindow
from core.scenes import CompositeScene, Polygon

from utils import transformations
from algorithms import scan, bresenham, clipping

from core.scenes import LineSegment
from algorithms import dda


class ComparationWindow(GenericWindow):
    
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Comparacion - Bresenham vs DDA",
            size, GenericWindow.STATIC)

    def draw(self, putpixel):
        seg1 = LineSegment((10, 10), (10, 50), bresenham.draw_segment)
        seg2 = LineSegment((50, 10), (50, 50), dda.draw_segment)

        seg1.draw(putpixel)
        seg2.draw(putpixel)

        seg3 = LineSegment((10, 110), (50, 110), bresenham.draw_segment)
        seg4 = LineSegment((10, 150), (50, 150), dda.draw_segment)

        seg3.draw(putpixel)
        seg4.draw(putpixel)

        seg5 = LineSegment((10, 250), (50, 210), bresenham.draw_segment)
        seg6 = LineSegment((60, 250), (100, 210), dda.draw_segment)

        seg5.draw(putpixel)
        seg6.draw(putpixel)

        seg7 = LineSegment((10, 350), (50, 349), bresenham.draw_segment)
        seg8 = LineSegment((60, 350), (100, 349), dda.draw_segment)

        seg7.draw(putpixel)
        seg8.draw(putpixel)

        seg9 = LineSegment((10, 450), (30, 390), bresenham.draw_segment)
        seg10 = LineSegment((60, 450), (80, 390), dda.draw_segment)

        seg9.draw(putpixel)
        seg10.draw(putpixel)

        seg11 = LineSegment((210, 500), (300, 502), bresenham.draw_segment)
        seg12 = LineSegment((360, 500), (450, 502), dda.draw_segment)

        seg11.draw(putpixel)
        seg12.draw(putpixel)


class SnowWindow(GenericWindow):

    # numero de bolas que tendran movimiento independiente de las demas
    BALLS = 30
    # frame a partir del cual se comienza a mostrar el poligono que se
    # recorta
    POLYGON_START_AT = 10
    
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Nieve", size,
            GenericWindow.AUTO_REFRESHING)

        self.__ball = CompositeScene()
        
        small_ball = self.__create_small_ball()
        big_ball = self.__create_big_ball(small_ball)

        self.__ball.add_child(big_ball)
        self.__ball.add_child(small_ball)
        
        self.__initialize_variables()

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
        
    def __initialize_variables(self):
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

        self.__clip = 80
        self.__h = 0

        self.__frames = 1

    def draw(self, putpixel):
        self.__prepare_winter_scene()
        self.__prepare_clipping_scene()        
        self.__scene.draw(putpixel)

    def __prepare_winter_scene(self):
        ball = self.__rotate_original_ball()
        self.__multiply_and_dance_original_ball(ball)
        self.__add_bigger_balls()

    def __rotate_original_ball(self):
        t_rotate = [[0.866025403784439, 0.5, 0], [-0.5, 0.866025403784439, 0],
            [0, 0, 1]]
        self.__ball.transform(t_rotate)
        ball = copy.deepcopy(self.__ball)
        t_move = [[1, 0, 80], [0, 1, 80], [0, 0, 1]]
        ball.transform(t_move)
        self.__t_down = [[1, 0, 0], [0, 1, self.__y], [0, 0, 1]] 
        ball.transform(self.__t_down)
        return ball

    def __multiply_and_dance_original_ball(self, ball):
        balls = []
        for x in range(self.BALLS):
            balls.append(copy.deepcopy(ball))
        
        t_pos = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.__scene = CompositeScene()
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
            self.__scene.add_child(b)
            i = i + 1
        self.__y = self.__y + 1
        
    def __add_bigger_balls(self):
        scene_big_balls = copy.deepcopy(self.__scene)
        t_bigger = [[2, 0, 0], [0, 2, 0], [0, 0, 1]]
        scene_big_balls.transform(t_bigger)
        self.__scene.add_child(scene_big_balls)

    def __prepare_clipping_scene(self):
        if self.__frames > self.POLYGON_START_AT:
            star = self.__prepare_star()

            if self.__pb > 200:
                self.__change_star_color()

            elif self.__clip > 0:
                self.__clip_star(star)
        
        self.__frames = self.__frames + 1
    
    def __prepare_star(self):
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

        self.__scene.add_child(pol)
        return pol
            
    def __change_star_color(self):
        self.__pr = self.__pr + self.__pdr
        self.__pg = self.__pg + self.__pdg
        self.__pb = self.__pb + self.__pdb
    
    def __clip_star(self, pol):
        vp = clipping.ViewPort((210 + self.__h, 110 + self.__h), self.__clip,
            self.__clip)
        pol.vertices = clipping.clip(vp, self.__polv)
        
        self.__clip = self.__clip - 2
        self.__h = self.__h + 1

        if self.__clip == 2:
            self.__pr = 255
            self.__pg = 255
            self.__pb = 255
            self.__clip = 80
            self.__h = 0
            
if __name__ == "__main__":
    app = wx.App()
    SnowWindow((500, 300))
    #ComparationWindow((800, 600))
    app.MainLoop()

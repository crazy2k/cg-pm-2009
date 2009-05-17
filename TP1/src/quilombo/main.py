import wx
import random
import time
import copy
import cPickle
import weakref

from core.windows import GenericWindow, ViewPort
from core.scenes import CompositeScene, Polygon

from utils import transformations
from algorithms import scan, bresenham, clipping, windowing

from core.scenes import LineSegment
from algorithms import dda, curvas



class ComparationWindow(GenericWindow):
    
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Comparacion - Bresenham vs DDA",
            size, GenericWindow.STATIC)
        self.CreateMenu()
    
    def CreateMenu(self):
        self.__algorithm = ""
        menu = wx.Menu()
        menu.Append(1, "Bezier")
        menu.AppendSeparator()
        menu.Append(2, "B-Spline Uniforme")
        menu.AppendSeparator()
        menu.Append(3, "B-Spline No Uniforme")
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "Algoritmo")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.menuBezier, id=1)
        self.Bind(wx.EVT_MENU, self.menuBSplineUniforme, id=2)
        self.Bind(wx.EVT_MENU, self.menuBSplineNoUniforme, id=3)
        
    def menuBezier(self, event):
        self.__algorithm = "Bezier"
        self.Refresh()
    
    def menuBSplineUniforme(self, event):
        self.__algorithm = "BSplineUniforme"
        self.Refresh()
    
    def menuBSplineNoUniforme(self, event):
        self.__algorithm = "BSplineNoUniforme"
        self.Refresh()
    
    def draw(self, putpixel):

        if False:
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

            seg13 = LineSegment((30, 550), (10, 490), bresenham.draw_segment)
            seg14 = LineSegment((80, 550), (60, 490), dda.draw_segment)

            seg13.draw(putpixel)
            seg14.draw(putpixel)
               
        LineSegment((400,0),(550,550), dda.draw_segment, (255,0, 0)).draw(putpixel)
        LineSegment((550,550),(660,0), dda.draw_segment, (255,0, 0)).draw(putpixel)
        LineSegment((660,0),(700,510), dda.draw_segment, (255,0, 0)).draw(putpixel)
        LineSegment((700,510),(750,10), dda.draw_segment, (255,0, 0)).draw(putpixel)

        self.button1 = wx.Button(self, id=-1, label='Button1', pos=(396, 0), size=(8, 8))
        self.button1.Bind(wx.EVT_BUTTON, self.buttonClick(self.button1))
        self.button2 = wx.Button(self, id=-1, label='Button2', pos=(546, 550), size=(8, 8))
        self.button2.Bind(wx.EVT_BUTTON, self.buttonClick(self.button2))
        self.button3 = wx.Button(self, id=-1, label='Button3', pos=(656, 0), size=(8, 8))
        self.button3.Bind(wx.EVT_BUTTON, self.buttonClick(self.button3))
        self.button4 = wx.Button(self, id=-1, label='Button4', pos=(696, 510), size=(8, 8))
        self.button4.Bind(wx.EVT_BUTTON, self.buttonClick(self.button4))
        self.button5 = wx.Button(self, id=-1, label='Button5', pos=(746, 10), size=(8, 8))
        self.button5.Bind(wx.EVT_BUTTON, self.buttonClick(self.button5))
        
        if (self.__algorithm == "Bezier"):
            curvas.Bezier([[400,0],[550,550],[660,0],[700,510],[750,10]], 1000, bresenham.draw_segment, putpixel)
        elif(self.__algorithm == "BSplineUniforme"):
            curvas.bsplines([[400,0],[550,550],[660,0],[700,510],[750,10]], 1000, bresenham.draw_segment, putpixel)
        elif (self.__algorithm == "BSplineNoUniforme"):
            curvas.bsplines_no_uniforme([[400,0],[550,550],[660,0],[700,510],[750,10]], 1000, 3, bresenham.draw_segment, putpixel)
    
    def buttonClick(self, button):
        dataobject = wx.CustomDataObject(wx.CustomDataFormat("MySpecialData"))
        dataobject.SetData("")
        dragSource = wx.DropSource(button)
        dragSource.SetData(dataobject)
        dragSource.DoDragDrop(wx.Drag_DefaultMove)

class SnowWindow(GenericWindow):

    # numero de bolas que tendran movimiento independiente de las demas
    BALLS = 20
    # frame a partir del cual se comienza a mostrar el poligono que se
    # recorta
    POLYGON_START_AT = 20
    
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

        size = self.GetSize().Get()
        self.__initial_vp = ViewPort((0,0), size[0], size[1])

    def draw(self, putpixel):
        self.__prepare_winter_scene()
        self.__prepare_clipping_scene()

        #vp = ViewPort((1000, 1000), 1100, 1100)
        vp = ViewPort((-100, -100), 800, 300)
        self.__scene.clip(vp)
        #self.__scene.imprimite()


        self.__scene.window(vp, self.__initial_vp)
        self.__scene.window(self.__initial_vp, self.__new_vp)


        self.__scene.draw(putpixel)

    def on_size(self, event):
        new_size = event.GetSize()

        self.__new_vp = ViewPort((0, 0), new_size[0], new_size[1])

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

            t_pos[0][2] = t_pos[0][2] + 25
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
        #scene_big_balls = copy.deepcopy(self.__scene)
        #t_bigger = [[2, 0, 0], [0, 2, 0], [0, 0, 1]]
        #scene_big_balls.transform(t_bigger)
        #self.__scene.add_child(scene_big_balls)
        pass

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

        w, h = self.__initial_vp.width, self.__initial_vp.height
        t_move = [[1, 0, w/2], [0, 1, h/2], [0, 0, 1]]
        pol.transform(t_move)

        self.__scene.add_child(pol)
        return pol
            
    def __change_star_color(self):
        self.__pr = self.__pr + self.__pdr
        self.__pg = self.__pg + self.__pdg
        self.__pb = self.__pb + self.__pdb
    
    def __clip_star(self, pol):

        w, h = self.__initial_vp.width, self.__initial_vp.height

        vp = clipping.ViewPort((w/2 - 40 + self.__h, h/2 - 40 + self.__h), self.__clip,
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
    #SnowWindow((800, 300))
    ComparationWindow((800, 600))
    app.MainLoop()

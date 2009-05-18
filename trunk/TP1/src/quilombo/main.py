import wx
import random
import time
import copy

import traceback

from core.windows import GenericWindow, ViewPort
from core.scenes import CompositeScene, Polygon

from utils import transformations
from algorithms import scan, bresenham, clipping, windowing

from core.scenes import LineSegment
from algorithms import dda, curvas



class MyButton(wx.Button):
    def __init__(self, window, id, label, pos, size, point):
        wx.Button.__init__(self, window, id, label, pos, size)

        self.id = id
        self.window = window

        wx.EVT_LEFT_DOWN(self, self.on_mouse_down)
        wx.EVT_RIGHT_DOWN(self, self.on_mouse_right_down)


    def on_mouse_right_down(self, event):
        if self.window.being_dragged == None:
            del(self.window.c_points[self.id])
            self.window.Refresh()

    def on_mouse_down(self, event):
        if self.window.being_dragged == None:
            self.window.being_dragged = self.id
        else:
            self.window.being_dragged = None


class CurvesWindow(GenericWindow):
    
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Trabajo Practico de Curvas",
            size, GenericWindow.STATIC)

        wx.EVT_MOTION(self, self.on_mouse_move)
        wx.EVT_LEFT_DOWN(self, self.on_mouse_down)

        self.create_menu()

        #self.c_points = [[100,100],[150,80],[200,100], [200,150], [150,180],[100,150],[100,100],[150,80],[200,100], [200,150], [150,180],[100,150],[100,100],[150,80],[200,100], [200,150], [150,180],[100,150]]
        self.c_points = []

        self.being_dragged = None
        self.buttons = []
        self.show_drawings = False


    def on_mouse_down(self, event):
        self.c_points.append([event.GetX(), event.GetY()])
        self.Refresh()
            
    def on_mouse_move(self, event):
        if self.being_dragged != None:
            self.c_points[self.being_dragged][0] = event.GetX()
            self.c_points[self.being_dragged][1] = event.GetY()
            self.Refresh()


    def create_menu(self):
        self.__algorithm = ""
        menu_algo = wx.Menu()
        menu_algo.Append(1, "Bezier")
        menu_algo.AppendSeparator()
        menu_algo.Append(4, "Poly Bezier Cubico")
        menu_algo.AppendSeparator()
        menu_algo.Append(2, "B-Spline Uniforme")
        menu_algo.AppendSeparator()
        menu_algo.Append(3, "B-Spline No Uniforme")

        menu_opt = wx.Menu()
        menu_opt.Append(5, "Limpiar editor")
        menu_opt.AppendSeparator()
        menu_opt.Append(6, "Imprimir puntos del grafo de control")
        menu_opt.AppendSeparator()
        menu_opt.Append(7, "Mostrar/Ocultar dibujos")

        
        menuBar = wx.MenuBar()
        menuBar.Append(menu_algo, "Algoritmos")
        menuBar.Append(menu_opt, "Opciones")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.menuBezier, id=1)
        self.Bind(wx.EVT_MENU, self.menuBSplineUniforme, id=2)
        self.Bind(wx.EVT_MENU, self.menuBSplineNoUniforme, id=3)
        self.Bind(wx.EVT_MENU, self.menuBezierMenorGrado, id=4)
        self.Bind(wx.EVT_MENU, self.menuLimpiar, id=5)
        self.Bind(wx.EVT_MENU, self.menuImprimir, id=6)
        self.Bind(wx.EVT_MENU, self.menuMostrarDibujos, id=7)
        
    def menuMostrarDibujos(self, event):
        if self.show_drawings:
            self.show_drawings = False
        else:
            self.show_drawings = True

        self.Refresh()


    def menuImprimir(self, event):
        print self.c_points

    def menuLimpiar(self, event):
        self.c_points = []
        self.Refresh()
        
    def menuBezier(self, event):
        self.__algorithm = "Bezier"
        self.Refresh()
    
    def menuBSplineUniforme(self, event):
        self.__algorithm = "BSplineUniforme"
        self.Refresh()
    
    def menuBSplineNoUniforme(self, event):
        self.__algorithm = "BSplineNoUniforme"
        self.Refresh()

    def menuBezierMenorGrado(self, event):
        self.__algorithm = "BezierMenorGrado"
        self.Refresh()
    
    def draw(self, putpixel):

        if self.show_drawings:
            nube = [[80, 67], [92, 46], [111, 44], [124, 74], [141, 49], [160, 46], [175, 69], [190, 47], [209, 46], [220, 66], [238, 78], [238, 103], [223, 115], [211, 132], [195, 130], [179, 113], [163, 129], [144, 129], [128, 112], [117, 126], [96, 128], [84, 112], [65, 101], [63, 77], [80,67]]
            curvas.BezierMenorGrado(nube, 1000, bresenham.draw_segment, putpixel)

            campo = [[7, 398], [110, 337], [226, 321], [355, 316], [483, 312], [591, 318], [697, 345], [791, 368]]
            curvas.Bezier(campo, 1000, bresenham.draw_segment, putpixel)

            arbol = [[271, 484], [301, 440], [316, 380], [314, 296], [243, 269], [252, 218], [218, 180], [250, 124], [302, 82], [388, 80], [419, 125], [458, 157], [446, 217], [437, 264], [386, 288], [384, 382], [397, 443], [421, 486]]
            curvas.bsplines_no_uniforme(arbol, 1000, 3, bresenham.draw_segment, putpixel)


            sol = [[100,100],[150,80],[200,100], [200,150], [150,180],[100,150],[100,100],[150,80],[200,100], [200,150], [150,180],[100,150],[100,100],[150,80],[200,100], [200,150], [150,180],[100,150]]
            curvas.bsplines(sol, 1000, bresenham.draw_segment, putpixel)
            
        else:

            c_points = self.c_points

            for b in self.buttons:
                b.Destroy()

            self.buttons = []
            s = len(c_points)
        
            b_size = (15, 15)

            alter_size = lambda p: [p[0] - b_size[0]/2, p[1] - b_size[1]/2]

            for i in range(s):
                if i + 1 != s:
                    LineSegment([int(c_points[i][0]),int(c_points[i][1])], [int(c_points[i+1][0]),int(c_points[i+1][1])] , bresenham.draw_segment, (255, 0, 0)).draw(putpixel)

                self.buttons.append(MyButton(self, i, '', alter_size(c_points[i]), b_size, c_points[i]))

            if self.__algorithm == "Bezier":
                curvas.Bezier(c_points, 1000, bresenham.draw_segment, putpixel)
            elif self.__algorithm == "BSplineUniforme":
                curvas.bsplines(c_points, 1000, bresenham.draw_segment, putpixel)
            elif self.__algorithm == "BSplineNoUniforme":
                curvas.bsplines_no_uniforme(c_points, 1000, 3, bresenham.draw_segment, putpixel)
            elif self.__algorithm == "BezierMenorGrado": 
                curvas.BezierMenorGrado(c_points, 1000, bresenham.draw_segment, putpixel)
      
            
if __name__ == "__main__":
    app = wx.App()
    CurvesWindow((800, 600))
    app.MainLoop()

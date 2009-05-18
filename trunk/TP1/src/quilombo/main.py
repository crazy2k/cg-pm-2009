import wx
import random
import time
import copy

import traceback

from core.windows import GenericWindow, ViewPort
from core.scenes import CompositeScene, Polygon

from utils import transformations
from algorithms import scan, bresenham, clipping, windowing

from core.scenes import *
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

        self.c_points = []
        self.being_dragged = None
        self.buttons = []
        self.show_drawings = False


    def on_mouse_down(self, event):
        if not self.show_drawings:
            self.c_points.append([event.GetX(), event.GetY()])
            self.Refresh()
            
    def on_mouse_move(self, event):
        if not self.show_drawings and self.being_dragged != None:
            self.c_points[self.being_dragged][0] = event.GetX()
            self.c_points[self.being_dragged][1] = event.GetY()
            self.Refresh()

    def create_menu(self):
        self.__algorithm = ""

        menu_algo = wx.Menu()
        menu_algo.Append(1, "Bezier")
        menu_algo.AppendSeparator()
        menu_algo.Append(4, "Poly Bezier")
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
        self.Bind(wx.EVT_MENU, self.menu_clear, id=5)
        self.Bind(wx.EVT_MENU, self.menu_print_points, id=6)
        self.Bind(wx.EVT_MENU, self.menu_show_drawings, id=7)

        self.__menu_algo = menu_algo
        self.__menu_opt = menu_opt
        
    def menu_show_drawings(self, event):
        if self.show_drawings:
            self.show_drawings = False

            for b in self.buttons:
                b.Show()

            for i in self.__menu_algo.GetMenuItems():
                i.Enable(True)
            for i in self.__menu_opt.GetMenuItems():
                if i.GetId() != 7: 
                    i.Enable(True)

        else:
            self.show_drawings = True

            for b in self.buttons:
                b.Hide()

            for i in self.__menu_algo.GetMenuItems():
                i.Enable(False)
            for i in self.__menu_opt.GetMenuItems():
                if i.GetId() != 7: 
                    i.Enable(False)

        self.Refresh()


    def menu_print_points(self, event):
        print self.c_points

    def menu_clear(self, event):
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
        # Dibujos
        if self.show_drawings:
            nube_points = [[80, 67], [92, 46], [111, 44], [124, 74],
                [141, 49], [160, 46], [175, 69], [190, 47], [209, 46],
                [220, 66], [238, 78], [238, 103], [223, 115], [211, 132],
                [195, 130], [179, 113], [163, 129], [144, 129], [128, 112],
                [117, 126], [96, 128], [84, 112], [65, 101], [63, 77],
                [80,67]]
            nube = PolyBezierCurve(nube_points, bresenham)

            campo_points = [[7, 398], [110, 337], [226, 321], [355, 316],
                [483, 312], [591, 318], [697, 345], [791, 368]]
            campo = BezierCurve(campo_points, bresenham)

            arbol_points = [[271, 484], [301, 440], [316, 380], [314, 296],
                [243, 269], [252, 218], [218, 180], [250, 124], [302, 82],
                [388, 80], [419, 125], [458, 157], [446, 217], [437, 264],
                [386, 288], [384, 382], [397, 443], [421, 486]]
            arbol = NotUniformBSplineCurve(arbol_points, bresenham)

            sol_points = [[100,100],[150,80],[200,100], [200,150],
                [150,180], [100,150], [100,100], [150,80], [200,100],
                [200,150], [150,180], [100,150], [100,100], [150,80],
                [200,100], [200,150], [150,180],[100,150]]
            sol = BSplineCurve(sol_points, bresenham)

            naive_scene = CompositeScene()
            naive_scene.add_child(nube)
            naive_scene.add_child(campo)
            naive_scene.add_child(arbol)
            naive_scene.add_child(sol)

            naive_scene.draw(putpixel)
        # Modo de edicion
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
                    LineSegment([c_points[i][0], c_points[i][1]],
                        [c_points[i+1][0], c_points[i+1][1]],
                        bresenham.draw_segment, (255, 0, 0)).draw(putpixel)

                self.buttons.append(MyButton(self, i, '',
                    alter_size(c_points[i]), b_size, c_points[i]))

            curve = None
            if self.__algorithm == "Bezier":
                curve = BezierCurve(c_points, bresenham)
            elif self.__algorithm == "BSplineUniforme":
                curve = BSplineCurve(c_points, bresenham)
            elif self.__algorithm == "BSplineNoUniforme":
                curve = NotUniformBSplineCurve(c_points, bresenham)
            elif self.__algorithm == "BezierMenorGrado": 
                curve = PolyBezierCurve(c_points, bresenham)

            if curve != None:
                curve.draw(putpixel)
      
            
if __name__ == "__main__":
    app = wx.App()
    CurvesWindow((800, 600))
    app.MainLoop()

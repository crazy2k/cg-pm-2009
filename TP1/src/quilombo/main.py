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

        wx.EVT_LEFT_DOWN(self, self.OnMouseDown)


    def OnMouseDown(self, event):
        if self.window.being_dragged == None:
            self.window.being_dragged = self.id
        else:
            self.window.being_dragged = None


class CurvesWindow(GenericWindow):
    
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Comparacion - Bresenham vs DDA",
            size, GenericWindow.STATIC)

        wx.EVT_MOTION(self, self.OnMouseMove)
        wx.EVT_LEFT_DOWN(self, self.OnMouseDown)


        self.CreateMenu()

        #self.c_points = [[100,100],[150,80],[200,100], [200,150], [150,180],[100,150],[100,100],[150,80],[200,100], [200,150], [150,180],[100,150],[100,100],[150,80],[200,100], [200,150], [150,180],[100,150]]
        self.c_points = []

        self.count = 0
        self.being_dragged = None
        self.buttons = []


    def OnMouseDown(self, event):
        self.c_points.append([event.GetX(), event.GetY()])
        self.Refresh()
            
    def OnMouseMove(self, event):
        if self.being_dragged != None:
            self.c_points[self.being_dragged][0] = event.GetX()
            self.c_points[self.being_dragged][1] = event.GetY()
            self.Refresh()


    def CreateMenu(self):
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
        menu_opt.Append(5, "Limpiar")
        
        menuBar = wx.MenuBar()
        menuBar.Append(menu_algo, "Algoritmos")
        menuBar.Append(menu_opt, "Opciones")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.menuBezier, id=1)
        self.Bind(wx.EVT_MENU, self.menuBSplineUniforme, id=2)
        self.Bind(wx.EVT_MENU, self.menuBSplineNoUniforme, id=3)
        self.Bind(wx.EVT_MENU, self.menuBezierMenorGrado, id=4)
        self.Bind(wx.EVT_MENU, self.menuLimpiar, id=5)
        
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

        self.count += 1

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

            self.buttons.append(MyButton(self, i, 'Button', alter_size(c_points[i]), b_size, c_points[i]))

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

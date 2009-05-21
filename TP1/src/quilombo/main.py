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
        if self.window.being_dragged == None and self.window.dirty() == False:
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

        self.__dirty = False
        self.create_menu()

        self.c_points = []
        self.being_dragged = None
        self.buttons = []
        self.show_drawings = False

    def dirty(self):
        return self.__dirty
        
    def on_mouse_down(self, event):
        if not self.show_drawings and self.__dirty == False:
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
        menu_opt.Append(8, "Mostrar espiral")
        menu_opt.Append(9, "Mostrar onda")
        menu_opt.Append(10, "Mostrar U")
        menu_opt.AppendSeparator()

        menu_opt.Append(6, "Imprimir puntos del grafo de control")
        menu_opt.AppendSeparator()
        menu_opt.Append(7, "Modo dibujos/editor")

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
        self.Bind(wx.EVT_MENU, self.menu_show_spiral, id=8)
        self.Bind(wx.EVT_MENU, self.menu_show_wave, id=9)
        self.Bind(wx.EVT_MENU, self.menu_show_U, id=10)

        self.__menu_algo = menu_algo
        self.__menu_opt = menu_opt
        
    def menu_show_spiral(self, event):
        self.c_points = [[95, 102], [127, 45], [180, 48], [205, 76],
            [223, 101], [217, 162], [183, 171], [139, 181], [115, 146],
            [130, 117], [149, 90], [181, 110], [175, 139]]
        self.Refresh()
        
    def menu_show_wave(self, event):
        self.c_points = [[52, 198], [70, 173], [112, 136], [161, 110],
            [203, 89], [253, 114], [289, 138], [324, 160], [382, 175],
            [446, 129], [499, 91]]
        self.Refresh()
 
    def menu_show_U(self, event):
        self.c_points = [[133, 61], [104, 116], [128, 227], [203, 227],
            [278, 227], [311, 119], [283, 62]]
        self.Refresh()
 

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
        self.LimpiarNoUnif()
        self.Refresh()
    
    def menuBSplineUniforme(self, event):
        self.__algorithm = "BSplineUniforme"
        self.LimpiarNoUnif()
        self.Refresh()
    
    def menuBSplineNoUniforme(self, event):
        self.__algorithm = "BSplineNoUniforme"
        self.LimpiarNoUnif()
        self.__dirty = True
        self.__knots = []
        dlg = wx.TextEntryDialog(self, 'Grado:', 'Eleccion del grado')
        while True:
            if dlg.ShowModal() == wx.ID_OK:
                try: 
                    grado = int(dlg.GetValue())
                    if grado > 0:
                        self.__grade = grado
                        break
                    else:
                        wx.MessageBox('El grado debe ser mayor que cero.',
                                   'Grado invalido') 
                except ValueError: 
                     wx.MessageBox('El grado ingresado es invalido.',
                                   'Grado invalido')                                           
        dlg.Destroy()
        
        for i in range (0,self.__grade + len(self.c_points)):
            if i < self.__grade:
                self.__knots.append(0)    
            elif i >= len(self.c_points):
                self.__knots.append((len(self.c_points) - self.__grade) + 1)
            else:
                self.__knots.append(i + 1 - self.__grade)
                  
        self.Refresh()
        self.__knotTitle = wx.StaticText(self, 11, 'Nudo')
        self.__knotNumber = wx.SpinCtrl(self, 12, pos = (0, 20) , min = 1, max = (len(self.c_points) - self.__grade) , initial = 1)
        self.Bind(wx.EVT_SPIN_UP, self.refreshSpinUp, id=12)
        self.Bind(wx.EVT_SPIN_DOWN, self.refreshSpinDown, id=12)
        self.__knotValueTitle = wx.StaticText(self, 13, 'Valor', pos = (0, 50))
        self.__knotValue = wx.Slider(self, 14, pos = (0, 70), minValue = self.__knots[self.__knotNumber.GetValue() + self.__grade - 2]*100, maxValue = self.__knots[self.__knotNumber.GetValue() + self.__grade]*100)
        self.Bind(wx.EVT_SLIDER, self.valorNudo, id=14)

    def refreshSpinUp(self, event):
        self.__knotValue.Destroy()
        self.__knotValue = wx.Slider(self, 14, pos = (0, 70), minValue = self.__knots[self.__knotNumber.GetValue() + self.__grade - 1]*100, maxValue = self.__knots[self.__knotNumber.GetValue() + self.__grade + 1]*100)
        self.Refresh()

    def refreshSpinDown(self, event):
        self.__knotValue.Destroy()
        self.__knotValue = wx.Slider(self, 14, pos = (0, 70), minValue = self.__knots[self.__knotNumber.GetValue() + self.__grade - 3]*100, maxValue = self.__knots[self.__knotNumber.GetValue() + self.__grade - 1]*100)
        self.Refresh()
        
    def valorNudo(self, event):
        self.__knots[self.__knotNumber.GetValue() + self.__grade -1] = float(self.__knotValue.GetValue())/100
        self.Refresh()
            
    def menuBezierMenorGrado(self, event):
        self.__algorithm = "BezierMenorGrado"
        self.LimpiarNoUnif()
        self.Refresh()

    def LimpiarNoUnif(self):
        if self.__dirty:
            self.__knotTitle.Destroy()
            self.__knotNumber.Destroy()
            self.__knotValueTitle.Destroy()
            self.__knotValue.Destroy()
            self.__dirty = False        
    
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
            knots = [0,0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,16,16]
            arbol = NotUniformBSplineCurve(arbol_points, knots, bresenham)

            sol_points = [[580, 70], [630, 50], [680, 70], [680, 120],
                [630, 150], [580, 120], [580, 70], [630, 50], [680, 70],
                [680, 120], [630, 150], [580, 120], [580, 70], [630, 50],
                [680, 70], [680, 120], [630, 150], [580, 120]]

            
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
            if self.__algorithm == "Bezier" and len(c_points) != 0:
                curve = BezierCurve(c_points, bresenham)
            elif self.__algorithm == "BSplineUniforme" and len(c_points) != 0:
                curve = BSplineCurve(c_points, bresenham)
            elif self.__algorithm == "BSplineNoUniforme" and len(c_points) != 0:
                curve = NotUniformBSplineCurve(c_points, self.__knots, bresenham)
            elif self.__algorithm == "BezierMenorGrado": 
                curve = PolyBezierCurve(c_points, bresenham)

            if curve != None:
                curve.draw(putpixel)
      
            
if __name__ == "__main__":
    app = wx.App()
    CurvesWindow((800, 600))
    app.MainLoop()

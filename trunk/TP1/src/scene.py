import wx

import bresenham
import dda
import scan

import random

class Triangle:

    self.algorithm = bresenham
    def __init__(self, vertex1, vertex2, vertex3, colour = wx.Colour(0, 0, 0)):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3

        self.animated = False

    def repaint(self, dc):
        scan.scan_triangle(vertex1, vertex2, vertex3, self.algorithm.draw_line_segment, dc.DrawPoint)

class BouncingTriangle(Triangle):
    def __init__(self, vertex1, vertex2, vertex3, box, colour = wx.Colour(0, 0, 0)):
        Triangle.__init__(vertex1, vertex2, vertex3, colour)



class SceneWindow(wx.Frame):

    SCENE_WIDTH = 500
    SCENE_HEIGHT = 600

    def __init__(self, title, algorithm):
        wx.Frame.__init__(self, None, id = 0, title = title,
            size=(SCENE_WIDTH, SCENE_HEIGHT))

        self.objects = []
        t = BouncingTriangle((200, 300), (250, 200), (300,300), (0, 0, SCENE_WIDTH, SCENE_HEIGHT))
        self.objects.add(t)

        self.Bind(wx.EVT_PAINT, self.repaint)

        self.Centre()
        self.Show(True)

        #self.x = 0
        #self.y = 0

        #self.r = 0
        #self.g = 0
        #self.b = 0

        #self.dr = 1
        #self.dg = -1
        #self.db = 1

        #self.dx = 1
        #self.dy = -1


    def repaint(self, event):
        for o in objects:
            o.repaint(wx.ClientDC(self))

        dc = wx.ClientDC(self)

        pen = dc.GetPen()

        if self.r == 255:
            self.dr = -1
        if self.g == 255:
            self.dg = -1
        if self.b == 255:
            self.db = -1

        if self.r == 0:
            self.dr = 1
        if self.g == 0:
            self.dg = 1
        if self.b == 0:
            self.db = 1


        v = random.randint(0, 2)
        if v == 0:
            self.r = self.r + self.dr
        elif v == 1:
            self.g = self.g + self.dg
        elif v == 2:
            self.b = self.b + self.db

        pen.SetColour(wx.Colour(self.r, self.g, self.b))

        dc.SetPen(pen)

        scan.scan_triangle(200 + self.x,300 + self.y,250 + self.x,200 + self.y,300 + self.x,300 + self.y,self.algoritmos.dibujar_segmento, dc.DrawPoint)

        if 200 + self.y == 0:
            self.dy = 1
        if 300 + self.x == 500:
            self.dx = -1
        if 200 + self.x == 0:
            self.dx = 1
        if 300 + self.y == 600:
            self.dy = -1

        self.x = self.x + self.dx
        self.y = self.y + self.dy

        self.Refresh()


app = wx.App()
#Ventana(id = 0, title = "Lineas con Bresenham", algoritmos = bresenham)
#Ventana(id = 1, title = "Lineas con DDA", algoritmos = dda)
Ventana(id = 1, title = "Triangulo en movimiento", algoritmos = bresenham)
app.MainLoop()

import wx

import bresenham
import dda
import scan

import random

class Ventana(wx.Frame):

    def __init__(self, id, title, algoritmos):
        wx.Frame.__init__(self, None, id, title, size=(500, 600))

        self.algoritmos = algoritmos

        self.Bind(wx.EVT_PAINT, self.dibujar_linea)

        self.Centre()
        self.Show(True)

        self.x = 0
        self.y = 0

        self.r = 0
        self.g = 0
        self.b = 0

        self.dr = 1
        self.dg = -1
        self.db = 1

        self.dx = 1
        self.dy = -1


    def dibujar_linea(self, event):
        dc = wx.ClientDC(self)
        #self.algoritmos.dibujar_segmento(10, 10, 400, 100, dc.DrawPoint)
        #self.algoritmos.dibujar_segmento(400, 500, 10, 10, dc.DrawPoint)
        #self.algoritmos.dibujar_segmento(100, 500, 400, 10, dc.DrawPoint)
        #self.algoritmos.dibujar_segmento(400, 10, 10, 500, dc.DrawPoint)

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

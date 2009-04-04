import wx

import bresenham
import dda
import scan

class Ventana(wx.Frame):
    def __init__(self, id, title, algoritmos):
        wx.Frame.__init__(self, None, id, title, size=(500, 600))

        self.algoritmos = algoritmos

        self.Bind(wx.EVT_PAINT, self.dibujar_linea)

        self.Centre()
        self.Show(True)


    def dibujar_linea(self, event):
        dc = wx.ClientDC(self)
        self.algoritmos.dibujar_segmento(10, 10, 400, 100, dc.DrawPoint)
        self.algoritmos.dibujar_segmento(400, 500, 10, 10, dc.DrawPoint)
        self.algoritmos.dibujar_segmento(100, 500, 400, 10, dc.DrawPoint)
        self.algoritmos.dibujar_segmento(400, 10, 10, 500, dc.DrawPoint)

        self.algoritmos.dibujar_segmento(20, 20, 20, 500, dc.DrawPoint)

        scan.scan_triangle(10,10,400,100,450,500,self.algoritmos.dibujar_segmento, dc.DrawPoint)

app = wx.App()
Ventana(id = 0, title = "Lineas con Bresenham", algoritmos = bresenham)
#Ventana(id = 1, title = "Lineas con DDA", algoritmos = dda)
app.MainLoop()


import psyco
import wx

import bresenham
import dda
import time
import scan

from PIL import Image



import random


class Ventana(wx.Frame):


    def __init__(self, id, title, algoritmos):
        wx.Frame.__init__(self, None, id, title, size=(500, 600))

        self.algoritmos = algoritmos
        
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

        self._buff = [[(255,255,255)]*600]*500

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Centre()
        self.Show(True)


    def add_to_buffer(self, x, y):
        #self._buff[x, y] = (0, 0, 0)
        try:
            self._buff[x][y] = (0, 0, 0)
        except:
            print x, y

    def on_paint(self, event):

        #self._buffer = self.empty_bitmap()
        #bmp = wx.EmptyBitmap(500, 600)
        #data = wx.NativePixelData(bmp)

        im = Image.new('RGB', (500,600))
    
        #print flatten(self._buff)
        #return


        #self._buff = im.load()


        self.draw(self.add_to_buffer)

        im.putdata(flatten(self._buff))
        bmp = pilToBitmap(im)

        pdc = wx.PaintDC(self)
        pdc.DrawBitmap(bmp, 0, 0)

        self.Refresh()

            
    def draw(self, putpixel):
        """pen = dc.GetPen()

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
        """
        v = random.randint(0, 2)
        if v == 0:
            self.r = self.r + self.dr
        elif v == 1:
            self.g = self.g + self.dg
        elif v == 2:
            self.b = self.b + self.db

        #pen.SetColour(wx.Colour(self.r, self.g, self.b))

        #dc.SetPen(pen)

        scan.scan_triangle(200 + self.x,300 + self.y,250 + self.x,200 + self.y,300 + self.x,300 + self.y,self.algoritmos.dibujar_segmento, putpixel)

        if 200 + self.y == 0:
            self.dy = 1
            print time.time()
        if 300 + self.x == 499:
            self.dx = -1
            print time.time()
        if 200 + self.x == 0:
            self.dx = 1
            print time.time()
        if 300 + self.y == 599:
            self.dy = -1
            print time.time()

        self.x = self.x + self.dx
        self.y = self.y + self.dy

def pilToBitmap(pil):
    return imageToBitmap(pilToImage(pil))

def imageToBitmap(image):
    return image.ConvertToBitmap()

def pilToImage(pil):
    image = wx.EmptyImage(pil.size[0], pil.size[1])
    image.SetData(pil.convert('RGB').tostring())
    return image

def flatten(l):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for x in l:
        for y in x:
            result.append(y)

    return result
       


app = wx.App()
#Ventana(id = 0, title = "Lineas con Bresenham", algoritmos = bresenham)
#Ventana(id = 1, title = "Lineas con DDA", algoritmos = dda)
Ventana(id = 1, title = "Triangulo en movimiento", algoritmos = bresenham)
app.MainLoop()

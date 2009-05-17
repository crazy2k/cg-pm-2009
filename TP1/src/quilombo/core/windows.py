import wx
from utils import convert
from PIL import Image

#import array
#import numpy


class ViewPort:
    def __init__(self, refpoint, width, height):
        self.refpoint = refpoint
        self.width = width
        self.height = height
        
    def getRefPoint(self):
        return self.refpoint
        
    def getWidth(self):
        return self.width
        
    def getHeight(self):
        return self.height

class GenericWindow(wx.Frame):
    
    AUTO_REFRESHING = 0
    STATIC = 1

    USE_NUMPY = False

    def __init__(self, id, title, size, type):
        wx.Frame.__init__(self, None, id, title, size = size)

        self.type = type
       
        # realizaremos double buffering
        width = size[0]
        height = size[1]

        # el metodo on_paint se encargara de repintar
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Bind(wx.EVT_SIZE, self.on_size)

        if self.type == self.AUTO_REFRESHING:
            self.timer = wx.Timer(self, id=1)
            self.timer.Start(300)
            self.Bind(wx.EVT_TIMER, self.on_timer, id=1)


        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.bmp = None

        self.Centre()
        self.Show(True)

    def on_timer(self, event):
        self.bmp = self.__create_bmp()

        # pinto el bitmap en la ventana
        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def on_paint(self, event):
        if self.bmp == None:
            self.bmp = self.__create_bmp()

        # pinto el bitmap en la ventana
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def Refresh(self):
        self.bmp = None
        wx.Frame.Refresh(self)

    def __create_bmp(self):
        size = self.GetSize().Get()

        width = size[0]
        height = size[1]

        if not self.USE_NUMPY:
            # creo una imagen de PIL, en blanco
            im = Image.new('RGB', size, (255, 255, 255))

            # voy a acceder a sus pixels a traves de esta variable
            self.__buff = im.load()

        elif self.USE_NUMPY:
            self.__bytes = numpy.empty((height, width, 3), numpy.uint8)
            self.__bytes[:][:][:] = 255

        # escribo en sus pixels, segun la funcion de dibujado
        self.draw(self.add_to_buffer)

        if not self.USE_NUMPY:
            # me genero un bitmap a partir de la imagen creada
            bmp = convert.pilToBitmap(im)

        elif self.USE_NUMPY:
            bmp = wx.BitmapFromBuffer(width, height, self.__bytes)
        
        return bmp


    def on_size(self, event):
       pass

    def on_close(self, event):
        if self.type == self.AUTO_REFRESHING:
            self.timer.Stop()
        self.Destroy()

    def add_to_buffer(self, x, y, colour = (0, 0, 0)):
        size = self.GetSize().Get()

        width = size[0]
        height = size[1]

        x = x % size[0]
        y = y % size[1]

        if not self.USE_NUMPY:
            self.__buff[x, y] = colour

        if self.USE_NUMPY:
            self.__bytes[y][x][0] = colour[0]
            self.__bytes[y][x][1] = colour[1]
            self.__bytes[y][x][2] = colour[2]

    def draw(self, x, y):
        raise NotImplementedError

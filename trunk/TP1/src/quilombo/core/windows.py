import wx
from utils import convert
from PIL import Image

#import array
import numpy

class GenericWindow(wx.Frame):
    
    AUTO_REFRESHING = 0
    STATIC = 1

    def __init__(self, id, title, size, type):
        wx.Frame.__init__(self, None, id, title, size = size)

        self.type = type
       
        # realizaremos double buffering
        width = size[0]
        height = size[1]

        # el metodo on_paint se encargara de repintar
        self.Bind(wx.EVT_PAINT, self.on_paint)

        if self.type == self.AUTO_REFRESHING:
            self.timer = wx.Timer(self, id=1)
            self.timer.Start(1)
            self.Bind(wx.EVT_TIMER, self.on_paint, id=1)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.Centre()
        self.Show(True)

    def on_close(self, event):
        if self.type == self.AUTO_REFRESHING:
            self.timer.Stop()
        self.Destroy()


    def on_paint(self, event):

        size = self.GetSize().Get()

        width = size[0]
        height = size[1]

        # creo una imagen de PIL, en blanco
        #im = Image.new('RGB', size, (255, 255, 255))

        # voy a acceder a sus pixels a traves de esta variable
        #self.__buff = im.load()

        #bmp = wx.EmptyBitmap(size[0], size[1], 32)

        #self.__px_data = wx.NativePixelData(bmp)
        #print wx.NativePixelData(bmp)
        #if not self.__px_data:
        #    raise RuntimeError("No se puede acceder a los datos del bmp.")

        #self.__pixels = self.__px_data.GetPixels()
        #for y in xrange(size[1]):
        #    for x in xrange(size[0]):
        #        pixels.Set
        # Make a bitmap using an array of RGB bytes

        self.__bpp = 3  # bytes per pixel
        #self.__bytes = array.array('B', [255] * width*height*self.__bpp)
        self.__bytes = numpy.zeros((width, height, 3), 'uint8')


        # escribo en sus pixels, segun la funcion de dibujado
        self.draw(self.add_to_buffer)

        # me genero un bitmap a partir de la imagen creada
        #bmp = convert.pilToBitmap(im)

        #bmp = wx.BitmapFromBuffer(width, height, self.__bytes)
        
        image = wx.EmptyImage(width, height)
        image.SetData(self.__bytes.tostring())
        bmp = image.ConvertToBitmap()

        # pinto el bitmap en la ventana
        pdc = wx.PaintDC(self)
        pdc.DrawBitmap(bmp, 0, 0)


    def add_to_buffer(self, x, y, colour = (0, 0, 0)):
        size = self.GetSize().Get()

        width = size[0]
        height = size[1]

        x = x % size[0]
        y = y % size[1]

        #self.__buff[x, y] = colour

        #self.__pixels.MoveTo(self.__px_data, x, y)
        #self.__pixels.Set(colour[0], colour[1], colour[2])

        #offset = y*width*self.__bpp + x*self.__bpp
        #r, g, b = colour[0], colour[1], colour[2]
        #self.__bytes[offset + 0] = r
        #self.__bytes[offset + 1] = g
        #self.__bytes[offset + 2] = b
        self.__bytes[x][y] = [colour[0], colour[1], colour[2]]


    def draw(self, x, y):
        raise NotImplementedError

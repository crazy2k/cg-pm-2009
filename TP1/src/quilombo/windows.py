import wx
from utils import convert
from PIL import Image

class GenericWindow(wx.Frame):
    
    AUTO_REFRESHING = 0

    def __init__(self, id, title, size, type):
        wx.Frame.__init__(self, None, id, title, size = size)

        self.type = type
       
        # realizaremos double buffering
        width = size[0]
        height = size[1]
        #self.__buff = [[(255,255,255)]*height]*width

        # el metodo on_paint se encargara de repintar
        self.Bind(wx.EVT_PAINT, self.on_paint)

        if self.type == self.AUTO_REFRESHING:
            self.timer = wx.Timer(self, id=1)
            self.timer.Start(1)
            self.Bind(wx.EVT_TIMER, self.on_paint, id=1)

        self.Bind(wx.EVT_CLOSE, self.on_close, id=1)

        self.Centre()
        self.Show(True)

    def on_close(self, event):
        if self.type == self.AUTO_REFRESHING:
            self.timer.Stop()
        self.Destroy()


    def on_paint(self, event):

        size = self.GetSize().Get()
        # creo una imagen de PIL, en blanco
        im = Image.new('RGB', size, (255, 255, 255))

        # voy a acceder a sus pixels a traves de esta variable
        self.__buff = im.load()

        # escribo en sus pixels, segun la funcion de dibujado
        self.draw(self.add_to_buffer)

        # me genero un bitmap a partir de la imagen creada
        bmp = convert.pilToBitmap(im)

        # pinto el bitmap en la ventana
        pdc = wx.PaintDC(self)
        pdc.DrawBitmap(bmp, 0, 0)


    def add_to_buffer(self, x, y, colour = (0, 0, 0)):
        size = self.GetSize().Get()
        #print size
        x = x % size[0]
        y = y % size[1]
        self.__buff[x, y] = colour

    def draw(self, x, y):
        raise NotImplementedError

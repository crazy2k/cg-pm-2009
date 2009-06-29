import wx

from core.glwindows import GLFrame

if __name__ == "__main__":

    app = wx.App()

    GLFrame(-1, "Arbolitos", (500, 500))

    app.MainLoop()




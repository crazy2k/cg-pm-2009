

import wx

from core.glwindows import GLFrame

if __name__ == "__main__":

    app = wx.App()

    GLFrame(-1, "Visualizador y editor de arbolitos", (1000, 450))

    app.MainLoop()




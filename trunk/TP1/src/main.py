import wx

import bresenham

from scene import SceneWindow


app = wx.App()

#Ventana(id = 0, title = "Lineas con Bresenham", algoritmos = bresenham)
#Ventana(id = 1, title = "Lineas con DDA", algoritmos = dda)
SceneWindow(id = 1, title = "Escena", algoritmos = bresenham)

app.MainLoop()

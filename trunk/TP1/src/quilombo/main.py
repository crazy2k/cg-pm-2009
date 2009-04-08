import wx
from windows import GenericWindow

import random
from scenes import CompositeScene, Triangle

import time

class OurWindow(GenericWindow):
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Nuestra escena", size,
            GenericWindow.AUTO_REFRESHING)

    def draw(self, putpixel):
        x, y = 0, 0

        r, g, b = 0, 0, 0

        dx = 1
        dy = -1

        dr = 1
        dg = -1
        db = 1

        scene = CompositeScene()
        tr = Triangle((200, 300), (250, 200), (300, 300))
        scene.add_child(tr)

        while True:
            if r == 255:
                dr = -1
            if g == 255:
                dg = -1
            if b == 255:
                db = -1

            if r == 0:
                dr = 1
            if g == 0:
                dg = 1
            if b == 0:
                db = 1

            v = random.randint(0, 2)
            if v == 0:
                r = r + dr
            elif v == 1:
                g = g + dg
            elif v == 2:
                b = b + db

            tr.colour = (r, g, b)
            move = lambda vertex, offsets: (vertex[0] + offsets[0], vertex[1] + offsets[1])
            tr.vertex1 = move(tr.vertex1, (dx, dy))
            tr.vertex2 = move(tr.vertex2, (dx, dy))
            tr.vertex3 = move(tr.vertex3, (dx, dy))

            scene.draw(putpixel)

            yield

            if tr.vertex2[1] == 0:
                dy = 1
                print time.time()
            if tr.vertex3[0] == 499:
                dx = -1
                print time.time()
            if tr.vertex1[0] == 0:
                dx = 1
                print time.time()
            if tr.vertex3[1] == 599:
                dy = -1
                print time.time()


if __name__ == "__main__":
    app = wx.App()
    OurWindow((500, 600))
    app.MainLoop()

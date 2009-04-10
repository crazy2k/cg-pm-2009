import wx
from windows import GenericWindow

import random
from scenes import CompositeScene, Triangle

from utils import transformations

import time

class OurWindow(GenericWindow):
    def __init__(self, size):
        GenericWindow.__init__(self, 0, "Nuestra escena", size,
            GenericWindow.AUTO_REFRESHING)

        self.__r = 0
        self.__g = 0
        self.__b = 0

        self.__dr = 0
        self.__dg = 0
        self.__db = 0

        self.__tr = Triangle((200, 300), (250, 200), (300, 300))
        self.__t = [[1, 0, 1], [0, 1, -1], [0, 0, 1]]

    def draw(self, putpixel):

        tr = self.__tr

        t = self.__t

        self.__dr = 1
        self.__dg = -1
        self.__db = 1

        scene = CompositeScene()

        scene.add_child(tr)

        if self.__r == 255:
            self.__dr = -1
        if self.__g == 255:
            self.__dg = -1
        if self.__b == 255:
            self.__db = -1

        if self.__r == 0:
            self.__dr = 1
        if self.__g == 0:
            self.__dg = 1
        if self.__b == 0:
            self.__db = 1

        v = random.randint(0, 2)
        if v == 0:
            self.__r = self.__r + self.__dr
        elif v == 1:
            self.__g = self.__g + self.__dg
        elif v == 2:
            self.__b = self.__b + self.__db

        tr.colour = (self.__r, self.__g, self.__b)
        tr.transform(self.__t)

        if tr.vertex2[1] == 0:
            self.__t[1] = [0, 1, 1]
            print time.time()
        if tr.vertex3[0] == self.GetSize().Get()[0] - 1:
            self.__t[0] = [1, 0, -1]
            print time.time()
        if tr.vertex1[0] == 0:
            self.__t[0] = [1, 0, 1]
            print time.time()
        if tr.vertex3[1] == self.GetSize().Get()[1] - 1:
            self.__t[1] = [0, 1, -1]
            print time.time()

        scene.draw(putpixel)


if __name__ == "__main__":
    app = wx.App()
    OurWindow((500, 600))
    app.MainLoop()

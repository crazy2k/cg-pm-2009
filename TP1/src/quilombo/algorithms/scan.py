class TriangleScanAlgorithm:

    def __init__(self):
        self.__maxx = 0
        self.__maxy = 0

    def scan(self, vertex1, vertex2, vertex3, draw_segment, putpixel):
        x1 = vertex1[0]
        y1 = vertex1[1]
        x2 = vertex2[0]
        y2 = vertex2[1]
        x3 = vertex3[0]
        y3 = vertex3[1]

        fig_maxwidth = max(x1, x2, x3) + 1
        fig_maxheight = max(y1, y2, y3) + 1

        self.__maxx = [-1]*fig_maxheight
        self.__minx = [fig_maxwidth]*fig_maxheight

        draw_segment((x1, y1), (x2, y2), self.__max_setter)
        draw_segment((x2, y2), (x3, y3), self.__max_setter)
        draw_segment((x1, y1), (x3, y3), self.__max_setter)

        for y in range(fig_maxheight):
            if self.__maxx[y] != -1:
                draw_segment((self.__minx[y], y), (self.__maxx[y], y), putpixel)


    def __max_setter(self, x,y):
        if x > self.__maxx[y]:
            self.__maxx[y] = x
        if x < self.__minx[y]:
            self.__minx[y] = x


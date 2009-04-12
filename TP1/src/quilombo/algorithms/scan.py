class PolygonScanAlgorithm:

    def __init__(self):
        self.__maxx = 0
        self.__maxy = 0

    def scan(self, vertices, draw_segment, putpixel, colour):
        fig_maxwidth = max([v[0] for v in vertices]) + 1
        fig_maxheight = max([v[1] for v in vertices]) + 1

        self.__maxx = [-1]*fig_maxheight
        self.__minx = [fig_maxwidth]*fig_maxheight

        for i in range(len(vertices) - 1):
            draw_segment(vertices[i], vertices[i+1], self.__max_setter, None)
        draw_segment(vertices[-1], vertices[0], self.__max_setter, None)

        for y in range(fig_maxheight):
            if self.__maxx[y] != -1:
                draw_segment((self.__minx[y], y), (self.__maxx[y], y),
                    putpixel, colour)


    def __max_setter(self, x, y, colour = None):
        if x > self.__maxx[y]:
            self.__maxx[y] = x
        if x < self.__minx[y]:
            self.__minx[y] = x


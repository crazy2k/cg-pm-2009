
def scan_triangle(x1,y1,x2,y2,x3,y3,dibujar_segmento,put_pixel):
    ancho_pantalla, alto_pantalla = 501, 601
    global maxx
    maxx = [-1]*alto_pantalla
    global minx
    minx = [ancho_pantalla]*alto_pantalla
    dibujar_segmento(x1,y1,x2,y2,funcion_scan)
    dibujar_segmento(x2,y2,x3,y3,funcion_scan)
    dibujar_segmento(x1,y1,x3,y3,funcion_scan)
    for y in range(alto_pantalla):
        if maxx[y] != -1 and minx[y] != alto_pantalla:
            dibujar_segmento(minx[y],y,maxx[y],y,put_pixel)


def funcion_scan(x,y):
    x, y = int(x),int(y)
    if x > maxx[y]:
        maxx[y] = x
    if x < minx[y]:
        minx[y] = x




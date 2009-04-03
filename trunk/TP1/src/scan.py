
# Comentario de prueba
def scan_triangle(x1,y1,x2,y2,x3,y3,dibujar_linea,put_pixel):
    ancho_pantalla, alto_pantalla = 10000, 10000
    global maxx
    maxx = [-1]*alto_pantalla
    global minx
    minx = [ancho_pantalla]*alto_pantalla
    dibujar_linea(x1,y1,x2,y2,funcion_scan)
    dibujar_linea(x2,y2,x3,y3,funcion_scan)
    dibujar_linea(x1,y1,x3,y3,funcion_scan)
    for y in range (0,alto_pantalla):
        if maxx[y] != -1:
            dibujar_linea(minx[y],y,maxx[y],y,put_pixel)


def funcion_scan(x,y):
    x, y = int(round(x)),int(round(y))
    if x > maxx[y]:
        maxx[y] = x
    if x < minx[y]:
        minx[y] = x




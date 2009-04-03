

def dibujar_segmento(x1, y1, x2, y2, putpixel):
    """Dibuja en el plano el segmento de una recta que pasa por los puntos
    (x1, y1) y (x2, y2), usando el algoritmo de DDA. Usa dichos puntos
    como extremos del segmento. Utiliza la funcion putpixel(x, y) para
    dibujar los puntos."""

    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = x2 - x1
    dy = y2 - y1

    m = float((y2 - y1))/(x2 - x1)

    y = y1

    for x in range(x1, x2 -1):
        putpixel(x, round(y))

        y = y + m


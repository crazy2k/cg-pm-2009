

def draw_segment(endpoint1, endpoint2, putpixel, colour):
    """Dibuja en el plano el segmento de una recta que pasa por los puntos
    endpoint1 y endpoint2, usando el algoritmo de Bresenham. Usa dichos puntos
    como extremos del segmento. Utiliza la funcion putpixel(x, y) para
    dibujar los puntos."""

    x1 = endpoint1[0]
    y1 = endpoint1[1]
    x2 = endpoint2[0]
    y2 = endpoint2[1]

    # si la pendiente tiene modulo mayor que 1, lo que vamos a hacer es
    # calcular la ubicacion para los puntos reflejados del otro lado de la
    # recta y = x, pero dibujaremos los pixels en el lugar en el que van
    # (mas adelante, imprimimos (y, x) en lugar de (x, y)
    steep = abs(y2 - y1) > abs(x2 - x1)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # dibujamos siempre de izquierda a derecha

    # si el punto inicial esta mas a la derecha que el punto final,
    # los intercambiamos
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    # si el punto inicial se encuentra mas arriba, en cada paso vamos
    # a movernos hacia la derecha o hacia arriba, en lugar de hacia la
    # derecha o hacia abajo
    if y1 > y2:
        step = -1
    else:
        step = 1

    dx = x2 - x1
    dy = abs(y2 - y1)

    ix = 2*dx
    iy = 2*dy

    e = iy - dx

    y = y1

    for x in range(x1, x2 + 1):

        if steep:
            putpixel(y, x, colour)
        else:
            putpixel(x, y, colour)

        # elijo el punto en la diagonal
        if e > 0:
            y = y + step
            e = e - ix + iy
        
        # elijo el punto al este
        else:
            e = e + iy


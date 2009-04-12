

def dibujar_segmento(x1, y1, x2, y2, putpixel):
    """Dibuja en el plano el segmento de una recta que pasa por los puntos
    (x1, y1) y (x2, y2), usando el algoritmo de Bresenham. Usa dichos puntos
    como extremos del segmento. Utiliza la funcion putpixel(x, y) para
    dibujar los puntos."""
    
    l = [x1, y1, x2, y2]
    for i in l:
        if not isinstance(i, int):
            raise Exception('Los puntos deben ser enteros.')

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
            putpixel(y,x)
        else:
            putpixel(x,y)

        # elijo el punto en la diagonal
        if e > 0:
            y = y + step
            e = e - ix + iy
        
        # elijo el punto al este
        else:
            e = e + iy

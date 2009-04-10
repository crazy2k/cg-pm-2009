def draw_segment(endpoint1, endpoint2, putpixel, colour):
    """Dibuja en el plano el segmento de una recta que pasa por los puntos
    endpoint1 y endpoint2, usando el algoritmo de DDA. Usa dichos puntos
    como extremos del segmento. Utiliza la funcion putpixel(x, y) para
    dibujar los puntos."""

    x1 = endpoint1(0)
    y1 = endpoint1(1)
    x2 = endpoint2(0)
    y2 = endpoint2(1)

    # tratamos el caso de las lineas verticales aparte
    if x1 == x2:
        # si el punto inicial esta mas abajo que el punto final,
        # intercambiamos los puntos (notar que basta con intercambiar y1 e y2)
        if y1 > y2:
            y1, y2 = y2, y1

        for y in range(y1, y2 + 1):
            putpixel(x1, y, colour)

        return


    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = x2 - x1
    dy = y2 - y1

    m = float((y2 - y1))/(x2 - x1)

    y = y1

    for x in range(x1, x2 -1):
        putpixel(x, round(y), colour)

        y = y + m


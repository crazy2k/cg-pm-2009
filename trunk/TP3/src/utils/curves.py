import copy


def Bezier(grafo_control, paso, drawsegment, putpixel):

    def de_casteljau(u, grafo_control, punto):
    
        n = len(grafo_control)
        for k in range (1, n):
            for l in range (0, n-k):
                grafo_control[l][0] = (1-u)*grafo_control[l][0] + u*grafo_control[l+1][0]
                grafo_control[l][1] = (1-u)*grafo_control[l][1] + u*grafo_control[l+1][1]
                
        punto = int(grafo_control[0][0]), int(grafo_control[0][1])
        return punto

    copia_grafo_control = copy.deepcopy(grafo_control)
    p = int(grafo_control[0][0]), int(grafo_control[0][1])

    for k in range (1, paso + 1):
        u = float(k)/paso

        p_anterior = copy.deepcopy(p)

        p = de_casteljau(u, copia_grafo_control, p)

        drawsegment(p_anterior, p, putpixel, (0,0,0))


def BezierMenorGrado(grafo_control, paso, drawsegment, putpixel):
    copia_grafo_control = copy.deepcopy(grafo_control)
    while len(copia_grafo_control)>0:
        Bezier(copia_grafo_control[0:4], paso, drawsegment, putpixel)
        copia_grafo_control = copia_grafo_control[3:]


def bsplines(g, pasos, draw_segment, putpixel):
    def base(u, i):
        if i == 1:
            return float(u*u*u)/6
        elif i == 0:
            return float(1 + u*3*(1 + u*(1 - u)))/6
        elif i == -1:
            return float(4 + u*u*3*(-2 + u))/6
        elif i == -2:
            return float(1 + u*(-3 + u*(3 - u)))/6

    p = g[0]
    
    for j in range(1, len(g)-1):
        for k in range(2, pasos + 1):
            u = float(k)/pasos
        
   
            p_anterior = copy.deepcopy(p)
            p = [0, 0]
            
            for i in range(-2, 2):
                v = base(u, i)
                
                index = i + j
                
                if index < 0:
                    index = 0
                elif index >= len(g):
                    index = len(g)-1

                p[0] = p[0] + g[index][0]*v
                p[1] = p[1] + g[index][1]*v
            
            p = [int(p[0]), int(p[1])]
            if j>1:
                draw_segment(p_anterior, p, putpixel, (0,0,0))



# g: grafo de control
# n: nudos (knots)
def bsplines_no_uniforme(g, n, pasos, grado, draw_segment, putpixel):

    pts_ctrol = len(g) - 1

    def base(n, u, i, k):

        # caso base de la recursion
        if k == 1:
            if (u < n[i+1]) and (n[i] <= u):
                return 1
            return 0

        # recursion
        else:
            # N_{i,k} = n1/d1 + n2/d2
            n1 = (u - n[i])*base(n, u, i, k - 1)
            n2 = (n[i + k] - u)*base(n, u, i+1, k-1)
            d1 = n[i + k -1] - n[i]
            d2 = n[i + k] - n[i + 1]

            # evitamos la division por cero para el primer cociente
            if d1 == 0:
                c1 = 0
            else:
                c1 = float(n1)/d1
                
            # evitamos la division por cero para el segundo cociente
            if d2 == 0:
                c2 = 0
            else:
                c2 = float(n2)/d2

            return c1 + c2

    p = g[0]
    # u va de 0 a pts_control - grado + 2
    for i in range(0, pasos*(pts_ctrol - grado + 2)):
        p_anterior = copy.deepcopy(p)
        p = [0, 0]
        u = float(i)/pasos
        
        # calculo P(u) = sumatoria de j = 0,..., pts_control de g_j*N
        # (N es la funcion de blending)
        # (recordar: j va hasta pts_control; el '+ 1' es por el range)
        for j in range(0, pts_ctrol + 1):
            v = base(n, u, j, grado)
            p[0] += g[j][0]*v
            p[1] += g[j][1]*v

        p_ant_int = [int(p_anterior[0]), int(p_anterior[1])]
        p_int = [int(p[0]), int(p[1])]

        draw_segment(p_ant_int, p_int, putpixel, (0,0,0))


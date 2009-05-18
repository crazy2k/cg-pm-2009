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
    for i in range ((len(grafo_control)+1)/4):
        for j in range (4):
            if i==0:
                Bezier(grafo_control[i*4:i*4+4], paso, drawsegment, putpixel)
            else:
                Bezier(grafo_control[i*4-1:i*4+3], paso, drawsegment, putpixel)
            


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



#def bspline2(grafo_control):
 #   for x in range(pasos):
        
def bsplines_no_uniforme(g, pasos, grado, draw_segment, putpixel):

    pts_ctrol=len(g)-1

    def Nudo(i):

        if i < grado:
            return 0
        elif i > pts_ctrol:
            return pts_ctrol-grado+2
        else:
            return i-grado+1
    
    def Base(u, i, k):
    
        if k==1:
            if (u < Nudo(i+1)) and (Nudo(i) <= u):
                return 1
            else:
                return 0
        else:
            n1 = (u-Nudo(i))*Base(u,i,k-1)
            n2 = (Nudo(i+k)-u)*Base(u,i+1,k-1)
            d1 = Nudo(i+k-1)-Nudo(i)
            d2 = Nudo(i+k)-Nudo(i+1)
            if d1==0:
                c1 = 0
            else:
                c1 = float(n1)/d1
            if d2==0:
                c2 = 0
            else:
                c2 = float(n2)/d2
            return c1+c2

    p = g[0]            
    for i in range(0,pasos*(pts_ctrol-grado+2)):
        p_anterior = copy.deepcopy(p)
        p = [0,0]
        u = float(i)/pasos
        
        for j in range(0,pts_ctrol+1):
            v = Base(u,j,grado)
            p[0] = p[0] + g[j][0]*v
            p[1] = p[1] + g[j][1]*v

        p_ant_int = [int(p_anterior[0]), int(p_anterior[1])]
        p_int = [int(p[0]), int(p[1])]
        #print p_ant_int, p_int
        draw_segment(p_ant_int, p_int, putpixel, (0,0,0))


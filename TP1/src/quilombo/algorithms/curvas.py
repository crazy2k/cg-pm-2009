import copy


def Bezier(grafo_control, paso, drawsegment, putpixel):

    def de_casteljau(u, grafo_control, punto):
    
        n = len(grafo_control)
        for k in range (1, n):
            for l in range (0, n-k):
                grafo_control[l][0] = (1-u)*grafo_control[l][0] + u*grafo_control[l+1][0]
                grafo_control[l][1] = (1-u)*grafo_control[l][1] + u*grafo_control[l+1][1]

        return (int(grafo_control[0][0]), int(grafo_control[0][1]))


    p = grafo_control[0]

    for k in range (1, paso + 1):
        u = float(k)/paso

        p_anterior = copy.deepcopy(p)

        p = de_casteljau(u, grafo_control, p)

        drawsegment(p_anterior, p, putpixel, (0,0,0))



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
    
    for j in range(0, len(g)):
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
            draw_segment(p_anterior, p, putpixel, (0,0,0))



#def bspline2(grafo_control):
 #   for x in range(pasos):
        

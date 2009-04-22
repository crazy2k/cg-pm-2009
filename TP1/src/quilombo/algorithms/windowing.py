from core.windows import ViewPort

def WindowingMatrix(old_viewport, new_viewport):
  
    xwi = old_viewport.getRefPoint()[0]
    xwd = old_viewport.getRefPoint()[0] + old_viewport.getWidth()
    ywa = old_viewport.getRefPoint()[1]
    ywb = old_viewport.getRefPoint()[1] + old_viewport.getHeight()
    xvi = new_viewport.getRefPoint()[0]
    xvd = new_viewport.getRefPoint()[0] + new_viewport.getWidth()
    yva = new_viewport.getRefPoint()[1]
    yvb = new_viewport.getRefPoint()[1] + new_viewport.getHeight()
    
    fx = float((xvd - xvi))/(xwd - xwi)
    fy = float((yva - yvb))/(ywa - ywb)
    tx = xvi - fx*xwi
    ty = yva - fy*ywa
    windowing_matrix = [[fx, 0, tx], [0, fy, ty], [0, 0, 1]]

    return windowing_matrix
    
    
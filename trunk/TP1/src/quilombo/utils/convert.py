import wx

def pilToBitmap(pil):
    return imageToBitmap(pilToImage(pil))

def imageToBitmap(image):
    return image.ConvertToBitmap()

def pilToImage(pil):
    image = wx.EmptyImage(pil.size[0], pil.size[1])
    image.SetData(pil.convert('RGB').tostring())
    return image


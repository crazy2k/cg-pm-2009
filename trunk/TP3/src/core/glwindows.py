import wx
import wx.glcanvas

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class GLFrame(wx.Frame):

    def __init__(self, id, title, size):
        wx.Frame.__init__(self, None, id, title, size = size)

        # BasicGLCanvas' creation
        attrib_list = (wx.glcanvas.WX_GL_RGBA, # RGBA
                       wx.glcanvas.WX_GL_DOUBLEBUFFER) # double-buffering

        self.glcanvas = BasicGLCanvas(self, attrib_list)

        self.Centre()
        self.Show(True)


class BasicGLCanvas(wx.glcanvas.GLCanvas):

    def __init__(self, parent, attrib_list):
        wx.glcanvas.GLCanvas.__init__(self, parent = parent,
            attribList = attrib_list)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)

    def on_size(self, event):
        if self.GetContext():
            # make this canvas' context the current context 
            self.SetCurrent()

            # update OpenGL viewport's size
            size = event.GetSize()
            width = size.GetWidth()
            height = size.GetHeight()
            glViewport(0, 0, width, height)


    # XXX: No nos cierra lo del double-buffering. Cuando escribimos y cuando
    # solo pegamos el buffer?
    # XXX: Cuales de estas cosas pueden hacerse una unica vez al inicio y
    # cuales necesitan hacerse en cada on_paint?
    def on_paint(self, event):
        # a PaintDC has to be created when attending an EVT_PAINT event
        wx.PaintDC(self)

        # make this canvas' context the current context 
        self.SetCurrent()

        # smooth shading: colors of vertices are interpolated
        glShadeModel(GL_SMOOTH)

        # specify (0, 0, 0, 1) as clear values (for glClear())
        glClearColor(0, 0, 0, 1)

        # projection matrix will be the identity
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # modelview matrix will be the identity
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # enable depth test (otherwise, the depth buffer is not updated)
        glEnable(GL_DEPTH_TEST)
        # pixel passes if "incoming depth <= stored depth"
        glDepthFunc(GL_LEQUAL)

        # nicest opt. as quality of color and texture coordinate interpolation
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        # create a new quadrics object
        quad = gluNewQuadric()
        # quadrics rendered with quad will not have texturing
        gluQuadricTexture(quad, False)

        # make polygons be filled with color or just see the lines/points
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) 

        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # set current color
        glColor3f(0, 10, 0)

        # we save the matrix in the modelview mode for further use
        glPushMatrix()

        # we rotate 10 degrees around the X-axis
        angle = -70
        glRotated(angle, 1, 0, 0)

        # draw a cylinder
        gluCylinder(quad, 0.50, 0.01, 1.0, 26, 4)

        # get rid of the new matrix
        glPopMatrix()

        self.SwapBuffers()


    def on_erase_background(self, event):
        # this is to avoid flickering on Win
        pass

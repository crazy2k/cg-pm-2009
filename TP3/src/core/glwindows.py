import wx
import wx.glcanvas

from OpenGL.GL import *
from OpenGL.GLU import *

from math import sin, cos, pi

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

        self.context_initialized = False

        self.cam_elevation = 0
        self.cam_azimuth = 0

        self.radian_unit = pi/180

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)


    def on_size(self, event):
        if self.GetContext():
            # make this canvas' context the current context 
            self.SetCurrent()

            # update OpenGL viewport's size
            size = event.GetSize()
            width = size.GetWidth()
            height = size.GetHeight()
            glViewport(0, 0, width, height)

    def on_paint(self, event):
        """Attend the EVT_PAINT event."""

        # a PaintDC has to be created when attending an EVT_PAINT event
        wx.PaintDC(self)

        # make this canvas' context the current context 
        self.SetCurrent()

        if not self.context_initialized:
            self.initialize_context()

        # modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.position_camera(10, self.cam_elevation, self.cam_azimuth)

        # just see polygons' lines
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) 

        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.draw_axis()

        self.draw_tree(5)

        self.SwapBuffers()

    def initialize_context(self):
        # smooth shading: colors of vertices are interpolated
        glShadeModel(GL_SMOOTH)

        # specify (0, 0, 0, 1) as clear values (for glClear())
        glClearColor(0, 0, 0, 1)

        # projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1, 1, 1000)

        # enable depth test (otherwise, the depth buffer is not updated)
        glEnable(GL_DEPTH_TEST)
        # pixel passes if "incoming depth <= stored depth"
        glDepthFunc(GL_LEQUAL)

        # nicest opt. as quality of color and texture coordinate interpolation
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        self.context_initialized = True

    def position_camera(self, radius, elevation, azimuth):
        """Position the camera at a point P, according to the values for
        radius, elevation and azimuth given. The center (point the camera is
        aiming to) is assumed to be the origin (0, 0, 0). Angles should be
        given in radians.

        radius      -- distance from the origin to P
        elevation   -- pi/2 minus the inclination angle (inclination
                       is the angle between the zenith (0, 1, 0) and the
                       line formed between the origin and P)
        azimuth     -- angle between reference direction (0, 0, 1) and
                       the line from the origin to the projection of P on
                       the XZ-plane

        """
        
        inclination = pi/2 - elevation
        eye_x = round(radius*cos(azimuth)*sin(inclination))
        eye_y = round(radius*sin(azimuth)*sin(inclination))
        eye_z = round(radius*cos(inclination))

        print "camera position: ", eye_x, eye_y, eye_z
        
        # center (point at which the camera is aiming): always (0, 0, 0)
        # up vector: (0, 1, 0) (positive Y-axis)
        gluLookAt(eye_x, eye_y, eye_z, 0, 0, 0, 0, 1, 0)

    def draw_axis(self):
        glBegin(GL_LINES)

        # X-axis
        glColor3f(1, 0, 0)

        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)

        # Y-axis
        glColor3f(0, 1, 0)

        glVertex3f(0, 0, 0)
        glVertex3f(0, 1, 0)

        # Z-axis
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1)

        glEnd()

    def draw_tree(self, level):
        h = 0.5
        self.draw_cylinder(rad = 0.01, height = h)
        
        if level > 0:

            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(15, 0, 0, 1)

            self.draw_tree(level - 1)

            glPopMatrix()

            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(-15, 0, 0, 1)
            glRotatef(-20, 1, 0, 0)

            self.draw_tree(level - 1)

            glPopMatrix()

    def draw_cylinder(self, rad, height):
        glPushMatrix()

        # create a new quadrics object
        quad = gluNewQuadric()
        # quadrics rendered with quad will not have texturing
        gluQuadricTexture(quad, False)
        
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, rad, rad, height, 26, 4)
        
        gluDeleteQuadric(quad)

        glPopMatrix()

    def on_erase_background(self, event):
        # this is to avoid flickering on Win
        pass

    def on_key_down(self, event):
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_LEFT:
            self.cam_elevation += self.radian_unit
        elif keycode == wx.WXK_RIGHT:
            self.cam_elevation -= self.radian_unit
        elif keycode == wx.WXK_UP:
            self.cam_azimuth += self.radian_unit
        elif keycode == wx.WXK_DOWN:
            self.cam_azimuth -= self.radian_unit

        self.Refresh()


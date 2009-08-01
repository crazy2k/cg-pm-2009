import wx
import wx.glcanvas
import wx.xrc as xrc

from OpenGL.GL import *
from OpenGL.GLU import *

from core.glfigures import *

from math import sin, cos, pi

from utils.transformations import IDENTITY_4

class GLFrame(wx.Frame):

    def __init__(self, id, title):
        wx.Frame.__init__(self, None, id, title)

        #
        # panel loading from XRC
        # 
        res = xrc.XmlResource("view/panel.xrc")
        self.panel = res.LoadPanel(self, "ID_WXPANEL")

        panel_w, panel_h = self.panel.GetSize().Get()

        self.bind_panel_events(res)

        #
        # DrawingGLCanvas' creation
        #
        attrib_list = (wx.glcanvas.WX_GL_RGBA, # RGBA
                       wx.glcanvas.WX_GL_DOUBLEBUFFER) # double-buffering

        # size settings
        glcanvas_w = 500
        glcanvas_h = panel_h
        
        glcanvas_size = wx.Size(glcanvas_w, glcanvas_h)

        # creation itself
        self.glcanvas = DrawingGLCanvas(self, attrib_list, glcanvas_size)

        # the canvas is filled
        self.fill_canvas()

        # fill the panel with canvas' state
        self.fill_panel()


        # sizer's creation
        grid = wx.FlexGridSizer(rows = 0, cols = 2, vgap = 0, hgap = 0)
        grid.Add(self.glcanvas)
        grid.Add(self.panel)

        # frame initialization
        self.SetSize(wx.Size(glcanvas_w + panel_w, panel_h))
        self.SetSizer(grid)
        self.Centre()
        self.Show(True)

    def bind_panel_events(self, res):
        self.Bind(wx.EVT_CHECKBOX, self.on_check_perspective,
            id = xrc.XRCID("ID_CHECKBOX_PERSPECTIVE"))

    def on_check_perspective(self, event):
        old_value = self.glcanvas.perspective_projection_enabled
        self.glcanvas.perspective_projection_enabled = not old_value

        self.glcanvas.Refresh()

    def fill_panel(self):
        def set_boxes_values(boxes, values):
            length = len(boxes)

            if length != len(values):
                raise Error("Number of boxes and number of values must match.")
            for i in range(length):
                box = xrc.XRCCTRL(self, boxes[i])
                box.SetValue(values[i])

        c = self.glcanvas

        checkbox_perspective = xrc.XRCCTRL(self,
            "ID_CHECKBOX_PERSPECTIVE")

        state = c.perspective_projection_enabled
        checkbox_perspective.SetValue(state)

        boxes = ("ID_PERSPECTIVE_FOVY", "ID_PERSPECTIVE_ASPECT",
            "ID_PERSPECTIVE_ZNEAR", "ID_PERSPECTIVE_ZFAR")
        values = (c.perspective_projection_fovy,
            c.perspective_projection_aspect,
            c.perspective_projection_zNear,
            c.perspective_projection_zFar)
        set_boxes_values(boxes, values)

    
    def fill_canvas(self):
        generate_surface = GLCylinder.generate_trunk

        primary_values = {
            "branch_height": 1.2,
            "min_cant": 6,
            "max_cant": 7,
            "initial_radius": 0.06,
            "radius_diff": 0.01,
            "angle": 45
        }
        secondary_values = {
            "branch_height": 0.5,
            "min_cant": 2,
            "max_cant": 4,
            "initial_radius": 0.04,
            "radius_diff": 0.01,
            "angle":40
        }
        tertiary_values = {
            "branch_height": 0.2,
            "min_cant": 1,
            "max_cant": 3,
            "initial_radius": 0.03,
            "radius_diff": 0.005,
            "angle":35
        }
        
        self.glcanvas.add_figure(
            generate_tree(
                0, 4, primary_values, secondary_values,
                tertiary_values, IDENTITY_4, generate_surface,
                generate_surface
            )
        )



class DrawingGLCanvas(wx.glcanvas.GLCanvas):
    """A DrawingGLCanvas is basically a GLCanvas with some additional
    behaviour.

    The DrawingGLCanvas takes care of the following events that occur on it:
    * Resize event  -- when this event happens, the viewport of the canvas'
                       OpenGL context is updated accordingly
    * Repaint event -- OpenGL context initialization takes place if needed,
                       some settings are updated (like the camera position)
                       and all figures added with .add_figure() are drawn
                       (their .draw() method is called)
    * UI events     -- user-interface related events are handled

    """

    def __init__(self, parent, attrib_list, canvas_size):
        wx.glcanvas.GLCanvas.__init__(self, parent = parent,
            attribList = attrib_list, size = canvas_size)

        self.figures = []

        self.context_initialized = False

        self.cam_elevation = 0
        self.cam_azimuth = 0

        self.radian_unit = pi/180

        # the canvas has its default state when created
        self.restore_default_state()

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def restore_default_state(self):
        self.perspective_projection_enabled = ppe = True
        self.perspective_projection_fovy = 45
        self.perspective_projection_aspect = 1
        self.perspective_projection_zNear = 0.1
        self.perspective_projection_zFar = 1000

        self.ortho_projection_enabled = not ppe
        self.ortho_projection_left = 0
        self.ortho_projection_right = 1
        self.ortho_projection_bottom = 0
        self.ortho_projection_top = 1
        self.ortho_projection_nearVal = 0.1
        self.ortho_projection_farVal = 1000



    def add_figure(self, figure):
        self.figures.append(figure)

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

        # a PaintDC has to be created when attending an EVT_PAINT event
        wx.PaintDC(self)

        # make this canvas' context the current context 
        self.SetCurrent()

        if not self.context_initialized:
            self.initialize_context()

        # projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if self.perspective_projection_enabled:
            gluPerspective(self.perspective_projection_fovy,
                self.perspective_projection_aspect,
                self.perspective_projection_zNear,
                self.perspective_projection_zFar)

        # modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.position_camera(5, self.cam_elevation, self.cam_azimuth)

        # just see polygons' lines
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) 

        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for f in self.figures:
            f.paint()

        self.SwapBuffers()

    def initialize_context(self):
        # all normal vectors will be normalised
        glEnable(GL_NORMALIZE)
        # smooth shading: colors of vertices are interpolated
        glShadeModel(GL_SMOOTH)

        # specify (0, 0, 0, 1) as clear values (for glClear())
        glClearColor(0, 0, 0, 1)

        
        # enable depth test (otherwise, the depth buffer is not updated)
        glEnable(GL_DEPTH_TEST)
        # pixel passes if "incoming depth <= stored depth"
        glDepthFunc(GL_LEQUAL)

        # nicest opt. as quality of color and texture coordinate interpolation
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        # Lighting settings
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 50)
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 10, 0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

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
        eye_x = radius*cos(azimuth)*sin(inclination)
        eye_y = radius*sin(azimuth)*sin(inclination)
        eye_z = radius*cos(inclination)


        # center (point at which the camera is aiming): always (0, 0, 0)
        # up vector: (0, 1, 0) (positive Y-axis)
        gluLookAt(eye_x, eye_y, eye_z, 0, 1, 0, 0, 1, 0)

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


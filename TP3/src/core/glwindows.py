import wx
import wx.glcanvas
import wx.xrc as xrc

from OpenGL.GL import *
from OpenGL.GLU import *

from core.glfigures import *

from math import sin, cos, pi

from utils.transformations import IDENTITY_4


def gen_def_get(name):
    def def_get(self):
        return getattr(self, "_" + name)
    return def_get

def gen_def_set(name):
    def def_set(self, value):
        setattr(self, "_" + name, value)
    return def_set


def initialize_attributes(obj, attr_list):
    for attr in attr_list:
        setattr(obj, attr, 0)

class GLFrame(wx.Frame):

    def __init__(self, id, title):
        wx.Frame.__init__(self, None, id, title)

        # .fp_sliders_settings is a dictionary with the shape:
        # {
        #   "SLIDER_NAME": {
        #       "min": <minimum possible value for this option>,
        #       "max": <maximum possible value for this option>,
        #       "step": <step value (might be a float)>,
        #       "dest": <"canvas" or "tree"; represents the object whose
        #           attribute (given in "attr") will change according to
        #           the slider's value>,
        #       "attr": <name of the attribute that is going to be changed>,
        #       "has_dependents": <True if other sliders depend on this
        #           slider's attribute value; False otherwise>
        #   },
        #   ...
        # }

        self.fp_sliders_settings = {}
        self.load_fp_sliders_settings()

        self.checkboxes_settings = {}
        self.load_checkboxes_settings()

        # panel loading from XRC
        res = xrc.XmlResource("view/panel.xrc")
        self.panel = res.LoadPanel(self, "ID_WXPANEL")

        # save panel's width and height for further use
        panel_w, panel_h = self.panel.GetSize().Get()

        # attributes for DrawingGLCanvas
        attrib_list = (wx.glcanvas.WX_GL_RGBA, # RGBA
                       wx.glcanvas.WX_GL_DOUBLEBUFFER) # double-buffering

        glcanvas_w = 500
        glcanvas_h = 500
        glcanvas_size = wx.Size(glcanvas_w, glcanvas_h)

        self.glcanvas = DrawingGLCanvas(self, attrib_list, glcanvas_size)
 
        # tree's settings are stored as attributes in this object
        self.tree_settings = TreeSettings()

        # the canvas is filled (drawable objects are put into it)
        self.fill_canvas()

        # fill the panel with canvas' and tree's state
        self.fill_panel()

        self.bind_panel_events(res)

        # sizer's creation
        grid = wx.FlexGridSizer(rows = 0, cols = 2, vgap = 0, hgap = 0)
        grid.Add(self.glcanvas)
        grid.Add(self.panel)

        # frame initialization
        self.SetSize(wx.Size(glcanvas_w + panel_w, glcanvas_h))
        self.SetSizer(grid)
        self.Centre()
        self.Show(True)

    def bind_panel_events(self, res):
        # bind checkboxes' events
        cb_names = [c for c in self.checkboxes_settings.iterkeys()]
        for c_name in cb_names:
            self.Bind(wx.EVT_CHECKBOX, self.on_check,
                id = xrc.XRCID(c_name))
        
        # bind sliders' events
        sliders_names = [s for s in self.fp_sliders_settings.iterkeys()]
        for s_name in sliders_names:
            # all sliders' events are binded to the same function
            self.Bind(wx.EVT_SCROLL, self.on_scroll_slider,
                id = xrc.XRCID(s_name))

    def _set_canvas_option(self, attr_name, attr_value):
        setattr(self.glcanvas, attr_name, attr_value)
        self.glcanvas.Refresh()

    def _set_tree_option(self, attr_name, attr_value):
        setattr(self.tree_settings, attr_name, attr_value)
        self.glcanvas.clear()
        self.fill_canvas()
        self.glcanvas.Refresh()

    def on_check(self, event):
        # get checkbox's actual data
        c_name = event.EventObject.GetName()
        c_value = event.EventObject.GetValue()

        c_settings = self.checkboxes_settings[c_name]

        attr_name = c_settings["attr"]

        # update canvas'/tree's state
        if c_settings["dest"] == "canvas":
            self._set_canvas_option(attr_name, c_value)
        elif c_settings["dest"] == "tree":
            self._set_tree_option(attr_name, c_value)

        if c_settings["has_dependents"]:
            self.fill_panel()

    def on_scroll_slider(self, event):
        # get slider's actual data
        s_name = event.EventObject.GetName()
        s_value = event.EventObject.GetValue()

        # get slider's settings
        s_settings = self.fp_sliders_settings[s_name]
        attr_name = s_settings["attr"]

        # transform data to the real value
        attr_value = s_settings["step"]*s_value

        # update canvas'/tree's state
        if s_settings["dest"] == "canvas":
            self._set_canvas_option(attr_name, attr_value)
        elif s_settings["dest"] == "tree":
            self._set_tree_option(attr_name, attr_value)

        # if the control has dependents, we update the whole panel
        if s_settings["has_dependents"]:
            self.fill_panel()
        # else we update the accompanying text only
        else:
            self.update_acc_text(s_name, attr_value)

    def update_acc_text(self, s_name, value):
        text_ctrl = xrc.XRCCTRL(self, s_name + "_TEXT")
        text_ctrl.SetValue(str(value))

    def _set_controls_values(self, settings_dict):
        for k, v in settings_dict.iteritems():
            ctrl = xrc.XRCCTRL(self, k)
            ctrl.SetValue(v)

    def fill_panel(self):

        # set values to sliders
        for s_name, s_settings in self.fp_sliders_settings.iteritems():
            slider = xrc.XRCCTRL(self, s_name)

            # set min and max
            mult = int(1/s_settings["step"])
            slider.SetMin(mult*s_settings["min"])
            slider.SetMax(mult*s_settings["max"])

            # set actual value
            if s_settings["dest"] == "canvas":
                value = getattr(self.glcanvas, s_settings["attr"])
            elif s_settings["dest"] == "tree":
                value = getattr(self.tree_settings, s_settings["attr"])
            
            slider.SetValue(value*mult)

            # update accompanying text
            self.update_acc_text(s_name, value)

        # set values to checkboxes
        for c_name, c_settings in self.checkboxes_settings.iteritems():
            cb = xrc.XRCCTRL(self, c_name)

            # set actual value
            if c_settings["dest"] == "canvas":
                value = getattr(self.glcanvas, c_settings["attr"])
            elif c_settings["dest"] == "tree":
                value = getattr(self.tree_settings, c_settings["attr"])
            
            cb.SetValue(value)

        # set actual values to the rest of controls
        light_sources = self.glcanvas.get_light_sources()

        choice = xrc.XRCCTRL(self, "ID_CHOICE_LIGHT_SOURCE")
        choice.Clear()
        choice.AppendItems(light_sources)

    def load_fp_sliders_settings(self):
        self.fp_sliders_settings = {
            "ID_PERSPECTIVE_FOVY": {
                    "min": 0,
                    "max": 180,
                    "step": 0.1,
                    "attr": "perspective_projection_fovy",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_PERSPECTIVE_ASPECT": {
                    "min": 0.1,
                    "max": 50,
                    "step": 0.001,
                    "attr": "perspective_projection_aspect",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_PERSPECTIVE_ZNEAR": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "attr": "perspective_projection_zNear",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_PERSPECTIVE_ZFAR": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "attr": "perspective_projection_zFar",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_ORTHO_VL": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "attr": "ortho_projection_left",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_ORTHO_VR": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "attr": "ortho_projection_right",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_ORTHO_HB": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "attr": "ortho_projection_bottom",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_ORTHO_HT": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "attr": "ortho_projection_top",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_HEIGHT": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "attr": "height",
                    "dest": "tree",
                    "has_dependents": False
            },

            "ID_BRANCH1_SIZE": {
                    "min": 0,
                    "max": 10,
                    "step": 0.001,
                    "attr": "branch1_size",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH1_RADIUS": {
                    "min": 0,
                    "max": 0.2,
                    "step": 0.001,
                    "attr": "branch1_radius",
                    "dest": "tree",
                    "has_dependents": True,
            },
            "ID_BRANCH1_NARROWING": {
                    "min": 0,
                    "max": 0.1,
                    "step": 0.001,
                    "attr": "branch1_narrowing",
                    "dest": "tree",
                    "has_dependents": True
            },
            "ID_BRANCH1_BRANCHES_MAX": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "attr": "branch1_branches_max",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH1_BRANCHES_MIN": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "attr": "branch1_branches_min",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH1_BRANCHES_MAXANGLE": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "attr": "branch1_branches_maxangle",
                    "dest": "tree",
                    "has_dependents": False
            },

            "ID_BRANCH2_SIZE": {
                    "min": 0,
                    "max": 10,
                    "step": 0.001,
                    "attr": "branch2_size",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH2_RADIUS": {
                    "min": 0,
                    "max": 0.2,
                    "step": 0.001,
                    "attr": "branch2_radius",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH2_NARROWING": {
                    "min": 0,
                    "max": 0.1,
                    "step": 0.001,
                    "attr": "branch2_narrowing",
                    "dest": "tree",
                    "has_dependents": True
            },
            "ID_BRANCH2_BRANCHES_MAX": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "attr": "branch2_branches_max",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH2_BRANCHES_MIN": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "attr": "branch2_branches_min",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH2_BRANCHES_MAXANGLE": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "attr": "branch2_branches_maxangle",
                    "dest": "tree",
                    "has_dependents": False
            },

            "ID_BRANCH3_SIZE": {
                    "min": 0,
                    "max": 10,
                    "step": 0.001,
                    "attr": "branch3_size",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH3_RADIUS": {
                    "min": 0,
                    "max": 10,
                    "step": 0.001,
                    "attr": "branch3_radius",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH3_NARROWING": {
                    "min": 0,
                    "max": 0.1,
                    "step": 0.001,
                    "attr": "branch3_narrowing",
                    "dest": "tree",
                    "has_dependents": True
            },
            "ID_BRANCH3_BRANCHES_MAX": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "attr": "branch3_branches_max",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH3_BRANCHES_MIN": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "attr": "branch3_branches_min",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH3_BRANCHES_MAXANGLE": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "attr": "branch3_branches_maxangle",
                    "dest": "tree",
                    "has_dependents": False
            },
        }

    def load_checkboxes_settings(self):
        self.checkboxes_settings = {
            "ID_CHECKBOX_PERSPECTIVE": {
                "dest": "canvas",
                "attr": "perspective_projection_enabled",
                "has_dependents": True
            },
            "ID_CHECKBOX_ORTHO": {
                "dest": "canvas",
                "attr": "perspective_projection_enabled",
                "attr": "ortho_projection_enabled",
                "has_dependents": True
            }
        }


    def fill_canvas(self):
        """Fill the canvas in .glcanvas with objects using its .add_figure
        method.

        So far, the only added object is a tree generated using
        generate_tree(). Parameters passed to generate_tree() are obtained
        from .tree_settings."""
        
        generate_trunk = GLCylinder.generate_trunk
        generate_leaf = GLBezier.generate_leaf

        s = self.tree_settings

        primary_values = {
            "branch_height": s.branch1_size,
            "initial_radius": s.branch1_radius,
            "radius_diff": s.branch1_narrowing,
            "angle": s.branch1_branches_maxangle,
            "min_cant": s.branch1_branches_min,
            "max_cant": s.branch1_branches_max
        }

        secondary_values = {
            "branch_height": s.branch2_size,
            "initial_radius": s.branch2_radius,
            "radius_diff": s.branch2_narrowing,
            "angle": s.branch2_branches_maxangle,
            "min_cant": s.branch2_branches_min,
            "max_cant": s.branch2_branches_max
        }

        tertiary_values = {
            "branch_height": s.branch3_size,
            "initial_radius": s.branch3_radius,
            "radius_diff": s.branch3_narrowing,
            "angle": s.branch3_branches_maxangle,
            "min_cant": s.branch3_branches_min,
            "max_cant": s.branch3_branches_max
        }

        self.glcanvas.add_figure(
            generate_tree(
                0, s.height, primary_values,
                secondary_values, tertiary_values,
                IDENTITY_4, generate_trunk, generate_leaf, s.current_seed
            )
        )

class TreeSettings(object):
    def __init__(self):
        import time
        self.current_seed = time.time()

        # properties that don't have dependents
        trouble_free = ["size", "branches_maxangle",
            "branches_min", "branches_max"]
        # properties that have dependents
        troubled = ["radius", "narrowing"]

        list_full_props = lambda attrs: ["branch" + str(i) + "_" + attr \
            for attr in attrs for i in (1, 2, 3)]

        full_trouble_free = list_full_props(trouble_free)
        full_troubled = list_full_props(troubled)

        # properties that don't have dependents get default getters and setters
        for p in full_trouble_free:
            setattr(TreeSettings, p, property(fget = gen_def_get(p),
                fset = gen_def_set(p)))

        # properties that _have_ dependents get a default getter but their get
        # a special setter, called set_<property name>
        for p in full_troubled:
            setattr(TreeSettings, p, property(fget = gen_def_get(p),
                fset = getattr(self, "set_" + p)))

        initialize_attributes(self, ["_" + p for p in \
            full_trouble_free + full_troubled])

        self.height = 6

        self.branch1_size = 1.2
        self.branch1_radius = 0.06
        self.branch1_narrowing = 0.01
        self.branch1_branches_maxangle = 45
        self.branch1_branches_min = 6
        self.branch1_branches_max = 7

        self.branch2_size = 0.5
        self.branch2_radius = 0.04
        self.branch2_narrowing = 0.01
        self.branch2_branches_maxangle = 40
        self.branch2_branches_min = 2
        self.branch2_branches_max = 4

        self.branch3_size = 0.2
        self.branch3_radius = 0.03
        self.branch3_narrowing = 0.005
        self.branch3_branches_maxangle = 35
        self.branch3_branches_min = 1
        self.branch3_branches_max = 3

    def set_branch1_radius(self, s, value):

        print vars()

        self._branch1_radius = value

        self.branch2_radius = self.branch1_radius - self.branch1_narrowing

    def set_branch2_radius(self, s, value):
        self._branch2_radius = value

        self.branch3_radius = self.branch2_radius - self.branch2_narrowing

    def set_branch3_radius(self, s, value):
        self._branch3_radius = value

    def set_branch1_narrowing(self, s, value):
        self._branch1_narrowing = value

        self.branch2_radius = self.branch1_radius - self.branch1_narrowing

    def set_branch2_narrowing(self, s, value):
        self._branch2_narrowing = value

        self.branch3_radius = self.branch2_radius - self.branch2_narrowing

    def set_branch3_narrowing(self, s, value):
        self._branch3_narrowing = value


class DrawingGLCanvas(wx.glcanvas.GLCanvas, object):
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

        trouble_free = ["perspective_projection_fovy",
            "perspective_projection_aspect", "perspective_projection_zNear",
            "perspective_projection_zFar", "ortho_projection_left",
            "ortho_projection_right", "ortho_projection_bottom",
            "ortho_projection_top", "ortho_projection_nearVal",
            "ortho_projection_farVal"]

        # properties that don't have dependents get default getters and setters
        for p in trouble_free:
            setattr(DrawingGLCanvas, p, property(fget = gen_def_get(p),
                fset = gen_def_set(p)))

        troubled = ["perspective_projection_enabled",
            "ortho_projection_enabled"]

        # properties that _have_ dependents get a default getter but they get
        # a special setter, called set_<property name>
        for p in troubled:
            setattr(DrawingGLCanvas, p, property(fget = gen_def_get(p),
                fset = getattr(self, "set_" + p)))

        initialize_attributes(self, ["_" + p for p in trouble_free + troubled])

        # the canvas has its default state when created
        self.restore_default_state()

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def clear(self):
        self.figures = []

    def restore_default_state(self):
        self.perspective_projection_enabled = ppe = True
        self.perspective_projection_fovy = 45
        self.perspective_projection_aspect = 1
        self.perspective_projection_zNear = 0.1
        self.perspective_projection_zFar = 1000

        self.ortho_projection_enabled = not ppe
        self.ortho_projection_left = -2
        self.ortho_projection_right = 2
        self.ortho_projection_bottom = -2
        self.ortho_projection_top = 2.5
        self.ortho_projection_nearVal = 0.1
        self.ortho_projection_farVal = 1000

        self.light0_enabled = True

    def set_perspective_projection_enabled(self, s, value):
        self._perspective_projection_enabled = value

        nvalue = not value
        if self.ortho_projection_enabled != nvalue:
            self.ortho_projection_enabled = not value

    def set_ortho_projection_enabled(self, s, value):
        self._ortho_projection_enabled = value

        nvalue = not value
        if self.perspective_projection_enabled != nvalue:
            self.perspective_projection_enabled = not value

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

        if self.ortho_projection_enabled:
            glOrtho(self.ortho_projection_left, self.ortho_projection_right,
                self.ortho_projection_bottom, self.ortho_projection_top,
                self.ortho_projection_nearVal, self.ortho_projection_farVal)

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

    def get_light_sources(self):
        light_sources = ["GL_LIGHT" + str(i) for i in range(8)]
        return light_sources

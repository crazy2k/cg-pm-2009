import wx
import wx.glcanvas
import wx.xrc as xrc

from OpenGL.GL import *
from OpenGL.GLU import *

from core.glfigures import *

from math import sin, cos, pi

import time

from utils.transformations import IDENTITY_4


class GLFrame(wx.Frame):

    def __init__(self, id, title):
        wx.Frame.__init__(self, None, id, title)

        # .fp_sliders_settings is a dictionary with the shape:
        # {
        #   "<slider's name>": {
        #       "min": <minimum possible value for this option>,
        #       "max": <maximum possible value for this option>,
        #       "step": <step value (might be a float)>,
        #       "dest": <"canvas" or "tree"; represents the object whose
        #           attribute (given in "attr") will change according to
        #           the slider's value>,
        #       "condition": <frame's attribute whose value will be used to
        #           replace the string "XXX" in attr's value; or None>
        #       "attr": <name of the attribute that is going to be changed>,
        #       "has_dependents": <True if other sliders depend on this
        #           slider's attribute value; False otherwise>
        #   },
        #   ...
        # }

        self.fp_sliders_settings = {}
        self.load_fp_sliders_settings()

        # .checkboxes_settings is a dictionary with the shape:
        # {
        #   "<checkbox's name>": {
        #       "dest": "<"canvas" or "tree"; represents the object whose
        #           attribute (given in "attr") will change according to
        #           the slider's value>",
        #       "condition": <frame's attribute whose value will be used to
        #           replace the string "XXX" in attr's value; or None>,
        #       "attr": <name of the attribute that is going to be changed>,
        #       "has_dependents": <True if other sliders depend on this
        #           slider's attribute value; False otherwise>
        #   },
        #   ...
        # }

        self.checkboxes_settings = {}
        self.load_checkboxes_settings()

        self.trunk_surfaces = [GLCylinder, GLBezier, GLNURBS, GLSweptSurface,
            GLSurfaceOfRevolution]

        # .current_light represents the light that is currently selected in
        # the dialog (valid values are 0 to 7)
        self.current_light = 0

        # .current_trunk_surface is an index in .trunk_surfaces; represents
        # the surface that is currently being used for trunks
        self.current_trunk_surface = 0

        # panel loading from XRC
        res = xrc.XmlResource("view/panel.xrc")
        self.panel = res.LoadPanel(self, "ID_WXPANEL")

        # save panel's width and height for further use
        panel_w, panel_h = self.panel.GetSize().Get()

        # attributes for DrawingGLCanvas
        attrib_list = (wx.glcanvas.WX_GL_RGBA, # RGBA
                       wx.glcanvas.WX_GL_DOUBLEBUFFER) # double-buffering

        glcanvas_w = 500
        glcanvas_h = panel_h
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
        self.SetSize(wx.Size(glcanvas_w + panel_w, max(glcanvas_h, panel_h)))
        self.SetSizer(grid)
        self.Centre()
        self.Show(True)

    def bind_panel_events(self, res):
        "Bind all panel's events with their respective event handlers."
    
        def bind(elem_names, event, event_handler):
            for elem_name in elem_names:
                self.Bind(event, event_handler, id = xrc.XRCID(elem_name))

        # bind checkboxes' events
        cb_names = self.checkboxes_settings.iterkeys()
        bind(cb_names, wx.EVT_CHECKBOX, self.on_check)
        
        # bind sliders' events
        sliders_names = self.fp_sliders_settings.iterkeys()
        bind(sliders_names, wx.EVT_SCROLL, self.on_scroll_slider)

        # bind choice's event
        choices_names = ["ID_CHOICE_LIGHT_SOURCE",
            "ID_CHOICE_TREE_TRUNK_SURFACE"]
        bind(choices_names, wx.EVT_CHOICE, self.on_choice)

        # bind colour pickers' events
        pickers_suffixes = ["NAT_AMBIENT", "NAT_DIFFUSE", "NAT_SPECULAR",
            "TREE_TRUNK", "TREE_LEAVES"]
        pickers_names = ["ID_CPICKER_" + p for p in pickers_suffixes]
        bind(pickers_names, wx.EVT_COLOURPICKER_CHANGED, self.on_pick)

        # bind "regenerate" button event
        bind(("ID_REGENERATE",), wx.EVT_BUTTON, self.on_click_button)

    def _get_final_attr_name(self, settings):
        """Get final attribute's name from settings dictionary.

        If the condition (given in settings["condition"]) is None, the
        value contained in settings["attr"] is returned. Otherwise, the
        following actions take place:
        * attribute's name (attr_name) is obtained from settings["attr"]
        * the value (cond_value) of GLFrame's attribute whose name is in
          settings["condition"] is obtained
        * attr_name is processed and the result is returned
        
        Processing means replacing each ocurrence of the string "XXX" in
        attr_name with cond_value.

        """
        attr_name = settings["attr"]

        cond = settings["condition"]
        if cond is not None:
            cond_value = str(getattr(self, cond))

            attr_name = attr_name.replace("XXX", cond_value)
            
        return attr_name

    def _set_attr(self, settings, attr_name, attr_value):
        dest = settings["dest"]
        if dest == "tree":
            self._set_tree_attr(attr_name, attr_value)
        elif dest == "canvas":
            self._set_canvas_attr(attr_name, attr_value)

    def _set_canvas_attr(self, attr_name, attr_value):
        setattr(self.glcanvas, attr_name, attr_value)
        self.glcanvas.Refresh()

    def _set_tree_attr(self, attr_name, attr_value):
        setattr(self.tree_settings, attr_name, attr_value)
        self._refill_canvas()

    def _refill_canvas(self):
        self.glcanvas.clear()
        self.fill_canvas()
        self.glcanvas.Refresh()

    def on_check(self, event):
        "Attend checkboxes' events."

        # get checkbox's data
        c_name = event.EventObject.GetName()
        c_value = event.EventObject.GetValue()

        c_settings = self.checkboxes_settings[c_name]

        # get the processed (if needed) attribute's name
        attr_name = self._get_final_attr_name(c_settings)

        # update canvas'/tree's state
        self._set_attr(c_settings, attr_name, c_value)

        if c_settings["has_dependents"]:
            self.fill_panel()

    def on_pick(self, event):
        "Attend color pickers' events."

        cpkr = event.EventObject
        col = cpkr.GetColour()
        name = cpkr.GetName()

        if name.startswith("ID_CPICKER_NAT"):
            prop = name.replace("ID_CPICKER_", "").lower()
            curr_light = str(self.current_light)

            normalised_color = int_col_to_fp(col.Get())
            self._set_canvas_attr("light" + curr_light + "_" + prop,
                normalised_color)

        elif name.startswith("ID_CPICKER_TREE"):
            if name.startswith("ID_CPICKER_TREE_TRUNK"):
                attr_name = "trunk_color"
            elif name.startswith("ID_CPICKER_TREE_LEAVES"):
                attr_name = "leaves_color"

            normalised_color = int_col_to_fp(col.Get())
            self._set_tree_attr(attr_name, normalised_color)

    def on_click_button(self, event):
        button = event.EventObject
        button_name = button.GetName()

        if button_name == "ID_REGENERATE":
            self._set_tree_attr("current_seed", time.time())

    def on_choice(self, event):
        "Attend choice controls' events."

        choice_ctrl = event.EventObject
        name = choice_ctrl.GetName()

        if name == "ID_CHOICE_LIGHT_SOURCE":
            self.current_light = event.GetInt()
            self.fill_panel()

        if name == "ID_CHOICE_TREE_TRUNK_SURFACE":
            self.current_trunk_surface = event.GetInt()
            self._refill_canvas()

    def on_scroll_slider(self, event):
        "Attend sliders' events."

        # get slider's actual data
        s_name = event.EventObject.GetName()
        s_value = event.EventObject.GetValue()

        # get slider's settings
        s_settings = self.fp_sliders_settings[s_name]

        attr_name = self._get_final_attr_name(s_settings)

        # transform data to the real value
        attr_value = s_settings["step"]*s_value

        # update canvas'/tree's state
        self._set_attr(s_settings, attr_name, attr_value)

        # if the control has dependents, we update the whole panel
        if s_settings["has_dependents"]:
            self.fill_panel()
        # else we update the accompanying text only
        else:
            self.update_acc_text(s_name, attr_value)

    def update_acc_text(self, s_name, value):
        text_ctrl = xrc.XRCCTRL(self, s_name + "_TEXT")
        text_ctrl.SetValue(str(value))

    def fill_panel(self):
        "Fill the panel with current canvas' and tree's state."

        # set values to sliders
        for s_name, s_settings in self.fp_sliders_settings.iteritems():
            slider = xrc.XRCCTRL(self, s_name)

            # set min and max
            mult = int(1/s_settings["step"])
            slider.SetMin(mult*s_settings["min"])
            slider.SetMax(mult*s_settings["max"])

            attr_name = self._get_final_attr_name(s_settings)

            # set actual value
            if s_settings["dest"] == "canvas":
                value = getattr(self.glcanvas, attr_name)
            elif s_settings["dest"] == "tree":
                value = getattr(self.tree_settings, attr_name)
            
            slider.SetValue(value*mult)

            # update accompanying text
            self.update_acc_text(s_name, value)

        # set values to checkboxes
        for c_name, c_settings in self.checkboxes_settings.iteritems():
            cb = xrc.XRCCTRL(self, c_name)

            attr_name = self._get_final_attr_name(c_settings)

            # set actual value
            if c_settings["dest"] == "canvas":
                value = getattr(self.glcanvas, attr_name)
            elif c_settings["dest"] == "tree":
                value = getattr(self.tree_settings, attr_name)
            
            cb.SetValue(value)

        # set values to the choice controls
        light_sources = self.glcanvas.get_light_sources()

        choice = xrc.XRCCTRL(self, "ID_CHOICE_LIGHT_SOURCE")
        choice.Clear()
        choice.AppendItems(light_sources)
        choice.SetSelection(self.current_light)

        trunk_surfaces = [s.name for s in self.trunk_surfaces]

        choice = xrc.XRCCTRL(self, "ID_CHOICE_TREE_TRUNK_SURFACE")
        choice.Clear()
        choice.AppendItems(trunk_surfaces)
        choice.SetSelection(self.current_trunk_surface)

        # set values to colour pickers

        def get_current_light_colour(propertie):
            """Get (r, g, b) tuple which represents the colour of the given
            propertie for the light currently selected."""
            ln = str(self.current_light)
            return getattr(self.glcanvas, "light" + ln + "_" + propertie)

        cpkr = xrc.XRCCTRL(self, "ID_CPICKER_NAT_AMBIENT")
        r, g, b = fp_col_to_int(get_current_light_colour("nat_ambient"))
        col = wx.Colour(r, g, b)
        cpkr.SetColour(col)

        cpkr = xrc.XRCCTRL(self, "ID_CPICKER_NAT_DIFFUSE")
        r, g, b = fp_col_to_int(get_current_light_colour("nat_diffuse"))
        col = wx.Colour(r, g, b)
        cpkr.SetColour(col)

        cpkr = xrc.XRCCTRL(self, "ID_CPICKER_NAT_SPECULAR")
        r, g, b = fp_col_to_int(get_current_light_colour("nat_specular"))
        col = wx.Colour(r, g, b)
        cpkr.SetColour(col)

        cpkr = xrc.XRCCTRL(self, "ID_CPICKER_TREE_TRUNK")
        cpkr.SetColour(fp_col_to_int(self.tree_settings.trunk_color))
        
        cpkr = xrc.XRCCTRL(self, "ID_CPICKER_TREE_LEAVES")
        cpkr.SetColour(fp_col_to_int(self.tree_settings.leaves_color))

    def load_fp_sliders_settings(self):
        self.fp_sliders_settings = {
            "ID_PERSPECTIVE_FOVY": {
                    "min": 0,
                    "max": 180,
                    "step": 0.1,
                    "condition": None,
                    "attr": "perspective_projection_fovy",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_PERSPECTIVE_ASPECT": {
                    "min": 0.1,
                    "max": 50,
                    "step": 0.001,
                    "condition": None,
                    "attr": "perspective_projection_aspect",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_PERSPECTIVE_ZNEAR": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "condition": None,
                    "attr": "perspective_projection_zNear",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_PERSPECTIVE_ZFAR": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "condition": None,
                    "attr": "perspective_projection_zFar",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_ORTHO_VL": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": None,
                    "attr": "ortho_projection_left",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_ORTHO_VR": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": None,
                    "attr": "ortho_projection_right",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_ORTHO_HB": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": None,
                    "attr": "ortho_projection_bottom",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_ORTHO_HT": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": None,
                    "attr": "ortho_projection_top",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_HEIGHT": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "condition": None,
                    "attr": "height",
                    "dest": "tree",
                    "has_dependents": False
            },

            "ID_BRANCH1_SIZE": {
                    "min": 0,
                    "max": 3,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch1_size",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH1_RADIUS": {
                    "min": 0,
                    "max": 0.1,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch1_radius",
                    "dest": "tree",
                    "has_dependents": True,
            },
            "ID_BRANCH1_NARROWING": {
                    "min": 0.001,
                    "max": 0.1,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch1_narrowing",
                    "dest": "tree",
                    "has_dependents": True
            },
            "ID_BRANCH1_BRANCHES_MAX": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "condition": None,
                    "attr": "branch1_branches_max",
                    "dest": "tree",
                    "has_dependents": True
            },
            "ID_BRANCH1_BRANCHES_MIN": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "condition": None,
                    "attr": "branch1_branches_min",
                    "dest": "tree",
                    "has_dependents": True
            },
            "ID_BRANCH1_BRANCHES_MAXANGLE": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "condition": None,
                    "attr": "branch1_branches_maxangle",
                    "dest": "tree",
                    "has_dependents": False
            },

            "ID_BRANCH2_SIZE": {
                    "min": 0,
                    "max": 3,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch2_size",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH2_RADIUS": {
                    "min": 0,
                    "max": 0.1,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch2_radius",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH2_NARROWING": {
                    "min": 0.001,
                    "max": 0.1,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch2_narrowing",
                    "dest": "tree",
                    "has_dependents": True
            },
            "ID_BRANCH2_BRANCHES_MAX": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "condition": None,
                    "attr": "branch2_branches_max",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH2_BRANCHES_MIN": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "condition": None,
                    "attr": "branch2_branches_min",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH2_BRANCHES_MAXANGLE": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "condition": None,
                    "attr": "branch2_branches_maxangle",
                    "dest": "tree",
                    "has_dependents": False
            },

            "ID_BRANCH3_SIZE": {
                    "min": 0,
                    "max": 3,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch3_size",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH3_RADIUS": {
                    "min": 0,
                    "max": 0.1,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch3_radius",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH3_NARROWING": {
                    "min": 0.001,
                    "max": 0.1,
                    "step": 0.001,
                    "condition": None,
                    "attr": "branch3_narrowing",
                    "dest": "tree",
                    "has_dependents": True
            },
            "ID_BRANCH3_BRANCHES_MAX": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "condition": None,
                    "attr": "branch3_branches_max",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH3_BRANCHES_MIN": {
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "condition": None,
                    "attr": "branch3_branches_min",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_BRANCH3_BRANCHES_MAXANGLE": {
                    "min": 0,
                    "max": 50,
                    "step": 0.01,
                    "condition": None,
                    "attr": "branch3_branches_maxangle",
                    "dest": "tree",
                    "has_dependents": False
            },
            "ID_POS_X": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": "current_light",
                    "attr": "lightXXX_pos_x",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_POS_Y": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": "current_light",
                    "attr": "lightXXX_pos_y",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_POS_Z": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": "current_light",
                    "attr": "lightXXX_pos_z",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_DIR_X": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": "current_light",
                    "attr": "lightXXX_dir_x",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_DIR_Y": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": "current_light",
                    "attr": "lightXXX_dir_y",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_DIR_Z": {
                    "min": -10,
                    "max": 10,
                    "step": 0.01,
                    "condition": "current_light",
                    "attr": "lightXXX_dir_z",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_LIGHT_EXP": {
                    "min": 0,
                    "max": 128,
                    "step": 0.01,
                    "condition": "current_light",
                    "attr": "lightXXX_exponent",
                    "dest": "canvas",
                    "has_dependents": False
            },
            "ID_LIGHT_MAXANGLE": {
                    "min": 0,
                    "max": 90,
                    "step": 0.01,
                    "condition": "current_light",
                    "attr": "lightXXX_maxangle",
                    "dest": "canvas",
                    "has_dependents": False
            },
        }

    def load_checkboxes_settings(self):
        self.checkboxes_settings = {
            "ID_CHECKBOX_PERSPECTIVE": {
                "dest": "canvas",
                "condition": None,
                "attr": "perspective_projection_enabled",
                "has_dependents": True
            },
            "ID_CHECKBOX_ORTHO": {
                "dest": "canvas",
                "condition": None,
                "attr": "ortho_projection_enabled",
                "has_dependents": True
            },
            "ID_CHECKBOX_LIGHT_ENABLE": {
                "dest": "canvas",
                "condition": "current_light",
                "attr": "lightXXX_enabled",
                "has_dependents": False
            }
        }


    def fill_canvas(self):
        """Fill the canvas in .glcanvas with objects using its .add_figure
        method.

        So far, the only added object is a tree generated using
        core.glfigures.generate_tree(). Parameters passed to generate_tree()
        are obtained from .tree_settings.
        
        """
        
        trunk_surface = self.trunk_surfaces[self.current_trunk_surface]
        generate_trunk = trunk_surface.generate_trunk
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
                s.height, primary_values,
                secondary_values, tertiary_values,
                IDENTITY_4, generate_trunk, generate_leaf, s.current_seed,
                s.trunk_color, s.leaves_color, 0
            )
        )

class TreeSettings(object):
    def __init__(self):
        self.current_seed = time.time()

        # properties that don't have dependents
        trouble_free = ["size", "branches_maxangle"]
        # properties that have dependents
        troubled = ["radius", "narrowing", "branches_min", "branches_max"]

        list_full_props = lambda attrs: ["branch" + str(i) + "_" + attr \
            for attr in attrs for i in (1, 2, 3)]

        full_trouble_free = list_full_props(trouble_free)
        full_troubled = list_full_props(troubled)

        # properties that don't have dependents get default getters and setters
        for p in full_trouble_free:
            setattr(TreeSettings, p, property(fget = gen_def_get(p),
                fset = gen_def_set(p)))

        # properties that _have_ dependents get a default getter but they get
        # a special setter, called set_<property name>
        for p in full_troubled:
            setattr(TreeSettings, p, property(fget = gen_def_get(p),
                fset = getattr(TreeSettings, "set_" + p)))

        initialize_attributes(self, ["_" + p for p in \
            full_trouble_free + full_troubled])

        self.height = 6

        self.trunk_color = int_col_to_fp((55, 35, 0))
        self.leaves_color = int_col_to_fp((0, 95, 0))

        self._branch1_size = 1.2
        self._branch1_radius = 0.06
        self._branch1_narrowing = 0.021
        self._branch1_branches_maxangle = 45
        self._branch1_branches_min = 6
        self._branch1_branches_max = 7

        self._branch2_size = 0.5
        self._branch2_radius = 0.039
        self._branch2_narrowing = 0.01
        self._branch2_branches_maxangle = 40
        self._branch2_branches_min = 2
        self._branch2_branches_max = 4

        self._branch3_size = 0.2
        self._branch3_radius = 0.029
        self._branch3_narrowing = 0.005
        self._branch3_branches_maxangle = 35
        self._branch3_branches_min = 1
        self._branch3_branches_max = 3

    def _get_height_calc(self):
        c = self.branch1_narrowing + self.branch2_narrowing - self.branch1_radius
        d = -self.branch3_narrowing

        r = float(c)/d + 2

        if int(r) == r:
            # border case
            r -= 1
        else:
            r = int(r)

        return r

    def set_branch1_radius(self, value):
        self._branch1_radius = value

        self.height = self._get_height_calc()

        self.branch2_radius = self.branch1_radius - self.branch1_narrowing

    def set_branch1_narrowing(self, value):
        self._branch1_narrowing = value

        self.height = self._get_height_calc()

        self.branch2_radius = self.branch1_radius - self.branch1_narrowing

    def set_branch1_branches_max(self, value):
        self._branch1_branches_max = value

        if value < self.branch1_branches_min:
            self.branch1_branches_min = value

    def set_branch1_branches_min(self, value):
        self._branch1_branches_min = value
        
        if value > self.branch1_branches_max:
            self.branch1_branches_max = value

    def set_branch2_radius(self, value):
        self._branch2_radius = value

        self.branch3_radius = self.branch2_radius - self.branch2_narrowing

    def set_branch2_narrowing(self, value):
        self._branch2_narrowing = value

        self.height = self._get_height_calc()

        self.branch3_radius = self.branch2_radius - self.branch2_narrowing

    def set_branch2_branches_max(self, value):
        self._branch1_branches_max = value

        if value < self.branch1_branches_min:
            self.branch1_branches_min = value

    def set_branch2_branches_min(self, value):
        self._branch1_branches_min = value
        
        if value > self.branch1_branches_max:
            self.branch1_branches_max = value

    def set_branch3_radius(self, value):
        self._branch3_radius = value

    def set_branch3_narrowing(self, value):
        self._branch3_narrowing = value

        self.height = self._get_height_calc()

    def set_branch3_branches_max(self, value):
        self._branch1_branches_max = value

        if value < self.branch1_branches_min:
            self.branch1_branches_min = value

    def set_branch3_branches_min(self, value):
        self._branch1_branches_min = value
        
        if value > self.branch1_branches_max:
            self.branch1_branches_max = value


class DrawingGLCanvas(wx.glcanvas.GLCanvas, object):
    """A DrawingGLCanvas is basically a GLCanvas with some additional
    behaviour.

    The DrawingGLCanvas takes care of the following events that occur on it:
    * Resize event  -- when this event happens, the viewport of the canvas'
                       OpenGL context is updated accordingly
    * Repaint event -- OpenGL context initialization takes place if needed,
                       some settings are updated (like the camera position)
                       and all figures added with .add_figure() are drawn
                       (their .paint() method is called)
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
                fset = getattr(DrawingGLCanvas, "set_" + p)))

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
        self.light0_nat_ambient = int_col_to_fp((150, 150, 150))
        self.light0_nat_diffuse = int_col_to_fp((150, 150, 150))
        self.light0_nat_specular = int_col_to_fp((200, 200, 200))
        self.light0_exponent = 10
        self.light0_maxangle = 45
        self.light0_pos_x = 0
        self.light0_pos_y = 0
        self.light0_pos_z = 10
        self.light0_dir_x = 0
        self.light0_dir_y = 0
        self.light0_dir_z = -1

        lighting_default_values = {
            "enabled": False,
            "nat_ambient": int_col_to_fp((100, 100, 100)),
            "nat_diffuse": int_col_to_fp((200, 200, 200)),
            "nat_specular": int_col_to_fp((200, 200, 200)),
            "exponent": 10,
            "maxangle": 45,
            "pos_x": 0,
            "pos_y": 10,
            "pos_z": 0,
            "dir_x": 0,
            "dir_y": -1,
            "dir_z": 0
        }

        for i in range(1, 8):
            for p in lighting_default_values.iterkeys():
                setattr(self, "light" + str(i) + "_" + p,
                    lighting_default_values[p])


    def set_perspective_projection_enabled(self, value):
        self._perspective_projection_enabled = value

        nvalue = not value
        if self.ortho_projection_enabled != nvalue:
            self.ortho_projection_enabled = not value

    def set_ortho_projection_enabled(self, value):
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

        self.setup_lighting()

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

    def setup_lighting(self):
        glEnable(GL_LIGHTING)

        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

        for li in self.get_light_sources():
            l = getattr(OpenGL.GL, li)

            # if li is GL_LIGHT0, then clean_lower_li is light0
            clean_lower_li = li.lower()[3:]

            full_prop_name = lambda prop: clean_lower_li + "_" + prop

            pos_x = getattr(self, full_prop_name("pos_x"))
            pos_y = getattr(self, full_prop_name("pos_y"))
            pos_z = getattr(self, full_prop_name("pos_z"))
            glLightfv(l, GL_POSITION, (pos_x, pos_y, pos_z, 1))

            nat_ambient = getattr(self, full_prop_name("nat_ambient"))
            glLightfv(l, GL_AMBIENT, nat_ambient + (1,))

            nat_diffuse = getattr(self, full_prop_name("nat_diffuse"))
            glLightfv(l, GL_DIFFUSE, nat_diffuse + (1,))

            nat_specular = getattr(self, full_prop_name("nat_specular"))
            glLightfv(l, GL_SPECULAR, nat_specular + (1,))

            dir_x = getattr(self, full_prop_name("dir_x"))
            dir_y = getattr(self, full_prop_name("dir_y"))
            dir_z = getattr(self, full_prop_name("dir_z"))
            glLightfv(l, GL_SPOT_DIRECTION, (dir_x, dir_y, dir_z, 1))

            exp = getattr(self, full_prop_name("exponent"))
            glLightfv(l, GL_SPOT_EXPONENT, exp)

            maxangle = getattr(self, full_prop_name("maxangle"))
            glLightfv(l, GL_SPOT_CUTOFF, maxangle)

            light_enabled = getattr(self, full_prop_name("enabled"))
            if light_enabled:
                glEnable(l)
            else:
                glDisable(l)

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

        # center (point at which the camera is aiming): (0, 1, 0)
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

def gen_def_get(name):
    "Generate a 'default getter' for the attribute named '_' + name."
    def def_get(self):
        return getattr(self, "_" + name)
    return def_get

def gen_def_set(name):
    def def_set(self, value):
        setattr(self, "_" + name, value)
    return def_set

def initialize_attributes(obj, attr_list):
    for attr in attr_list:
        setattr(obj, attr, 0.01)


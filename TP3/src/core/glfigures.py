from OpenGL.GL import *
from OpenGL.GLU import *

from utils.transformations import *

from numpy import pi, matrix

import random

class Drawable:
    """A Drawable is simply something that can be drawn."""

    def draw(self):
        raise NotImplementedError


class SceneNode:
    
    def __init__(self, transformation, obj):
        self.transformation = transformation
        self.obj = obj

        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def paint(self):

        glPushMatrix()

        self.apply_transformation()

        self.obj.draw()

        for s in self.children:
            s.paint()

        glPopMatrix()

    def apply_transformation(self):
        raise NotImplementedError


class GLSceneNode(SceneNode):
    
    def __init__(self, transformation, obj):
        SceneNode.__init__(self, transformation, obj)

    def apply_transformation(self):
        glMultMatrixd(self.transformation.transpose())

        
def generate_tree(actual_level, height, branch_height, min_cant, max_cant, bottom_radius, top_radius, angle, transformation, generate_trunk):
    # generate a node with a new trunk into it, and make
    # initial_transformation its associated transformation
    
    trunk = generate_trunk(bottom_radius, top_radius, branch_height)
    node = GLSceneNode(transformation, trunk)
    
    if actual_level < height:
        cant = int(random.random()*float(max_cant - min_cant)) + min_cant
        for i in range (cant):
                angle_x = int(random.random()*float(2*angle) - float(angle))
                angle_z = int(random.random()*float(2*angle) - float(angle))
                next_transformation = translation(trunk.endpoint()) * rotation(degree2radians(angle_z), "Z") * rotation(degree2radians(angle_x), "X")
                node.add_child(generate_tree(actual_level + 1, height, branch_height, min_cant, max_cant, 2*bottom_radius - top_radius, bottom_radius, angle, next_transformation, generate_trunk))
    return node

    
class GLCylinder:

    def __init__(self, bottom_radius, top_radius, height):
        self.bottom_radius = bottom_radius
        self.top_radius = top_radius
        self.height = height
                
    def draw(self):
        glPushMatrix()

        # create a new quadrics object
        quad = gluNewQuadric()
        # quadrics rendered with quad will not have texturing
        gluQuadricTexture(quad, False)
        
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, self.top_radius, self.bottom_radius, self.height, 26, 4)
        
        gluDeleteQuadric(quad)

        glPopMatrix()

    def endpoint(self):
        return (0, self.height, 0)

    @classmethod
    def generate(cls, bottom_radius, top_radius, height):
        c = GLCylinder(bottom_radius, top_radius, height)
        return c


class GLSweptSurface:
    pass


class GLSurfaceOfRevolution:
    
    def __init__(self, function, eval_steps, rotation_steps):
        """Construct a closed surface of revolution which will be drawn
        around the Y-axis using OpenGL.
        
        function        -- function that defines the curve to be rotated
                           around the Y-axis to create the surface
        eval_steps      -- integer number that defines the number of times
                           the curve will be evaluated
        rotation_steps  -- integer number that defines de number of times
                           the curve will be rotated

        The function receives a number from 0 to 1, and gives (x, y) pairs
        (points on the XY-plane).
        """

        self.function = function
        self.eval_steps = eval_steps
        self.rotation_steps = rotation_steps

        self.eval_step = 1.0/self.eval_steps
        self.rotation_step = 2*pi/self.rotation_steps

    def draw(self):
        fst_rotation_angle = 0
        sec_rotation_angle = self.rotation_step 
        for x in range(self.rotation_steps):

            curr_eval_number = 0
            for y in range(self.eval_steps):
                # curr_point and next_point are two contiguous points on the
                # curve that lies on the XY-plane
                p = self.function(curr_eval_number)
                curr_point = (p[0], p[1], 0, 1)

                curr_eval_number += self.eval_step

                p = self.function(curr_eval_number)
                next_point = (p[0], p[1], 0, 1)

                # transform points into 1x4 matrixes
                curr_point = matrix(curr_point).transpose()
                next_point = matrix(next_point).transpose()

                # get points on the first curve
                curr_point_fst = rotation(fst_rotation_angle, "Y")*curr_point
                next_point_fst = rotation(fst_rotation_angle, "Y")*next_point

                # get points on the second curve
                curr_point_sec = rotation(sec_rotation_angle, "Y")*curr_point
                next_point_sec = rotation(sec_rotation_angle, "Y")*next_point

                # make precision arrangements
                self.precision_correction(curr_point_fst)
                self.precision_correction(next_point_fst)
                self.precision_correction(curr_point_sec)
                self.precision_correction(next_point_sec)

                # draw the 4-sided polygon                
                glBegin(GL_QUAD_STRIP)

                if y == 0:
                    glVertex3d(curr_point_fst[0], curr_point_fst[1], curr_point_fst[2])
                    glVertex3d(curr_point_sec[0], curr_point_sec[1], curr_point_sec[2])

                glVertex3d(next_point_fst[0], next_point_fst[1], next_point_fst[2])
                glVertex3d(next_point_sec[0], next_point_sec[1], next_point_sec[2])


                glEnd()

            # angles are increased in self.rotation_step
            fst_rotation_angle = sec_rotation_angle
            sec_rotation_angle += self.rotation_step

    def precision_correction(self, iterable):
        for i in range(len(iterable)):
            x = iterable[i]

            # see it as a positive number
            if x < 0:
                x = -x

            # if it's too small, it's changed to zero
            if x < 0.000000001:
                iterable[i] = 0

    def endpoint(self):
        return (0, self.function(1)[1], 0)

    @classmethod
    def generate(cls, bottom_radius, top_radius, height):
        function = lambda x: (bottom_radius, x*height)
        c = GLSurfaceOfRevolution(function, 1, 25)
        return c

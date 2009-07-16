from OpenGL.GL import *
from OpenGL.GLU import *

from utils.transformations import *

from numpy import pi, matrix, sin, size, sqrt, dot

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

    
class GLCylinder(Drawable):

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


class GLSweptSurface(Drawable):
    
    def __init__(self, curve_function, direction_function, rotation_function,
        curve_eval_steps, surface_eval_steps):
        """Construct a closed swept surface which will be drawn
        around the Y-axis using OpenGL.
        
        curve_function      -- function that defines the curve to be swept
        direction_function  -- function that defines the surface's direction
                               when drawing it
        rotation_function   -- function that defines how the curve will rotate
                               while the surface is crated
        curve_eval_steps    -- integer number that defines de number of times
                               the curve will be evaluated
        surface_eval_steps  -- integer number that defines de number of times
                               the curve will be drawn

        Functions receive a number from 0 to 1, and give, for each invocation:
        * an (x, y) pair (point on the XY-plane) corresponding to a point
          in the curve, in the case of the curve_function (thus, the
          curve_function is a parametric function that defines a curve on
          the XY-plane)
        * a translation matrix (might be a numpy.matrix) that will be used to
          translate the origin when drawing the curve, in the case of the
          direction_function
        * a rotation matrix (might be a numpy.matrix) that will be applied
          in order to rotate the curve before translating it according to
          the direction_function, in the case of the rotation_function

        It should be noted that the parameter in the curve_function has a
        different meaning than in both the direction_function and the
        rotation_function. In the first, it is used to describe the curve
        to be swept, whereas in the other two it is used as a surface's
        parameter.

        """

        self.curve_function = curve_function
        self.direction_function = direction_function
        self.rotation_function = rotation_function
        self.curve_eval_steps = curve_eval_steps
        self.surface_eval_steps = surface_eval_steps

        self.curve_eval_step = 1.0/self.curve_eval_steps
        self.surface_eval_step = 1/self.surface_eval_steps
    
    def draw(self):

        curr_curve_eval_number = 0
        for i in range(self.curve_eval_steps):
            # p1 and p2 are two (general) contiguous points on the curve
            p = self.curve_function(curr_curve_eval_number)
            p1 = (p[0], p[1], 0, 1)

            curr_curve_eval_number += self.curve_eval_step

            p = self.curve_function(curr_curve_eval_number)
            p2 = (p[0], p[1], 0, 1)
            
            # transform points into 1x4 matrixes
            p1 = matrix(p1).transpose()
            p2 = matrix(p2).transpose()

            curr_surface_eval_number = 0

            glBegin(GL_QUAD_STRIP)
            for j in range(self.surface_eval_steps):

                # q1 and q2 are two contiguous points on a specific curve
                # on the surface

                q1 = copy.copy(p1)
                q2 = copy.copy(p2)

                q1 = self.rotation_function(curr_surface_eval_number)*q1
                q1 = self.direction_function(curr_surface_eval_number)*q1

                q2 = self.rotation_function(curr_surface_eval_number)*q2
                q2 = self.direction_function(curr_surface_eval_number)*q2

                # r1 and r2 are two contiguous points on the next curve
                # on the surface

                r1 = copy.copy(p1)
                r2 = copy.copy(p2)

                curr_surface_eval_number += self.surface_eval_step

                r1 = self.rotation_function(curr_surface_eval_number)*r1
                r1 = self.direction_function(curr_surface_eval_number)*r1

                r2 = self.rotation_function(curr_surface_eval_number)*r2
                r2 = self.direction_function(curr_surface_eval_number)*r2

                if j == 0:
                    glVertex3d()


class GLSurfaceOfRevolution(Drawable):
    
    def __init__(self, function, eval_steps, rotation_steps):
        """Construct a surface of revolution which will be drawn
        around the Y-axis using OpenGL.
        
        function        -- function that defines the curve to be rotated
                           around the Y-axis to create the surface
        eval_steps      -- integer number that defines the number of times
                           the curve will be evaluated
        rotation_steps  -- integer number that defines de number of times
                           the curve will be rotated

        The function receives a number from 0 to 1, and gives (x, y) pairs
        (points on the XY-plane) with x > 0.

        """

        self.function = function
        self.eval_steps = eval_steps
        self.rotation_steps = rotation_steps

        self.eval_step = 1.0/self.eval_steps
        self.rotation_step = 2*pi/self.rotation_steps

    def draw(self):
        fst_rotation_angle = 0
        sec_rotation_angle = self.rotation_step 
        for i in range(self.rotation_steps):

            curr_eval_number = 0
            glBegin(GL_QUAD_STRIP)
            for j in range(self.eval_steps):
                # curr_point and next_point are two contiguous points on the
                # curve that lies on the XY-plane
                p_curr = self.function(curr_eval_number)
                curr_point = self.twodseq_to_vector(p_curr)

                curr_eval_number += self.eval_step

                p_next = self.function(curr_eval_number)
                next_point = self.twodseq_to_vector(p_next)

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
                if j == 0:
                    # normals for the first two vertices will be the X-axis
                    # rotated accordingly and then normalized
                    x_axis = matrix((1, 0, 0, 1)).transpose()
                    n_fst = rotation(fst_rotation_angle, "Y")*x_axis
                    n_sec = rotation(sec_rotation_angle, "Y")*x_axis

                    # this isn't needed when GL_NORMALIZE is set
                    #n_fst = self.normalize(n_fst)
                    #n_sec = self.normalize(n_sec)

                    glNormal3d(n_fst.item(0), n_fst.item(1), n_fst.item(2))
                    glVertex3d(curr_point_fst.item(0), curr_point_fst.item(1),
                        curr_point_fst.item(2))

                    glNormal3d(n_sec.item(0), n_sec.item(1), n_sec.item(2))
                    glVertex3d(curr_point_sec.item(0), curr_point_sec.item(1),
                        curr_point_sec.item(2))

                # the tangent to the curve in p_next will have a direction
                # approximated by p_next - p_curr
                tg = matrix(p_next).transpose() - matrix(p_curr).transpose()

                # the normal for p_next will be a vector that is perpendicular
                # to its tangent line
                n = (tg.item(1), -tg.item(0))
                # n now lives on a 3D world
                n = self.twodseq_to_vector(n)

                # the normals will be this vector rotated accordingly
                # and then normalized
                n_fst = rotation(fst_rotation_angle, "Y")*n
                n_sec = rotation(sec_rotation_angle, "Y")*n

                # this isn't needed when GL_NORMALIZE is set
                #n_fst = self.normalize(n_fst)
                #n_sec = self.normalize(n_sec)

                glNormal3d(n_fst.item(0), n_fst.item(1), n_fst.item(2))
                glVertex3d(next_point_fst.item(0), next_point_fst.item(1),
                    next_point_fst.item(2))

                glNormal3d(n_sec.item(0), n_sec.item(1), n_sec.item(2))
                glVertex3d(next_point_sec.item(0), next_point_sec.item(1),
                    next_point_sec.item(2))

            glEnd()

            # angles are increased in self.rotation_step
            fst_rotation_angle = sec_rotation_angle
            sec_rotation_angle += self.rotation_step

    def normalize(self, v):
        """Normalizes a three-dimensional vector.

        This function expects the vector v to be a 3x1 or 4x1 matrix. If the
        latter, the last row will be ignored for the calculation. Once the
        normalised vector is obtained, a 4x1 matrix is returned, composed of
        the normalised vector plus a 1 in the last row.
        
        """

        v = matrix((v.item(0), v.item(1), v.item(2)))
        norm = sqrt(dot(v, v.transpose()).item(0))
        v_n = v/norm
        return matrix((v_n.item(0), v_n.item(1), v_n.item(2), 1)).transpose()

    def twodseq_to_vector(self, seq):
        point = (seq[0], seq[1], 0, 1)
        m = matrix(point)
        return m.transpose()

    def precision_correction(self, v):
        for i in range(len(v)):
            x = v.item(i)

            # see it as a positive number
            if x < 0:
                x = -x

            # if it's too small, it's changed to zero
            if x < 0.000000001:
                v.itemset(i, 0)

    def endpoint(self):
        return (0, self.function(1)[1], 0)

    @classmethod
    def generate(cls, bottom_radius, top_radius, height):
        function = lambda x: (bottom_radius, x*height)

        c = GLSurfaceOfRevolution(function, 15, 20)
        return c

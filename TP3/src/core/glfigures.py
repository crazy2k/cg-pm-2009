from OpenGL.GL import *
from OpenGL.GLU import *

from utils.transformations import *

from numpy import pi, matrix, cross, size, sqrt, dot

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
        """Construct a swept surface which will be drawn
        around the Y-axis using OpenGL.
        
        curve_function      -- function that defines the curve to be swept
        direction_function  -- function that defines the surface's direction
                               when drawing it
        rotation_function   -- function that defines how the curve will rotate
                               while the surface is created
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
          (beware the curve will be rotated to be on XZ-plane before, so these
          rotation matrices should rotate around the Y-axis)

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
        self.surface_eval_step = 1.0/self.surface_eval_steps

    def draw(self):

        curr_curve_eval_number = 0
        while curr_curve_eval_number <= 1:
            # p1 to p4 are (general) contiguous points on the curve
            d = self.curve_eval_step
            parms = (curr_curve_eval_number,
                     curr_curve_eval_number + d,
                     curr_curve_eval_number + 2*d,
                     curr_curve_eval_number + 3*d)

            p1, p2, p3, p4 = self.evaluate_points(parms)

            curr_curve_eval_number += d

            # since the curve will be swept through the Y-axis, points have
            # to be rotated 90 degrees around the X-axis (they're now points
            # on the XZ-plane)
            vectors = (p1, p2, p3, p4)
            angle = degree2radians(-90)
            p1, p2, p3, p4 = [rotation(angle, "X")*v for v in vectors]

            # the curr_surface_eval_number starts at a first nonexistent row;
            # this is because the vertices we're going to 
            curr_surface_eval_number = -self.surface_eval_step
            glBegin(GL_QUAD_STRIP)
            while curr_surface_eval_number <= 1:
                # vm is a 3x4 array that will hold vectors which are in the
                # context we need
                #
                #   vm =
                #
                #     2 +----------+----------+----------+
                #       |    s1    |    s2    |    s3    |
                #     1 +---------[+]--------[+]---------+
                #       |    s4    |    s5    |    s6    |
                #     0 +----------+----------+----------+
                #       0          1          2          3
                #
                #   * "+" are vertices
                #   * our current vertices (the ones we are going to draw)
                #     are the ones located at (1, 1) and (1, 2), which will
                #     be called s and t respectively
                #   * s1 to s6 are surfaces going to be drawn

                vm = [[0]*4 for i in range(3)]

                # vm is now filled accordingly
                vectors = (p1, p2, p3, p4)

                c = curr_surface_eval_number
                for row in range(3):
                    rotation = self.rotation_function(c)
                    translation = self.direction_function(c)
                    vm[row] =  [translation*rotation*v for v in vectors]

                    c += self.surface_eval_step

                # normals for each surface are calculated
                normal = self.normal

                s1_normal = normal(vm[2][1] - vm[1][0], vm[2][0] - vm[1][1])
                s2_normal = normal(vm[2][2] - vm[1][1], vm[2][1] - vm[1][2])
                s3_normal = normal(vm[2][3] - vm[1][2], vm[2][2] - vm[1][3])
                s4_normal = normal(vm[1][1] - vm[0][0], vm[1][0] - vm[0][1])
                s5_normal = normal(vm[1][2] - vm[0][1], vm[1][1] - vm[0][2])
                s6_normal = normal(vm[1][3] - vm[0][2], vm[1][2] - vm[0][3])

                # s and t vertex receive the average of their adjacent normals
                # as their normal values
                s_adj = [s1_normal, s2_normal, s4_normal, s5_normal]
                s_normal = self.vector_average(s_adj)
                
                t_adj = [s2_normal, s3_normal, s5_normal, s6_normal]
                t_normal = self.vector_average(t_adj)

                glNormal3d(s_normal.item(0), s_normal.item(1),
                    s_normal.item(2))
                glVertex3d(s.item(0), s.item(1), s.item(2))

                glNormal3d(t_normal.item(0), t_normal.item(1),
                    t_normal.item(2))
                glVertex3d(t.item(0), t.item(1), t.item(2))

                curr_surface_eval_number += self.surface_eval_step


     def evaluate_points(self, parms):
        """Given a sequence of parameters, returns a list of the
        corresponding points that result from evaluating
        self.curve_function on those parameters after preprocessing them.
        The preprocessing takes out the integer part from the parameters."""
        points = []
        for parm in parms:
            # we take out the integer part first
            parm = parm - int(parm)

            r = self.curve_function(parm)
            v = twodseq_to_vector(r)
            points.append(v)

        return ptors in a higher row are supposed to be at a lower
                        #     position on the surface (they have a lower value for
                                        #     their Y-component)
                                         

    def vector_average(self, v_list):
        """Receives a list of 1x3 matrices (vectors). It calculates the
        average between those that aren't None."""
        sum = matrix((0, 0, 0))
        tot = 0
        for v in v_list:
            if v != None:
                sum += v
                tot += 1

        return sum/tot

    def normal(self, v1, v2):
        """Receives two 1x3 matrices (vectors). If none of the two is none,
        returns a third vector perpendicular to the ones given."""
        if v1 != None and v2 != None:
            return cross(v1, v2)
        else:
            return None


 
                


class GLSurfaceOfRevolution(Drawable):
    
    def __init__(self, function, eval_steps, rotation_steps):
        """Construct a surface of revolution which will be draw
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
                curr_point = twodseq_to_vector(p_curr)

                curr_eval_number += self.eval_step

                p_next = self.function(curr_eval_number)
                next_point = twodseq_to_vector(p_next)

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
                tg = matrix(p_next) - matrix(p_curr)

                # the normal for p_next will be a vector that is perpendicular
                # to its tangent line
                n = (tg.item(1), -tg.item(0))
                # n now lives on a 3D world
                n = twodseq_to_vector(n)

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

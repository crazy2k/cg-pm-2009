from OpenGL.GL import *
from OpenGL.GLU import *

from utils.transformations import *

from numpy import pi, cross, size, sqrt, dot

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

        
def generate_tree(actual_level, height, primary_values, secondary_values, tertiary_values, transformation, generate_trunk, generate_leaf, seed):
    # generate a node with a new trunk into it, and make
    # initial_transformation its associated transformation
    if actual_level == 0:
        values = primary_values
        random.seed(seed)
    elif actual_level == 1:
        values = secondary_values
    else: #actual_level >= 2
        values = tertiary_values
    
    if actual_level >= 2:
        bottom_radius = values["initial_radius"] - values["radius_diff"]*(actual_level-2)
    else:
        bottom_radius = values["initial_radius"]
    
    trunk = generate_trunk(bottom_radius - values["radius_diff"], bottom_radius, values["branch_height"])
    node = GLSceneNode(transformation, trunk)
    
    if actual_level >= 2:
        leaf_trunk_radio = values["initial_radius"] - values["radius_diff"]*(height-2)
        node.add_child(generate_trunk_leaf(values, generate_trunk, trunk.endpoint(), leaf_trunk_radio, generate_leaf))
                
    if actual_level < height - 1:
        cant = int(random.random()*float(values["max_cant"] - values["min_cant"]) + values["min_cant"])
        for i in range (cant):
            angle_x = int(random.random()*float(2*values["angle"]) - float(values["angle"]))
            angle_z = int(random.random()*float(2*values["angle"]) - float(values["angle"]))
            next_transformation = translation(trunk.endpoint())*rotation(degree2radians(angle_z), "Z") * rotation(degree2radians(angle_x), "X")
            node.add_child(generate_tree(actual_level + 1, height, primary_values, secondary_values, tertiary_values, next_transformation, generate_trunk, generate_leaf, None))
    return node

def generate_trunk_leaf(values, generate_trunk, trunk_endpoint, leaf_trunk_radio, generate_leaf):
    angle_x = int(random.random()*float(2*values["angle"]) - float(values["angle"]))
    angle_z = int(random.random()*float(2*values["angle"]) - float(values["angle"]))
    transformation = translation(trunk_endpoint)*rotation(degree2radians(angle_z), "Z")*rotation(degree2radians(angle_x), "X")
    trunk = generate_trunk(leaf_trunk_radio,leaf_trunk_radio,values["branch_height"])
    node = GLSceneNode(transformation, trunk)
    leaf_node = GLSceneNode(transformation, generate_leaf(0.1,0.1,0.3))
    node.add_child(leaf_node)
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
    def generate_trunk(cls, bottom_radius, top_radius, height):
        c = GLCylinder(bottom_radius, top_radius, height)
        return c
class GLBezier(Drawable):
    
    def __init__(self, c_points, height):
        self.c_points = c_points
        self.type = GL_MAP2_VERTEX_3
        self.height = height

    def draw(self):
        glEnable(self.type)
        glEnable(GL_AUTO_NORMAL)
        glMap2f(self.type, 
                0.0, 1.0,  # U ranges 0..1 
                0.0, 1.0,  # V ranges 0..1  
                self.c_points)  # control points 
        glMapGrid2f(5, 0.0, 1.0, 60, 0.0, 1.0)  # we tell OpenGL to iterate 
        #across the full 0.0 to 1.0 range setup above with 5 rows and 6 columns
        glEvalMesh2(GL_FILL,
                0, 5,   # Starting at 0 mesh 5 steps (rows)
                0, 60)  # Starting at 0 mesh 6 steps (columns)
        glDisable(GL_AUTO_NORMAL)

    def endpoint(self):
        return (0, self.height, 0)

    @classmethod
    def generate_trunk(cls, bottom_radius, top_radius, height):
        r = bottom_radius
        
        def circle(a):
            return [(-r,a,0),(-r,a,-r),(r,a,-r),(r,a,r),(-r,a,r),(-r,a,0)]
        
        c1 = circle(0)
        c2 = circle(0)
        c3 = circle(0)
        c4 = circle(height)
        c5 = circle(height)
        c6 = circle(height) 
        
        m = [c1, c2, c3, c4, c5, c6]
        return GLBezier(m, height)
    
    @classmethod
    def generate_leaf(cls, mayor_radius, minor_radius, height):

        def leaf(a, b, c):
            return [(-a,b,0),(0,b,-c),(a*2,b,0),(0,b,c),(-a,b,0)]
        
        c1 = leaf(0,0,0)
        c2 = leaf(mayor_radius/2,height/2,minor_radius/2)
        c3 = leaf(mayor_radius,height/2,minor_radius)
        c4 = leaf(mayor_radius/2,height/2,minor_radius/2)
        c5 = leaf(0,height,0)
        m = [c1,c2,c3,c4,c5]
        return GLBezier(m, height)
        
    
class GLNURBS(Drawable):
    
    def __init__(self, sknots, tknots, c_points, height):
        self.sknots = sknots
        self.tknots = tknots
        self.c_points = c_points
        self.type = GL_MAP2_VERTEX_3
        self.height = height

        self.nurb = gluNewNurbsRenderer()

    def draw(self):
        glEnable(GL_AUTO_NORMAL)
        gluBeginSurface(self.nurb)
        gluNurbsSurface(self.nurb, self.sknots, self.tknots, self.c_points,
            self.type)
        gluEndSurface(self.nurb)
        glDisable(GL_AUTO_NORMAL)

    def endpoint(self):
        return (0, self.height, 0)

    @classmethod
    def generate_trunk(cls, bottom_radius, top_radius, height):
                
        r = bottom_radius
        h = height
        
        def cylinder_column(x,z):
            return [(x,0,z),(x,h/5,z),(x,h/4,z),(x,h/3,z),(x,h/2,z),(x,h,z)]
        
        c1 = cylinder_column(-r,0)
        c2 = cylinder_column(-r,r)
        c3 = cylinder_column(r,r)
        c4 = cylinder_column(r,-r)
        c5 = cylinder_column(-r,-r)
        c6 = cylinder_column(-r,0)
        m = [c1, c2, c3, c4, c5, c6]

        knots = []
        grade = 4
        for i in range (0,grade + len(c1)):
            if i < grade:
                knots.append(0)    
            elif i >= len(c1):
                knots.append((len(c1) - grade) + 1)
            else:
                knots.append(i + 1 - grade)

        return GLNURBS(knots, knots, m, height)
 

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
        while curr_curve_eval_number < 1:
            # p1 to p4 are (general) contiguous points on the curve
            d = self.curve_eval_step
            parms = (curr_curve_eval_number,
                     curr_curve_eval_number + d,
                     curr_curve_eval_number + 2*d,
                     curr_curve_eval_number + 3*d)

            p1, p2, p3, p4 = self.evaluate_points(parms)

            # since the curve will be swept through the Y-axis, points have
            # to be rotated 90 degrees around the X-axis (they're now points
            # on the XZ-plane)
            angle = degree2radians(-90)
            p1, p2, p3, p4 = [rotation(angle, "X")*v for v in (p1, p2, p3, p4)]

            # the curr_surface_eval_number starts at a first nonexistent row;
            # this is because the vertices we're going to give to OpenGL are
            # the ones at the next row
            curr_surface_eval_number = -self.surface_eval_step
            glBegin(GL_QUAD_STRIP)
            while curr_surface_eval_number < 1:
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
                #   * "+" are vertices (or Nones) 
                #   * our current vertices (the ones we are going to draw)
                #     are the ones located at (1, 1) and (1, 2), which will
                #     be called s and t respectively
                #   * s1 to s6 are surfaces

                vm = [[0]*4 for i in range(3)]

                # vm is now filled accordingly
                vectors = (p1, p2, p3, p4)

                c = curr_surface_eval_number
                for row in range(3):
                    # if this row is a nonexistent row, it's filled with Nones
                    if c == -self.surface_eval_step or c > 1:
                        vm[row] = [None]*4
                    # if it does exist, vectors are rotated, translated and
                    # then stored in the matrix
                    else:
                        rot = self.rotation_function(c)
                        trans = self.direction_function(c)
                        vm[row] =  [trans*rot*v for v in vectors]

                    c += self.surface_eval_step

                s = vm[1][1]
                t = vm[1][2]

                # normals for each surface are calculated
                normal = self.normal

                s1_normal = normal(vm[2][1], vm[1][0], vm[2][0], vm[1][1])
                s2_normal = normal(vm[2][2], vm[1][1], vm[2][1], vm[1][2])
                s3_normal = normal(vm[2][3], vm[1][2], vm[2][2], vm[1][3])
                s4_normal = normal(vm[1][1], vm[0][0], vm[1][0], vm[0][1])
                s5_normal = normal(vm[1][2], vm[0][1], vm[1][1], vm[0][2])
                s6_normal = normal(vm[1][3], vm[0][2], vm[1][2], vm[0][3])

                # s and t vertices receive the average of the normals from the
                # surfaces they compose as their normal values
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

                # move one step forward on the surface
                curr_surface_eval_number += self.surface_eval_step

            glEnd()

            # move one step forward on the curve
            curr_curve_eval_number += self.curve_eval_step

    def evaluate_points(self, parms):
        """Given a sequence of parameters, returns a list of the
        corresponding points that result from evaluating self.curve_function
        on those parameters after preprocessing them. The preprocessing takes
        out the integer part from the parameters."""
        points = []
        for parm in parms:
            # we take out the integer part first
            parm = parm - int(parm)

            r = self.curve_function(parm)
            v = twodseq_to_4x1vector(r)
            points.append(v)

        return points
                                        
    def normal(self, v1head, v1tail, v2head, v2tail):
        """Receives four 4x1 matrices (vectors). If neither is None,
        the following process takes place:
            1. Two vectors are created:
                a) v1head - v1tail
                b) v2head - v2tail
            2. The last component of the two 4x1 matrices is removed.
            3. A new 3x1 vector, perpendicular to those resulting from 2 is
               calculated.
            4. A fourth component (a 1) is added to this new vector, and the
               vector is returned.

        """
       
        if None in (v1head, v1tail, v2head, v2tail):
            return None
        else:
            v1 = v1head - v1tail
            x1 = (v1.item(0), v1.item(1), v1.item(2))
            v1 = my_matrix(x1)

            v2 = v2head - v2tail
            x2 = (v2.item(0), v2.item(1), v2.item(2))
            v2 = my_matrix(x2)

            v3 = cross(v1, v2)
            p3 = (v3.item(0), v3.item(1), v3.item(2))
            return threedseq_to_4x1vector(p3)

    def vector_average(self, v_list):
        """Receives a list of 4x1 matrices (vectors). It calculates the
        average between those that aren't None, ignoring the fourth component
        of each vector. After that calculation, the resulting 3x1 matrix is
        extended to a 4x1 matrix with 1 as its fourth component."""

        k = 200

        sum = my_matrix((0, 0, 0))
        tot = 0
        for v in v_list:
            if v != None:
                # v is multiplied by a factor to make its components bigger
                # to reduce precision errors
                v = k*v

                p = (v.item(0), v.item(1), v.item(2))
                v_1x3 = my_matrix(p)

                sum += v_1x3
                tot += 1

        a = (sum/k)/tot
        return threedseq_to_4x1vector((a.item(0), a.item(1), a.item(2)))

    def endpoint(self):
        p = (0, 0, 0)
        pt = self.direction_function(1)*threedseq_to_4x1vector(p)
        return (pt.item(0), pt.item(1), pt.item(2))

    @classmethod
    def generate_trunk(cls, bottom_radius, top_radius, height):
        r = bottom_radius
        circle_function = lambda x: (r*cos(x*2*pi), r*sin(x*2*pi))

        def direction_function(x):
            return translation((0, height*x, 0))

        def rotation_function(x):
            return IDENTITY_4

        c = GLSweptSurface(circle_function,
            direction_function, rotation_function,
            curve_eval_steps = 5, surface_eval_steps = 5)
        return c
 

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
                curr_point = twodseq_to_4x1vector(p_curr)

                curr_eval_number += self.eval_step

                p_next = self.function(curr_eval_number)
                next_point = twodseq_to_4x1vector(p_next)

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
                    x_axis = my_matrix((1, 0, 0, 1)).transpose()
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
                tg = my_matrix(p_next) - my_matrix(p_curr)

                # the normal for p_next will be a vector that is perpendicular
                # to its tangent line
                n = (tg.item(1), -tg.item(0))
                # n now lives on a 3D world
                n = twodseq_to_4x1vector(n)

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

        v = my_matrix((v.item(0), v.item(1), v.item(2)))
        norm = sqrt(dot(v, v.transpose()).item(0))
        v_n = v/norm
        m = my_matrix((v_n.item(0), v_n.item(1), v_n.item(2), 1)).transpose()
        return m


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
    def generate_trunk(cls, bottom_radius, top_radius, height):
        function = lambda x: (bottom_radius, x*height)

        c = GLSurfaceOfRevolution(function, 5, 5)
        return c

from OpenGL.GL import *
from OpenGL.GLU import *

from utils.transformations import *
import random

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


def generate_tree(actual_level, levels, radius, radius_diff, initial_transformation, generate_trunk):
    # generate a node with a new trunk into it, and make
    # initial_transformation its associated transformation
    if actual_level == 0:
        trunk = generate_trunk(radius*1.5, 1.4, actual_level, radius_diff)
    else:
        trunk = generate_trunk(radius - actual_level*0.01, 0.7 - 0.15*actual_level, actual_level, radius_diff)
    node = GLSceneNode(initial_transformation, trunk)
    
    if actual_level < levels:
        cant = (int(random.random()*100)%3)+ levels - 2*actual_level + 4
        create_branchs(cant, actual_level, levels, radius, radius_diff, generate_trunk, trunk, node)
    return node
    
def create_branchs(cant, actual_level, levels, radius, radius_diff, generate_trunk, trunk, node):
    for i in range(cant):
        create_branch(actual_level + 1, levels, radius, radius_diff, generate_trunk, trunk, node)

def create_branch(level, levels, radius, diff, generate_trunk, trunk, node):
    r = ((random.random()*180)%90)-45
    s = ((random.random()*260)%130)-65
    translation_m = translation(trunk.endpoint())
    next_t = translation_m * rotation(degree2radians(r), "Z") * rotation(degree2radians(s), "X")
    node.add_child(generate_tree(level, levels, radius, diff, next_t, generate_trunk))


class GLCylinder:

    def __init__(self, radius, diff, height):
        self.radius = radius
        self.height = height
        self.radius_diff = diff
        
    def draw(self):
        glPushMatrix()

        # create a new quadrics object
        quad = gluNewQuadric()
        # quadrics rendered with quad will not have texturing
        gluQuadricTexture(quad, False)
        
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, self.radius, self.radius - self.radius_diff, self.height, 26, 4)
        
        gluDeleteQuadric(quad)

        glPopMatrix()

    def endpoint(self):
        return (0, self.height, 0)

    @classmethod
    def generate(cls, radius, height, level, diff):
        c = GLCylinder(radius, diff, height)
        return c



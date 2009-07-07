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


def generate_tree(level, initial_transformation, generate_trunk):
    # generate a node with a new trunk into it, and make
    # initial_transformation its associated transformation
    trunk = generate_trunk()
    node = GLSceneNode(initial_transformation, trunk)

    r = ((random.random()*100)%66)-33
    s = ((random.random()*100)%50)-25
    t = ((random.random()*100)%66)-33
    u = ((random.random()*100)%50)-25
    w = ((random.random()*100)%66)-33
    x = ((random.random()*100)%50)-25
    y = ((random.random()*100)%66)-33
    z = ((random.random()*100)%50)-25

    if level > 0:
        translation_m = translation(trunk.endpoint())

        next_t = translation_m*rotation(degree2radians(r), "Z")*rotation(degree2radians(s), "X")

        node.add_child(generate_tree(level - 1, next_t, generate_trunk))

    return node


class GLCylinder:

    def __init__(self, radius, height):
        self.radius = radius
        self.height = height
        
    def draw(self):
        glPushMatrix()

        # create a new quadrics object
        quad = gluNewQuadric()
        # quadrics rendered with quad will not have texturing
        gluQuadricTexture(quad, False)
        
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, self.radius, self.radius, self.height, 26, 4)
        
        gluDeleteQuadric(quad)

        glPopMatrix()

    def endpoint(self):
        return (0, self.height, 0)

    @classmethod
    def generate(cls):
        c = GLCylinder(0.05, 0.5)
        return c



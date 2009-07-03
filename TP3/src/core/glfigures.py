from OpenGL.GL import *
from OpenGL.GLU import *
import random

class GLFigure:
    """GLFigure defines a common interface for all figures that are going
    to be drawn on a GLCanvas."""

    def draw(self):
        raise NotImplementedError

class GLAxis(GLFigure):

    def draw(self):
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

class GLTree(GLFigure):

    def __init__(self, level, trunk_generator):
        """GLTree's constructor takes two arguments:
        * level             -- nonnegative integer indicating the tree's level
        * trunk_generator   -- a Python generator, which will be called every
                               time a trunk is needed to be drawn; it should
                               give figures with the .draw() method
                               implemented

        """

        self.level = level
        self.trunk_generator = trunk_generator

    def draw(self):
        self.draw_tree(self.level)

    def draw_tree(self, level):
        h = 0.5
        r = ((random.random()*100)%66)-33
        s = ((random.random()*100)%50)-25
        t = random.random()

        f = self.trunk_generator(self.level - level)
        f.draw()

        if level > 0 and (t > 0.4 or level > 1):
            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(r-s, 0, 0, 1)
            self.draw_tree(level - 1)

            glPopMatrix()

            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(r, 0, 0, 1)
            glRotatef(s, 1, 0, 0)
            self.draw_tree(level - 1)

            glPopMatrix()


class GLCylinder(GLFigure):

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
        gluCylinder(quad, self.radius, self.radius-0.01, self.height, 26, 4)
        
        gluDeleteQuadric(quad)

        glPopMatrix()

    @classmethod
    def generate(cls, level):
        c = GLCylinder(0.05 - level*0.01, 0.5)
        return c




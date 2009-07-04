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

    def __init__(self, level, root, trunk_generator):
        """GLTree's constructor takes two arguments:
        * level             -- nonnegative integer indicating the tree's level
        * trunk_generator   -- a Python generator, which will be called every
                               time a trunk is needed to be drawn; it should
                               give figures with the .draw() method
                               implemented

        """
        self.level = level
        self.root = root
        self.trunk_generator = trunk_generator

    def draw(self):

        glPushMatrix()
        glTranslatef(self.root[0], self.root[1], self.root[2])

        self.draw_tree(self.level)
        glPopMatrix()

    def draw_tree(self, level):
        h = 0.5
        glColor3f(0.4,0.3,0.2)
        r = ((random.random()*100)%66)-33
        s = ((random.random()*100)%50)-25
        t = ((random.random()*100)%66)-33
        u = ((random.random()*100)%50)-25
        w = ((random.random()*100)%66)-33
        x = ((random.random()*100)%50)-25
        y = ((random.random()*100)%66)-33
        z = ((random.random()*100)%50)-25

        f = self.trunk_generator(self.level - level, 0.01)
        f.draw()
        if level == self.level:
            g = self.trunk_generator(self.level - level + 1, 0)
            glTranslatef(0,h,0)
            g.draw()
        
        if level > 0:
            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(r, 0, 0, 1)
            glRotatef(s, 1, 0, 0)
            self.draw_tree(level - 1)
            if level < 4:
                quad = gluNewQuadric()
                gluSphere(quad,0.05,100,100)
            glPopMatrix()

            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(t, 0, 0, 1)
            glRotatef(u, 1, 0, 0)
            self.draw_tree(level - 1)
            if level < 4:
                quad = gluNewQuadric()
                gluSphere(quad,0.05,100,100)
            glPopMatrix()

            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(-w, 0, 0, 1)
            glRotatef(-x, 1, 0, 0)
            self.draw_tree(level - 1)
            if level < 4:
                quad = gluNewQuadric()
                gluSphere(quad,0.05,100,100)
            glPopMatrix()

            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(-y, 0, 0, 1)
            glRotatef(-z, 1, 0, 0)
            self.draw_tree(level - 1)
            if level < 4:
                quad = gluNewQuadric()
                gluSphere(quad,0.05,100,100)
            glPopMatrix()

class GLCylinder(GLFigure):

    def __init__(self, radius, diff, height):
        self.radius = radius
        self.diff = diff
        self.height = height
        
    def draw(self):
        glPushMatrix()

        # create a new quadrics object
        quad = gluNewQuadric()
        # quadrics rendered with quad will not have texturing
        gluQuadricTexture(quad, False)
        
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, self.radius, self.radius-self.diff, self.height, 26, 4)
        
        gluDeleteQuadric(quad)

        glPopMatrix()

    @classmethod
    def generate(cls, level, diff):
        c = GLCylinder(0.05 - level*0.01, diff, 0.5)
        return c




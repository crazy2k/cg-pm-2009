from OpenGL.GL import *
from OpenGL.GLU import *

class GLAxis:

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

class GLTree:

    def __init__(self, level, trunk_generator):
        self.level = level
        self.trunk_generator = trunk_generator

    def draw(self):
        self.draw_tree(self.level)

    def draw_tree(self, level):
        h = 0.5

        f = self.trunk_generator.next()
        f.draw()

        if level > 0:
            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(15, 0, 0, 1)
            self.draw_tree(level - 1)

            glPopMatrix()

            glPushMatrix()

            glTranslatef(0, h, 0)
            glRotatef(-15, 0, 0, 1)
            glRotatef(-20, 1, 0, 0)
            self.draw_tree(level - 1)

            glPopMatrix()


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

    @classmethod
    def generator(self):
        while True:
            c = GLCylinder(0.01, 0.5)

            yield c




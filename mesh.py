# A mesh class which has its own VBO
from OpenGL.GL import *
from OpenGL.arrays import vbo
import numpy as np

# Set point size
glPointSize(5)

class Mesh:
    def __init__(self, vertices, indices=[], normals=[], uvs=[]):
        self.vertices = vertices
        self.indices = indices
        self.normals = normals
        self.uvs = uvs

        self.vbo = vbo.VBO(np.array(self.vertices, 'f'))

    def draw(self):
        self.vbo.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glVertexPointer(3, GL_FLOAT, 32, self.vbo)
        glNormalPointer(GL_FLOAT, 32, self.vbo+12)
        glTexCoordPointer(2, GL_FLOAT, 32, self.vbo+24)

        glDrawArrays(GL_POINTS, 0, len(self.vertices))

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        self.vbo.unbind()
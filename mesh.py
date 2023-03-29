# A mesh class which has its own VBO
from OpenGL.GL import *
from OpenGL.arrays import vbo
import numpy as np

glLineWidth(8)

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
        glVertexPointer(3, GL_FLOAT, 32, self.vbo)
        glDrawArrays(GL_LINE_LOOP, 0, len(self.vertices))
        glDisableClientState(GL_VERTEX_ARRAY)
        self.vbo.unbind()
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
        
        # Only implement the vertices
        self.vbo = vbo.VBO(np.array(self.vertices, 'f'))
        
    def draw(self):
        self.vbo.bind()
        try:
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, self.vbo)
            glDrawArrays(GL_LINES, 0, len(self.vertices))
        finally:
            self.vbo.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
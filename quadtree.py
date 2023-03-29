# Implementation of a QuadTree in Python
# This is for Terrain LoD
import opensimplex
import numpy as np
from mesh import Mesh
from OpenGL.GL import glColor3f
import random

# Create LeafNode first
class LeafNode(object):
    def __init__(self, position, size, resolution):
        self.position = position
        self.size = size
        self.resolution = resolution
        self.mesh = None
        self.generate()
        self.color = [random.random(), random.random(), random.random()]
    
    def generate(self,):
        self.heightmap = {}
        self.mesh = np.array([])
        
        # Generate the heightmap
        for x in range(self.resolution):
            for y in range(self.resolution):
                x_pos = x / (self.resolution - 1) * self.size[0] + self.position[0]
                y_pos = y / (self.resolution - 1) * self.size[1] + self.position[1]
                self.heightmap[(x, y)] = opensimplex.noise2(x_pos, y_pos)
                
        # Generate the mesh without the indices
        for x in range(self.resolution - 1):
            for y in range(self.resolution - 1):
                self.mesh = np.append(self.mesh, [
                    x / (self.resolution - 1) * self.size[0] + self.position[0],
                    self.heightmap[(x, y)],
                    y / (self.resolution - 1) * self.size[1] + self.position[1],
                    (x + 1) / (self.resolution - 1) * self.size[0] + self.position[0],
                    self.heightmap[(x + 1, y)],
                    y / (self.resolution - 1) * self.size[1] + self.position[1],
                    (x + 1) / (self.resolution - 1) * self.size[0] + self.position[0],
                    self.heightmap[(x + 1, y + 1)],
                    (y + 1) / (self.resolution - 1) * self.size[1] + self.position[1],
                    x / (self.resolution - 1) * self.size[0] + self.position[0],
                    self.heightmap[(x, y + 1)],
                    (y + 1) / (self.resolution - 1) * self.size[1] + self.position[1],
                    x / (self.resolution - 1) * self.size[0] + self.position[0],
                    self.heightmap[(x, y)],
                    y / (self.resolution - 1) * self.size[1] + self.position[1],
                ])
                
        # Create the mesh object
        self.mesh = Mesh(self.mesh)
        print("Generated mesh with %d vertices" % (len(self.mesh.vertices) / 3))
        
    def draw(self):
        if self.mesh:
            glColor3f(self.color[0], self.color[1], self.color[2])
            self.mesh.draw()

class QuadTree(object):
    def __init__(self, position, size, level):
        self.position = position
        self.level = level
        self.size = size
        self.children = []
        self.terrain = LeafNode(position, size, 32)
        self._split = False
        
    def draw(self):
        if not self._split:
            self.terrain.draw()
            return
        for child in self.children:
            glColor3f(0.0, 0.0, 0.0)
            child.draw()
            
    def split(self):
        XY = QuadTree([self.position[0], self.position[1]], [self.size[0] / 2, self.size[1] / 2], self.level - 1)
        Xy = QuadTree([self.position[0], self.position[1] + self.size[1] / 2], [self.size[0] / 2, self.size[1] / 2], self.level - 1)
        xY = QuadTree([self.position[0] + self.size[0] / 2, self.position[1]], [self.size[0] / 2, self.size[1] / 2], self.level - 1)
        xy = QuadTree([self.position[0] + self.size[0] / 2, self.position[1] + self.size[1] / 2], [self.size[0] / 2, self.size[1] / 2], self.level - 1)
        self.children.extend([XY, Xy, xY, xy])
        self._split = True

    def unite(self):
        del self.children[:]
        self.children = []
        self._split = False
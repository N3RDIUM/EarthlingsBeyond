# Implementation of a QuadTree in Python
# This is for Terrain LoD
import opensimplex
import numpy as np
from mesh import Mesh

# Create LeafNode first
class LeafNode(object):
    def __init__(self, position, size, resolution):
        self.position = position
        self.size = size
        self.resolution = resolution
        self.mesh = None
        self.generate()
    
    def generate(self,):
        self.heightmap = {}
        self.mesh = np.array([])
        
        # Generate the heightmap
        for x in range(-1, self.resolution+1):
            for z in range(-1, self.resolution+1):
                self.heightmap[(x, z)] = opensimplex.noise2(
                    (x + self.position[0]) / 16.0, (z + self.position[1]) / 16.0)
        
        # Create the mesh, scale the heightmap to the size of the chunk
        for x in range(self.resolution - 1):
            for z in range(self.resolution - 1):
                self.mesh = np.append(self.mesh, [
                    x / self.resolution * self.size[0] + self.position[0], self.heightmap[(x, z)] * self.size[1], z / self.resolution * self.size[1] + self.position[1],
                ])
        # Create the mesh object
        self.mesh = Mesh(self.mesh)
        print("Generated mesh with %d vertices" % (len(self.mesh.vertices) / 3))
        
    def draw(self):
        if self.mesh:
            self.mesh.draw()

class QuadTree(object):
    def __init__(self, position, size, level):
        self.position = position
        self.level = level
        self.size = size
        self.children = []
        self.terrain = LeafNode([0, 0], [16, 16], 16)
        self.split = False
        
    def draw(self):
        if not self.split:
            self.terrain.draw()
            return
        for child in self.children:
            child.draw()
            
    def split(self):
        XY = LeafNode((self.position[0], self.position[1]), (self.size[0]/2, self.size[1]/2), self.level + 1)
        Xy = LeafNode((self.position[0], self.position[1] + self.size[1]/2), (self.size[0]/2, self.size[1]/2), self.level + 1)
        xY = LeafNode((self.position[0] + self.size[0]/2, self.position[1]), (self.size[0]/2, self.size[1]/2), self.level + 1)
        xy = LeafNode((self.position[0] + self.size[0]/2, self.position[1] + self.size[1]/2), (self.size[0]/2, self.size[1]/2), self.level + 1)
        self.children.extend([XY, Xy, xY, xy])
        self.split = True

    def unite(self):
        del self.children[:]
        self.children = []
        self.split = False
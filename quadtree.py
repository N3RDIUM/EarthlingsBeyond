# Implementation of a QuadTree in Python
# This is for Terrain LoD
import noise
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
        vertices = []
        indices = []
        
        for x in range(self.resolution):
            for y in range(self.resolution):
                # Basically, create a grid of points
                vertices.append((x/self.resolution*self.size[0] + self.position[0], y/self.resolution*self.size[1] + self.position[1], noise.pnoise2(x/self.resolution*self.size[0] + self.position[0], y/self.resolution*self.size[1] + self.position[1], 2, 0.5, 2, 1, 1, 1)))
                
        # Now, create the indices
        for x in range(self.resolution - 1):
            for y in range(self.resolution - 1):
                indices.append((x*self.resolution + y, (x+1)*self.resolution + y, x*self.resolution + y + 1))
                indices.append(((x+1)*self.resolution + y, (x+1)*self.resolution + y + 1, x*self.resolution + y + 1))
        
        self.mesh = Mesh(vertices, indices)
        print("Generated mesh with %d vertices and %d indices" % (len(vertices), len(indices)))
        
    def draw(self):
        if self.mesh:
            self.mesh.draw()

class QuadTree(object):
    def __init__(self, position, size, level):
        self.position = position
        self.level = level
        self.size = size
        self.children = []
        self.terrain = LeafNode([0, 0], [1, 1], 16)
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
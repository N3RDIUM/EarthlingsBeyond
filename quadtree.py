# Implementation of a QuadTree in Python
# This is for Terrain LoD
import noise
import numpy as np
from mesh import Mesh
from OpenGL.GL import glColor3f
import math
import random
import threading

def midpoint(v1, v2):
    x = (v1[0] + v2[0]) / 2
    y = (v1[1] + v2[1]) / 2
    z = (v1[2] + v2[2]) / 2
    
    return (x, y, z)

class CubeTree:
    def __init__(self, size=32, position=[0,0,0]):
        self.size = size

        self.up = QuadTree(rect=[(0,size,0), (size,size,0), (size,size,size), (0,size,size)], level=1, parent=self)
        self.down = QuadTree(rect=[(0,0,0), (size,0,0), (size,0,size), (0,0,size)], level=1, parent=self)
        self.left = QuadTree(rect=[(0,0,0), (0,size,0), (0,size,size), (0,0,size)], level=1, parent=self)
        self.right = QuadTree(rect=[(size,0,0), (size,size,0), (size,size,size), (size,0,size)], level=1, parent=self)
        self.front = QuadTree(rect=[(0,0,0), (size,0,0), (size,size,0), (0,size,0)], level=1, parent=self)
        self.back = QuadTree(rect=[(0,0,size), (size,0,size), (size,size,size), (0,size,size)], level=1, parent=self)
        
    def draw(self):
        self.up.draw()
        self.down.draw()
        self.left.draw()
        self.right.draw()
        self.front.draw()
        self.back.draw()

class QuadTree:
    def __init__(self, rect=[(0,0,0), (100,0,0), (100,0,100), (0,0,100)], level=1, parent=None):
        self.rect = rect
        self.level = level
        self.parent = parent
        self.mesh = None
        self.children = []
        self.generate()
        
    def generate(self):
        lnode = LeafNode(self.rect, self.level + 1, self, tesselate=6)
        self.children.append(lnode)
        
    def split(self):
        self.children = []
        
        # Split the quad into 4 quads
        corner1 = self.rect[0]
        corner2 = self.rect[1]
        corner3 = self.rect[2]
        corner4 = self.rect[3]
        
        # Make a midpoint between each corner
        midpoint1 = midpoint(corner1, corner2)
        midpoint2 = midpoint(corner2, corner3)
        midpoint3 = midpoint(corner3, corner4)
        midpoint4 = midpoint(corner4, corner1)
        midpoint5 = midpoint(corner1, corner3)
        
        # Now, make a simple quad
        rect1 = [corner1, midpoint1, midpoint5, midpoint4]
        rect2 = [midpoint1, corner2, midpoint2, midpoint5]
        rect3 = [midpoint5, midpoint2, corner3, midpoint3]
        rect4 = [midpoint4, midpoint5, midpoint3, corner4]
        
        # Create a node for each quad
        node1 = QuadTree(rect1, self.level + 1, self.parent)
        node2 = QuadTree(rect2, self.level + 1, self.parent)
        node3 = QuadTree(rect3, self.level + 1, self.parent)
        node4 = QuadTree(rect4, self.level + 1, self.parent)
        
        # Add the nodes to the children list
        self.children.append(node1)
        self.children.append(node2)
        self.children.append(node3)
        self.children.append(node4)
        
    def unite(self):
        self.children = []
        self.generate()
        
    def draw(self):
        for child in self.children:
            child.draw()
            
class LeafNode():
    def __init__(self, rect, level, parent, tesselate=8):
        self.rect = rect
        self.level = level
        self.parent = parent
        self._tesselate = tesselate
        self.mesh = None
        self.color = [random.random(), random.random(), random.random()]
        self.generate()
        
    def generate(self):
        corner1 = self.rect[0]
        corner2 = self.rect[1]
        corner3 = self.rect[2]
        corner4 = self.rect[3]
        
        # Now, make a simple quad
        vertices = [
            corner1, corner2, corner3, corner4
        ]
        
        # Tesselate the quad, make it a sphere, and add noise
        vertices = self.tesselate(vertices, times=self._tesselate)
        vertices = self.sphere(vertices)
        
        # Convert the points to a triangle mesh
        vertices = self.convert_to_mesh(vertices)
        
        # Create a mesh
        self.mesh = Mesh(vertices)
        
    def tesselate(self, vertices, times=1):
        if times == 0:
            return vertices
        
        new_vertices = []
        
        for i in range(0, len(vertices), 4):
            corner1 = vertices[i]
            corner2 = vertices[i + 1]
            corner3 = vertices[i + 2]
            corner4 = vertices[i + 3]
            
            # Make a midpoint between each corner
            midpoint1 = midpoint(corner1, corner2)
            midpoint2 = midpoint(corner2, corner3)
            midpoint3 = midpoint(corner3, corner4)
            midpoint4 = midpoint(corner4, corner1)
            midpoint5 = midpoint(corner1, corner3)
            
            # Now, make a simple quad
            new_vertices.append(corner1)
            new_vertices.append(midpoint1)
            new_vertices.append(midpoint5)
            new_vertices.append(midpoint4)
            
            new_vertices.append(midpoint1)
            new_vertices.append(corner2)
            new_vertices.append(midpoint2)
            new_vertices.append(midpoint5)
            
            new_vertices.append(midpoint5)
            new_vertices.append(midpoint2)
            new_vertices.append(corner3)
            new_vertices.append(midpoint3)
            
            new_vertices.append(midpoint4)
            new_vertices.append(midpoint5)
            new_vertices.append(midpoint3)
            new_vertices.append(corner4)
            
        return self.tesselate(new_vertices, times - 1)

    def sphere(self, vertices):
        CENTER = [self.parent.parent.size / 2]*3
        for i in range(len(vertices)):
            v = vertices[i]
            x = v[0] - CENTER[0]
            y = v[1] - CENTER[1]
            z = v[2] - CENTER[2]
            
            length = math.sqrt(x**2 + y**2 + z**2)
            
            x = x / length * self.parent.parent.size
            y = y / length * self.parent.parent.size
            z = z / length * self.parent.parent.size
            
            vertices[i] = (x, y, z)
        return vertices
    
    def convert_to_mesh(self, vertices):
        # Convert the points to a triangle mesh
        new_vertices = []
        for i in range(0, len(vertices), 4):
            corner1 = vertices[i + 2]
            corner2 = vertices[i + 3]
            corner3 = vertices[i + 1]
            corner4 = vertices[i + 0]
            
            new_vertices.append(corner1)
            new_vertices.append(corner3)
            new_vertices.append(corner4)
            
            new_vertices.append(corner1)
            new_vertices.append(corner3)
            new_vertices.append(corner4)
        return new_vertices
        
    def draw(self):
        if self.mesh is not None:
            glColor3f(self.color[0], self.color[1], self.color[2])
            self.mesh.draw()
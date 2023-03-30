# Implementation of a QuadTree in Python
# This is for Terrain LoD
import noise
import numpy as np
from mesh import Mesh
from OpenGL.GL import glColor3f
import math
import random
import threading

class QuadTree:
    def __init__(self, rect=[(0,0,0), (100,0,0), (100,0,100), (0,0,100)], level=1, parent=None):
        self.rect = rect
        self.level = level
        self.parent = parent
        self.mesh = None
        self.children = []
        self.generate()
        
    def generate(self):
        lnode = LeafNode(self.rect, self.level + 1, self, tesselate=8)
        self.children.append(lnode)
        
    def split(self):
        self.children = []
        
        XY = self.rect[0]
        ZW = self.rect[1]
        x = XY[0]
        y = XY[1]
        z = ZW[0]
        w = ZW[1]
        midx = (x + z) / 2
        midy = (y + w) / 2
        
        # Top Left
        rect = ((x, y), (midx, midy))
        node = QuadTree(rect, self.level + 1, self)
        self.children.append(node)
        
        # Top Right
        rect = ((midx, y), (z, midy))
        node = QuadTree(rect, self.level + 1, self)
        self.children.append(node)
        
        # Bottom Left
        rect = ((x, midy), (midx, w))
        node = QuadTree(rect, self.level + 1, self)
        self.children.append(node)
        
        # Bottom Right
        rect = ((midx, midy), (z, w))
        node = QuadTree(rect, self.level + 1, self)
        self.children.append(node)
        
    def unite(self):
        self.children = []
        self.generate()
        
    def draw(self):
        for child in self.children:
            child.draw()
            
class LeafNode():
    def __init__(self, rect, level, parent, tesselate=32):
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
            corner1, corner2, corner3,
            corner1, corner3, corner4
        ]
        
        # Tesselate the quad and add noise
        vertices = self.tesselate(vertices, times=self._tesselate)
        vertices = self.add_noise(vertices)
        
        # Create a mesh
        self.mesh = Mesh(vertices)
        
    def tesselate(self, vertices, times=1):
        if times == 0:
            return vertices
        
        new_vertices = []
        
        for i in range(0, len(vertices), 3):
            v1 = vertices[i]
            v2 = vertices[i+1]
            v3 = vertices[i+2]
            
            v12 = self.midpoint(v1, v2)
            v23 = self.midpoint(v2, v3)
            v31 = self.midpoint(v3, v1)
            
            new_vertices.append(v1)
            new_vertices.append(v12)
            new_vertices.append(v31)
            
            new_vertices.append(v2)
            new_vertices.append(v23)
            new_vertices.append(v12)
            
            new_vertices.append(v3)
            new_vertices.append(v31)
            new_vertices.append(v23)
            
            new_vertices.append(v12)
            new_vertices.append(v23)
            new_vertices.append(v31)
            
        return self.tesselate(new_vertices, times - 1)
    
    def midpoint(self, v1, v2):
        x = (v1[0] + v2[0]) / 2
        y = (v1[1] + v2[1]) / 2
        z = (v1[2] + v2[2]) / 2
        
        return (x, y, z)
    
    def add_noise(self, vertices):
        new_vertices = []
        for vertex in vertices:
            x = vertex[0]
            y = vertex[1]
            z = vertex[2]
            
            y += noise.pnoise2(x / 10, z / 10) * 10
            new_vertices.append((x, y, z))
            
        return new_vertices
        
    def draw(self):
        if self.mesh is not None:
            glColor3f(self.color[0], self.color[1], self.color[2])
            self.mesh.draw()
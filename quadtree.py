# Implementation of a QuadTree in Python
# This is for Terrain LoD
import noise
import numpy as np
from mesh import Mesh
from OpenGL.GL import glColor3f
import math
import random
import threading

class CubeTree(object):
    """
    Basically, a cube whose sides are QuadTrees
    """

    def __init__(self, position, size=32):
        self.position = position
        self.size = size

        self.up = QuadTree(
            [position[0], 
             position[1] + self.size, 
             position[2] - self.size / 2], self.size, 1, _type="up", parent_position=position)
        self.down = QuadTree(
            [position[0], 
             position[1], 
             position[2] - self.size / 2], self.size, 1, _type="down", parent_position=position)
        self.left = QuadTree(
            [position[0], 
             position[1], 
             position[2] - self.size / 2], self.size, 1, _type="left", parent_position=position)
        self.right = QuadTree(
            [position[0] + self.size, 
             position[1], 
             position[2] - self.size / 2], self.size, 1, _type="right", parent_position=position)
        self.front = QuadTree(
            [position[0], 
             position[1], 
             position[2] - self.size / 2], self.size, 1, _type="front", parent_position=position)
        self.back = QuadTree(
            [position[0], 
             position[1], 
             position[2] + self.size / 2], self.size, 1, _type="back", parent_position=position)
        
    def draw(self):
        self.up.draw()
        self.down.draw()
        self.left.draw()
        self.right.draw()
        self.front.draw()
        self.back.draw()


class QuadTree(object):
    def __init__(self, position, size, level, _type="up", parent_position=[]):
        self.position = position
        self.type = _type
        self.level = level
        self.size = size
        self.children = []
        self.parent_position = parent_position
        self.terrain = LeafNode(position, size, 16, _type=_type, parent_position=parent_position, level=level)
        self._split = False

    def draw(self):
        if not self._split:
            self.terrain.draw()
            return
        for child in self.children:
            glColor3f(0.0, 0.0, 0.0)
            child.draw()

    def split(self):
        if self.type in ["up", "down"]:
            xy = QuadTree([self.position[0], self.position[1], self.position[2]], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            xY = QuadTree([self.position[0], self.position[1], self.position[2] + self.size / 2], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            XY = QuadTree([self.position[0] + self.size / 2, self.position[1], self.position[2] + self.size / 2], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            Xy = QuadTree([self.position[0] + self.size / 2, self.position[1], self.position[2]], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
        elif self.type in ["left", "right"]:
            xy = QuadTree([self.position[0], self.position[1], self.position[2]], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            xY = QuadTree([self.position[0], self.position[1] + self.size / 2, self.position[2]], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            XY = QuadTree([self.position[0], self.position[1] + self.size / 2, self.position[2] + self.size / 2], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            Xy = QuadTree([self.position[0], self.position[1], self.position[2] + self.size / 2], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
        elif self.type in ["front", "back"]:
            xy = QuadTree([self.position[0], self.position[1], self.position[2]], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            xY = QuadTree([self.position[0] + self.size / 2, self.position[1], self.position[2]], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            XY = QuadTree([self.position[0] + self.size / 2, self.position[1] + self.size / 2, self.position[2]], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
            Xy = QuadTree([self.position[0], self.position[1] + self.size / 2, self.position[2]], self.size / 4, self.level + 1, _type=self.type, parent_position=self.position)
        self.children.extend([xy, xY, XY, Xy])
        self._split = True

    def unite(self):
        del self.children[:]
        self.children = []
        self._split = False


class LeafNode(object):
    def __init__(self, position, size, resolution, _type="up", parent_position=[], level=1):
        self.position = position
        self.size = size * (level)
        self.resolution = resolution
        self.mesh = None
        self.type = _type
        self.color = [random.random(), random.random(), random.random()]
        self.parent_position = parent_position
        self.level = level
        
        self.gen_thread = threading.Thread(target=self.generate)
        self.gen_thread.start()

    def generate(self,):
        self._mesh = np.array([])

        # Generate the mesh without the indices (show the triangles)
        for x in range(self.resolution):
            for y in range(self.resolution):
                if self.type in ["up", "down"]:
                    self._mesh = np.append(self._mesh, [x * self.size / self.resolution, 0, y * self.size / self.resolution])
                    self._mesh = np.append(self._mesh, [x * self.size / self.resolution, 0, (y + 1) * self.size / self.resolution])
                    self._mesh = np.append(self._mesh, [(x + 1) * self.size / self.resolution, 0, y * self.size / self.resolution])

                    self._mesh = np.append(self._mesh, [(x + 1) * self.size / self.resolution, 0, y * self.size / self.resolution])
                    self._mesh = np.append(self._mesh, [x * self.size / self.resolution, 0, (y + 1) * self.size / self.resolution])
                    self._mesh = np.append(self._mesh, [(x + 1) * self.size / self.resolution, 0, (y + 1) * self.size / self.resolution])
                elif self.type in ["left", "right"]:
                    self._mesh = np.append(self._mesh, [0, x * self.size / self.resolution, y * self.size / self.resolution])
                    self._mesh = np.append(self._mesh, [0, x * self.size / self.resolution, (y + 1) * self.size / self.resolution])
                    self._mesh = np.append(self._mesh, [0, (x + 1) * self.size / self.resolution, y * self.size / self.resolution])

                    self._mesh = np.append(self._mesh, [0, (x + 1) * self.size / self.resolution, y * self.size / self.resolution])
                    self._mesh = np.append(self._mesh, [0, x * self.size / self.resolution, (y + 1) * self.size / self.resolution])
                    self._mesh = np.append(self._mesh, [0, (x + 1) * self.size / self.resolution, (y + 1) * self.size / self.resolution])
                elif self.type in ["front", "back"]:
                    self._mesh = np.append(self._mesh, [x * self.size / self.resolution, y * self.size / self.resolution, 0])
                    self._mesh = np.append(self._mesh, [x * self.size / self.resolution, (y + 1) * self.size / self.resolution, 0])
                    self._mesh = np.append(self._mesh, [(x + 1) * self.size / self.resolution, y * self.size / self.resolution, 0])

                    self._mesh = np.append(self._mesh, [(x + 1) * self.size / self.resolution, y * self.size / self.resolution, 0])
                    self._mesh = np.append(self._mesh, [x * self.size / self.resolution, (y + 1) * self.size / self.resolution, 0])
                    self._mesh = np.append(self._mesh, [(x + 1) * self.size / self.resolution, (y + 1) * self.size / self.resolution, 0])
                    
        for index in range(0, len(self._mesh), 3):
            self._mesh[index] = self._mesh[index] + self.position[0]
            self._mesh[index + 1] = self._mesh[index + 1] + self.position[1]
            self._mesh[index + 2] = self._mesh[index + 2] + self.position[2]
        
        # Make it part of the sphere
        CENTER = [
            self.parent_position[0] + self.size / 2,
            self.parent_position[1] + self.size / 2,
            self.parent_position[2]
        ]
        # Do it in such a way that the center of the sphere is the center of the cube
        # And, the smaller "split" cubes are the smaller the sphere is
        for index in range(0, len(self._mesh), 3):
            vector = [
                self._mesh[index] - CENTER[0],
                self._mesh[index + 1] - CENTER[1],
                self._mesh[index + 2] - CENTER[2]
            ]
            length = math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)
            vector = [
                vector[0] / length,
                vector[1] / length,
                vector[2] / length
            ]
            self._mesh[index] = vector[0] * self.size / 2 + CENTER[0]
            self._mesh[index + 1] = vector[1] * self.size / 2 + CENTER[1]
            self._mesh[index + 2] = vector[2] * self.size / 2 + CENTER[2]
            
        self.generated = True

    def create_mesh(self):
        self.mesh = Mesh(self._mesh)

    def draw(self):
        try:
            if self.generated:
                self.create_mesh()
            else:
                return
        except AttributeError:
            pass
        if self.mesh is not None:
            glColor3f(self.color[0], self.color[1], self.color[2])
            self.mesh.draw()

# Implementation of a QuadTree in Python
# This is for Terrain LoD
import noise
import numpy as np
from mesh import Mesh
from OpenGL.GL import glColor3f, glBegin, glEnd, glVertex3f, GL_QUADS, glPushMatrix, glPopMatrix, glTranslatef
import random
import threading


def multiDimenDist(point1, point2):
    deltaVals = [point2[dimension]-point1[dimension]
                 for dimension in range(len(point1))]
    runningSquared = 0
    for coOrd in deltaVals:
        runningSquared += coOrd**2
    return runningSquared**(1/2)


def findVec(point1, point2, unitSphere=False):
    finalVector = [0 for coOrd in point1]
    for dimension, coOrd in enumerate(point1):
        deltaCoOrd = point2[dimension]-coOrd
        finalVector[dimension] = deltaCoOrd
    if unitSphere:
        totalDist = multiDimenDist(point1, point2)
        unitVector = []
        for dimen in finalVector:
            unitVector.append(dimen/totalDist)
        return unitVector
    else:
        return finalVector


class CubeTree(object):
    """
    Basically, a cube whose sides are QuadTrees
    """

    def __init__(self, position, size=32):
        self.position = position
        self.size = size

        self.up = QuadTree(
            [position[0], position[1], position[2] + self.size], self.size, 4, _type="up", parent_position=position)
        self.down = QuadTree(
            [position[0], position[1], position[2] - self.size], self.size, 4, _type="down", parent_position=position)
        self.left = QuadTree(
            [position[0] - self.size, position[1], position[2]], self.size, 4, _type="left", parent_position=position)
        self.right = QuadTree(
            [position[0] + self.size, position[1], position[2]], self.size, 4, _type="right", parent_position=position)
        self.front = QuadTree(
            [position[0], position[1] - self.size, position[2]], self.size, 4, _type="front", parent_position=position)
        self.back = QuadTree(
            [position[0], position[1] + self.size, position[2]], self.size, 4, _type="back", parent_position=position)

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
        self.terrain = LeafNode(position, size, 64, _type=_type, parent_position=parent_position)
        self._split = False

    def draw(self):
        if not self._split:
            self.terrain.draw()
            return
        for child in self.children:
            glColor3f(0.0, 0.0, 0.0)
            child.draw()

    def split(self):
        XY = QuadTree([self.position[0], self.position[1]], [
                      self.size / 2, self.size / 2], self.level - 1, _type=self.type)
        Xy = QuadTree([self.position[0], self.position[1] + self.size / 2],
                      [self.size / 2, self.size / 2], self.level - 1, _type=self.type)
        xY = QuadTree([self.position[0] + self.size / 2, self.position[1]],
                      [self.size / 2, self.size / 2], self.level - 1, _type=self.type)
        xy = QuadTree([self.position[0] + self.size / 2, self.position[1] + self.size / 2],
                      [self.size / 2, self.size / 2], self.level - 1, _type=self.type)
        self.children.extend([XY, Xy, xY, xy])
        self._split = True

    def unite(self):
        del self.children[:]
        self.children = []
        self._split = False


class LeafNode(object):
    def __init__(self, position, size, resolution, _type="up", parent_position=[]):
        self.position = position
        self.size = size
        self.resolution = resolution
        self.mesh = None
        self.type = _type
        self.color = [random.random(), random.random(), random.random()]
        self.parent_position = parent_position
        
        self.gen_thread = threading.Thread(target=self.generate)
        self.gen_thread.start()

    def generate(self,):
        self.heightmap = {}
        self._mesh = np.array([])

        # Generate the heightmap
        for x in range(self.resolution):
            for y in range(self.resolution):
                self.heightmap[(x, y)] = 0

        # Generate the mesh without the indices
        for x in range(self.resolution - 1):
            for y in range(self.resolution - 1):
                self._mesh = np.append(self._mesh, [
                    x / (self.resolution - 1) * self.size,
                    self.heightmap[(x, y)],
                    y / (self.resolution - 1) * self.size,
                    
                    (x + 1) / (self.resolution - 1) * self.size,
                    self.heightmap[(x + 1, y)],
                    y / (self.resolution - 1) * self.size,
                    
                    (x + 1) / (self.resolution - 1) * self.size,
                    self.heightmap[(x + 1, y + 1)],
                    (y + 1) / (self.resolution - 1) * self.size,
                    
                    x / (self.resolution - 1) * self.size,
                    self.heightmap[(x, y + 1)],
                    (y + 1) / (self.resolution - 1) * self.size,
                    
                    x / (self.resolution - 1) * self.size,
                    self.heightmap[(x, y)],
                    y / (self.resolution - 1) * self.size,
                ])

        # Now, apply the rotation
        if self.type == "up":
            for index in range(0, len(self._mesh), 3):
                x = self._mesh[index]
                y = self._mesh[index + 1]
                z = self._mesh[index + 2]
                self._mesh[index] = z
                self._mesh[index + 1] = y + self.size / 2
                self._mesh[index + 2] = x
        elif self.type == "down":
            for index in range(0, len(self._mesh), 3):
                x = self._mesh[index]
                y = self._mesh[index + 1]
                z = self._mesh[index + 2]
                self._mesh[index] = z
                self._mesh[index + 1] = y - self.size / 2
                self._mesh[index + 2] = x
        elif self.type == "left":
            for index in range(0, len(self._mesh), 3):
                x = self._mesh[index]
                y = self._mesh[index + 1]
                z = self._mesh[index + 2]
                self._mesh[index] = x
                self._mesh[index + 1] = z - self.size / 2
                self._mesh[index + 2] = y
        elif self.type == "right":
            for index in range(0, len(self._mesh), 3):
                x = self._mesh[index]
                y = self._mesh[index + 1]
                z = self._mesh[index + 2]
                self._mesh[index] = x
                self._mesh[index + 1] = z - self.size / 2
                self._mesh[index + 2] = y + self.size
        elif self.type == "front":
            for index in range(0, len(self._mesh), 3):
                x = self._mesh[index]
                y = self._mesh[index + 1]
                z = self._mesh[index + 2]
                self._mesh[index] = y
                self._mesh[index + 1] = x - self.size / 2
                self._mesh[index + 2] = z
        elif self.type == "back":
            for index in range(0, len(self._mesh), 3):
                x = self._mesh[index]
                y = self._mesh[index + 1]
                z = self._mesh[index + 2]
                self._mesh[index] = y + self.size
                self._mesh[index + 1] = x - self.size / 2
                self._mesh[index + 2] = z

        # Tesselate the mesh towards a sphere
        CENTER = [
            self.size / 2, 
            0, 
            self.size / 2
        ]
        simplex = noise.snoise3
        for index in range(0, len(self._mesh), 3):
            x = self._mesh[index]
            y = self._mesh[index + 1]
            z = self._mesh[index + 2]
            vector = findVec((x, y, z), CENTER, True)
            self._mesh[index] = vector[0] * self.size / 2
            self._mesh[index + 1] = vector[1] * self.size / 2
            self._mesh[index + 2] = vector[2] * self.size / 2
            
            _noise = (
                simplex(vector[0], vector[1], vector[2]) * 400 + \
                simplex(vector[0] * 2, vector[1] * 2, vector[2] * 2) * 1600 + \
                simplex(vector[0] / 2, vector[1] / 2, vector[2] / 2) * 200 + \
                simplex(vector[0] / 4, vector[1] / 4, vector[2] / 4) * 400 + \
                simplex(vector[0] / 8, vector[1] / 8, vector[2] / 8) * 800
            ) / 4
            self._mesh[index] += vector[0] * _noise
            self._mesh[index + 1] += vector[1] * _noise
            self._mesh[index + 2] += vector[2] * _noise 
        
        for index in range(0, len(self._mesh), 3):
            x = self._mesh[index] + self.parent_position[0]
            y = self._mesh[index + 1] + self.parent_position[1]
            z = self._mesh[index + 2] + self.parent_position[2]
            self._mesh[index] = x
            self._mesh[index + 1] = y
            self._mesh[index + 2] = z
            
        self.generated = True

    def create_mesh(self):
        self.mesh = Mesh(self._mesh[:-1])

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

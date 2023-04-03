# Implementation of a QuadTree in Python
# This is for Terrain LoD
import noise
import numpy
from mesh import Mesh
from OpenGL.GL import *
from OpenGL.GLUT import *
import math
import random
import threading

def midpoint(v1, v2):
    x = (v1[0] + v2[0]) / 2
    y = (v1[1] + v2[1]) / 2
    z = (v1[2] + v2[2]) / 2
    
    return (x, y, z)

glutInit()
def drawSphere(x, y, z, radius=1):
    glPushMatrix()
    glTranslatef(x, y, z)
    glutSolidSphere(radius, 10, 10)
    glPopMatrix()

class CubeTree:
    def __init__(self, size=320, position=[0,0,-160], rotation=[-13.5,0,0], rotation_vel=[0.02,0.01,0.04], camera=None):
        self.size = size
        self.position = position
        self.rotation = rotation
        self.rotation_vel = rotation_vel
        self.camera = camera
        self.drawing = False
        
        self.up = QuadTree(rect=[(0,size,0), (0,size,size), (size,size,size), (size,size,0)], level=1, parent=self)
        self.left = QuadTree(rect=[(0,0,0), (0,0,size), (0,size,size), (0,size,0)], level=1, parent=self)
        self.front = QuadTree(rect=[(0,0,0), (0,size,0), (size,size,0), (size,0,0)], level=1, parent=self)

        self.down = QuadTree(rect=[(0,0,0), (size,0,0), (size,0,size), (0,0,size)], level=1, parent=self)
        self.right = QuadTree(rect=[(size,0,0), (size,size,0), (size,size,size), (size,0,size)], level=1, parent=self)
        self.back = QuadTree(rect=[(0,0,size), (size,0,size), (size,size,size), (0,size,size)], level=1, parent=self)
        
    def draw(self):
        self.drawing = True
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        
        self.up.draw()
        self.left.draw()
        self.front.draw()
        
        self.right.draw()
        self.down.draw()
        self.back.draw()
        
        glColor4f(0.5, 0.69, 1.0, 1.0)
        glutSolidSphere(self.size, 128, 128)
        
        glPopMatrix()
        
        self.drawing = False
        
        self.rotation[0] += self.rotation_vel[0]
        self.rotation[1] += self.rotation_vel[1]
        self.rotation[2] += self.rotation_vel[2]
        
    def update(self):
        if self.camera is not None:
            # self.up.update(self.camera.position)
            # self.down.update(self.camera.position)
            # self.left.update(self.camera.position)
            # self.right.update(self.camera.position)
            # self.front.update(self.camera.position)
            # self.back.update(self.camera.position)
            pass

class QuadTree:
    def __init__(self, rect=[(0,0,0), (100,0,0), (100,0,100), (0,0,100)], level=1, parent=None):
        self.rect = rect
        self.level = level
        self.parent = parent
        self.mesh = None
        self.children = []
        self.size = self.rect[1][0] - self.rect[0][0]
        self.position = []
        
        self.generate()
    
    def generate(self):
        lnode = LeafNode(self.rect, self.level + 1, self)
        self.children.append(lnode)
        
    def split(self):
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
        
        del self.children[0]
        self.children.remove(self.children[0])
        
    def unite(self):
        self.children = []
        self.generate()
        
    def draw(self):
        for child in self.children:
            child.draw()
        
    def update(self, camera_position):
        if len(self.position) == 0:
            return
        
        # Rotate the camera position
        camera_position = self.rotate_point(camera_position, self.parent.rotation)
        
        # Calculate the distance between the camera and the center of the quad
        distance = math.sqrt((self.position[0] - camera_position[0]) ** 2 + (self.position[1] - camera_position[1]) ** 2 + (self.position[2] - camera_position[2]) ** 2)
        
        # If the camera is close enough to the quad, split it
        if distance < self.size:
            if len(self.children) == 1:
                self.split()
                
            for child in self.children:
                child.update(camera_position)
        else:
            if len(self.children) == 4:
                self.unite()
        
    @staticmethod
    def rotate_point(point, rotation):
        x = point[0]
        y = point[1]
        z = point[2]
        
        x1 = x * math.cos(rotation[0]) - y * math.sin(rotation[0])
        y1 = x * math.sin(rotation[0]) + y * math.cos(rotation[0])
        z1 = z
        
        x2 = x1 * math.cos(rotation[1]) - z1 * math.sin(rotation[1])
        y2 = y1
        z2 = x1 * math.sin(rotation[1]) + z1 * math.cos(rotation[1])
        
        x3 = x2
        y3 = y2 * math.cos(rotation[2]) - z2 * math.sin(rotation[2])
        z3 = y2 * math.sin(rotation[2]) + z2 * math.cos(rotation[2])
        
        return (x3, y3, z3)

            
class LeafNode():
    def __init__(self, rect, level, parent, tesselate=4):
        self.rect = rect
        self.level = level
        self.parent = parent
        self._tesselate = tesselate
        self.mesh = None
        self.color = [random.random(), random.random(), random.random()]
        
        self.thread = threading.Thread(target=self.generate, daemon=True)
        self.thread.start()
        
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
        vertices = self.spherify_and_add_noise(vertices)
        
        # Convert the points to a triangle mesh
        vertices = self.convert_to_mesh(vertices)
        
        # Indices 
        indices = self.get_indices(vertices)
        
        # Get the normals
        normals = self.get_normals(
            numpy.array(vertices)
        )
        
        # Get average position
        self.parent.position = self.get_average_position(vertices)
        
        # Create a mesh
        self.mesh = vertices
        self.normals = normals
        self.indices = indices
        
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

    def spherify_and_add_noise(self, vertices):
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
            
            # Add noise
            _noise = self.avg([
                # Local noise
                noise.snoise3(x, y, z) * 0.25,
                noise.snoise3(x / 2, y / 2, z / 2) * 0.5,
                noise.snoise3(x / 4, y / 4, z / 4) * 2,
                noise.snoise3(x / 8, y / 8, z / 8) * 4,
                noise.snoise3(x / 16, y / 16, z / 16) * 8,
                noise.snoise3(x / 32, y / 32, z / 32) * 16,
                
                # Getting larger
                noise.snoise3(x / 320, y / 320, z / 320) * 32,
                noise.snoise3(x / 640, y / 640, z / 640) * 64,
                
                # Noise that produces continents
                noise.snoise3(x / 128, y / 128, z / 128) * 128,
            ])
            vector = [x, y, z]
            vector = self.normalize(vector)
            x = x + vector[0] * _noise
            y = y + vector[1] * _noise
            z = z + vector[2] * _noise
            
            vertices[i] = (x, y, z)
        return vertices

    @staticmethod
    def normalize(vector):
        length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        return vector[0] / length, vector[1] / length, vector[2] / length

    @staticmethod
    def avg(array):
        return sum(array) / len(array)
    
    def convert_to_mesh(self, vertices):
        # Convert the points to a triangle mesh
        new_vertices = []
        for i in range(0, len(vertices), 4):
            corner1 = vertices[i + 2]
            corner2 = vertices[i + 3]
            corner3 = vertices[i + 1]
            corner4 = vertices[i + 0]
            
            # This is for GL_TRIANGLES
            new_vertices.append(corner1)
            new_vertices.append(corner2)
            new_vertices.append(corner3)
            
            new_vertices.append(corner3)
            new_vertices.append(corner2)
            new_vertices.append(corner4)
        return new_vertices
    
    def get_indices(self, vertices):
        indices = []
        for i in range(len(vertices)):
            indices.append(i)
        return indices

    @staticmethod
    def get_normals(vtx):
        normals = []
        for i in range(0, len(vtx), 3):
            p1 = vtx[i]
            p2 = vtx[i + 1]
            p3 = vtx[i + 2]
            u = p2 - p1
            v = p3 - p1
            n = numpy.cross(u, v)
            normals.append(n)
            normals.append(n)
            normals.append(n)
        return normals
    
    def get_average_position(self, vertices):
        x = 0
        y = 0
        z = 0
        for vertex in vertices:
            x += vertex[0]
            y += vertex[1]
            z += vertex[2]
        x /= len(vertices)
        y /= len(vertices)
        z /= len(vertices)
        return (x, y, z)
        
    def draw(self):
        if self.mesh is not None:
            glColor3f(self.color[0], self.color[1], self.color[2])
            try:
                # Draw double-sided
                self.mesh.draw()
            except:
                self.mesh = Mesh(vertices=self.mesh, normals=self.normals, indices=self.indices)
                
    def __del__(self):
        del self.mesh
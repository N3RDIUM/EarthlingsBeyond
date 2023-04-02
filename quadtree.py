# Implementation of a QuadTree in Python
# This is for Terrain LoD
import noise
from mesh import Mesh
from OpenGL.GL import *
import math
import random
import threading

def midpoint(v1, v2):
    x = (v1[0] + v2[0]) / 2
    y = (v1[1] + v2[1]) / 2
    z = (v1[2] + v2[2]) / 2
    
    return (x, y, z)

class CubeTree:
    def __init__(self, size=320, position=[0,0,-160], rotation=[-13.5,0,0], rotation_vel=[0,0.001,0], camera=None):
        self.size = size
        self.position = position
        self.rotation = rotation
        self.rotation_vel = rotation_vel
        self.camera = camera
        self.drawing = False

        self.up = QuadTree(rect=[(0,size,0), (size,size,0), (size,size,size), (0,size,size)], level=1, parent=self)
        self.down = QuadTree(rect=[(0,0,0), (size,0,0), (size,0,size), (0,0,size)], level=1, parent=self)
        self.left = QuadTree(rect=[(0,0,0), (0,size,0), (0,size,size), (0,0,size)], level=1, parent=self)
        self.right = QuadTree(rect=[(size,0,0), (size,size,0), (size,size,size), (size,0,size)], level=1, parent=self)
        self.front = QuadTree(rect=[(0,0,0), (size,0,0), (size,size,0), (0,size,0)], level=1, parent=self)
        self.back = QuadTree(rect=[(0,0,size), (size,0,size), (size,size,size), (0,size,size)], level=1, parent=self)
        
    def draw(self):
        self.drawing = True
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        self.up.draw()
        self.down.draw()
        self.left.draw()
        self.right.draw()
        self.front.draw()
        self.back.draw()
        glPopMatrix()
        self.drawing = False
        
        self.rotation[0] += self.rotation_vel[0]
        self.rotation[1] += self.rotation_vel[1]
        self.rotation[2] += self.rotation_vel[2]
        
    def update(self):
        if self.camera is not None:
            self.up.update(self.camera.position)
            self.down.update(self.camera.position)
            self.left.update(self.camera.position)
            self.right.update(self.camera.position)
            self.front.update(self.camera.position)
            self.back.update(self.camera.position)

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
        del self.children[:]
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
        
    def update(self, camera_position):
        # Get the distance between the camera and the center of the quad
        center = self.position
        if len(center) == 0:
            return
        
        # Apply the parent's rotation
        if self.parent is not None:
            center = self.rotate_point(center, self.parent.rotation)
        
        # Calculate the distance
        distance = math.sqrt((center[0] - camera_position[0]) ** 2 + (center[1] - camera_position[1]) ** 2 + (center[2] - camera_position[2]) ** 2)
        
        # If the distance is less than the size of the quad, split the quad
        # Else, unite the quad
        if distance < self.size:
            if len(self.children) == 1 and self.level < 6:
                self.split()
        else:
            if len(self.children) > 1:
                self.unite()
            
        # Update the children
        for child in self.children:
            if type(child) is QuadTree:
                child.update(camera_position)

    @staticmethod
    def rotate_point(point, rotation):
        x = point[0]
        y = point[1]
        z = point[2]

        # Rotate around the x-axis
        y = y * math.cos(math.radians(rotation[0])) - z * math.sin(math.radians(rotation[0]))
        z = y * math.sin(math.radians(rotation[0])) + z * math.cos(math.radians(rotation[0]))
        z = -z  # Negate the z-coordinate after the first rotation

        # Rotate around the y-axis
        x = x * math.cos(math.radians(rotation[1])) + z * math.sin(math.radians(rotation[1]))
        z = -x * math.sin(math.radians(rotation[1])) + z * math.cos(math.radians(rotation[1]))

        # Rotate around the z-axis
        x = x * math.cos(math.radians(rotation[2])) - y * math.sin(math.radians(rotation[2]))
        y = x * math.sin(math.radians(rotation[2])) + y * math.cos(math.radians(rotation[2]))

        return -x, y, z

            
class LeafNode():
    def __init__(self, rect, level, parent, tesselate=6):
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
        
        # Get the normals
        normals = self.get_normals(vertices)
        
        # Get average position
        self.parent.position = self.get_average_position(vertices)
        
        # Create a mesh
        self.mesh = vertices
        
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
            
            _noise = noise.snoise3(x / 640, y / 640, z / 640) * 12
            length = math.sqrt(x**2 + y**2 + z**2) + _noise
            
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
            
            # This is for GL_TRIANGLES
            new_vertices.append(corner1)
            new_vertices.append(corner2)
            new_vertices.append(corner3)
            
            new_vertices.append(corner3)
            new_vertices.append(corner2)
            new_vertices.append(corner4)
        return new_vertices
    
    def get_normals(self, vertices):
        normals = []
        for i in range(0, len(vertices), 3):
            corner1 = vertices[i + 0]
            corner2 = vertices[i + 1]
            corner3 = vertices[i + 2]
            
            # Make a midpoint between each corner
            midpoint1 = midpoint(corner1, corner2)
            midpoint2 = midpoint(corner2, corner3)
            
            # Now, make a simple quad
            normal = self.cross_product(midpoint1, midpoint2)
            
            normals.append(normal)
            normals.append(normal)
            normals.append(normal)
        return normals
    
    @staticmethod
    def cross_product(a, b):
        x = a[1] * b[2] - a[2] * b[1]
        y = a[2] * b[0] - a[0] * b[2]
        z = a[0] * b[1] - a[1] * b[0]
        return (x, y, z)
    
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
                self.mesh = Mesh(vertices=self.mesh)
                
    def __del__(self):
        del self.mesh
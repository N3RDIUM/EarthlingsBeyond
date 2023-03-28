from OpenGL.GL import *
import glfw
from math import sin, cos, radians

class Camera(object):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0]):
        self.position = position
        self.rotation = rotation
        self.mouse_prev = glfw.get_cursor_pos(glfw.get_current_context())
    
    def update(self, window):
        # move forward
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1])) * 0.1
            self.position[2] += cos(radians(self.rotation[1])) * 0.1
            
        # move backward
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position[0] += sin(radians(self.rotation[1])) * 0.1
            self.position[2] -= cos(radians(self.rotation[1])) * 0.1
            
        # strafe left
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1] - 90)) * 0.1
            self.position[2] += cos(radians(self.rotation[1] - 90)) * 0.1
            
        # strafe right
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1] + 90)) * 0.1
            self.position[2] += cos(radians(self.rotation[1] + 90)) * 0.1
            
        # go up
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            self.position[1] -= 0.1
            
        # go down
        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            self.position[1] += 0.1
        
        # mouse look
        current_position = glfw.get_cursor_pos(window)
        delta = []
        delta.append(current_position[0] - self.mouse_prev[0])
        delta.append(current_position[1] - self.mouse_prev[1])
        self.mouse_prev = current_position
        
        self.rotation[0] += delta[1] * 0.1
        self.rotation[1] += delta[0] * 0.1
        
        if self.rotation[0] > 90:
            self.rotation[0] = 90
        elif self.rotation[0] < -90:
            self.rotation[0] = -90
        
        # update view
        glLoadIdentity()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glTranslatef(self.position[0], self.position[1], self.position[2])
from OpenGL.GL import *
import glfw
from math import sin, cos, radians

class Camera(object):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0]):
        self.position = position
        self.rotation = rotation
    
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
            self.position[0] += sin(radians(self.rotation[1] - 90)) * 0.1
            self.position[2] -= cos(radians(self.rotation[1] - 90)) * 0.1
            
        # strafe right
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position[0] += sin(radians(self.rotation[1] + 90)) * 0.1
            self.position[2] -= cos(radians(self.rotation[1] + 90)) * 0.1
            
        # go up
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            self.position[1] += 0.1
            
        # go down
        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            self.position[1] -= 0.1
        
        # update view
        glLoadIdentity()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glTranslatef(self.position[0], self.position[1], self.position[2])
        
    def mouse_motion(self, x, y):
        sensitivity = 0.5
        
        # calculate differences in mouse position
        x_diff = x - glfw.get_window_size(glfw.get_current_context())[0] / 2
        y_diff = y - glfw.get_window_size(glfw.get_current_context())[1] / 2
        
        # update rotation
        self.rotation[0] -= y_diff * sensitivity
        self.rotation[1] -= x_diff * sensitivity
        
        # keep rotation within bounds
        if self.rotation[0] > 90:
            self.rotation[0] = 90
        elif self.rotation[0] < -90:
            self.rotation[0] = -90

        glfw.set_cursor_pos(glfw.get_current_context(), glfw.get_window_size(glfw.get_current_context())[0] / 2,
                            glfw.get_window_size(glfw.get_current_context())[1] / 2)

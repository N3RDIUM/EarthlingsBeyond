import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

from quadtree import CubeTree
from camera import Camera

def main():
    # Initialize GLFW
    if not glfw.init():
        return
    
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(1600, 900, "Earthlings Beyond", None, None)
    if not window:
        glfw.terminate()
        return
    
    # Make the window's context current
    glfw.make_context_current(window)
    
    # Create a quadtree and camera
    terrain = CubeTree([0, 0, -16])
    camera = Camera()
    
    def _setup_3d():
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, glfw.get_window_size(window)[0] / glfw.get_window_size(window)[1], 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    frame = 0
        
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Render here, e.g. using pyOpenGL
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        _setup_3d()
        camera.update(window)
        terrain.draw()
        
        # Swap front and back buffers
        glfw.swap_buffers(window)
        
        # Poll for and process events
        glfw.poll_events()
        
        frame += 1
        
    # Terminate GLFW
    glfw.terminate()

if __name__ == '__main__':
    main()

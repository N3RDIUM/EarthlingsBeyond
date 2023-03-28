import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

from quadtree import QuadTree
from camera import Camera

def main():
    # Initialize GLFW
    if not glfw.init():
        return
    
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 480, "Earthlings Beyond", None, None)
    if not window:
        glfw.terminate()
        return
    
    # Make the window's context current
    glfw.make_context_current(window)
    
    # Create a quadtree and camera
    terrain = QuadTree([0, 0], [1, 1], 0)
    camera = Camera()
    
    def _setup_3d():
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, 640 / 480, 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Setup 3D rendering
        _setup_3d()
        
        # Clear the screen to black
        glClear(GL_COLOR_BUFFER_BIT)
        # Now we can set the color
        glColor3f(1, 1, 1)
        
        # Update the camera
        camera.update(window)
        
        # Draw the quadtree
        terrain.draw()
        
        # Swap front and back buffers
        glfw.swap_buffers(window)
        
        # Poll for and process events
        glfw.poll_events()
        
    # Terminate GLFW
    glfw.terminate()

if __name__ == '__main__':
    main()

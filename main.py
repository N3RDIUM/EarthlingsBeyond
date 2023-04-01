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
    camera = Camera(position=[0, 0, -1800])
    terrain = CubeTree(camera=camera,)
    
    def _setup_3d():
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, glfw.get_window_size(window)[0] / glfw.get_window_size(window)[1], 0.1, 1000000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    frame = 0
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glEnable(GL_FOG) # For a false sense of depth
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogfv(GL_FOG_COLOR, [0.0, 0.0, 0.0, 1.0])
    glFogf(GL_FOG_DENSITY, 0.001)
    glHint(GL_FOG_HINT, GL_NICEST)
    glFogf(GL_FOG_START, 10.0)
    glFogf(GL_FOG_END, 5000.0)
    glFogi(GL_FOG_COORD_SRC, GL_FRAGMENT_DEPTH)
        
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Render here, e.g. using pyOpenGL
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        _setup_3d()
        camera.update(window)
        
        # Draw the terrain
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

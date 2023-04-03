import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from quadtree import CubeTree
from camera import Camera

glutInit()

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
    camera = Camera(position=[0, 0, -180])
    terrain = CubeTree(camera=camera,)
    
    def _setup_3d():
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, glfw.get_window_size(window)[0] / glfw.get_window_size(window)[1], 0.1, 1000000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    frame = 0
    glEnable(GL_FOG) # For a false sense of depth
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, [0.0, 0.0, 0.0, 1.0])
    glFogf(GL_FOG_DENSITY, 0.1)
    glHint(GL_FOG_HINT, GL_NICEST)
    glFogf(GL_FOG_START, 10.0)
    glFogf(GL_FOG_END, 3200.0)
    glFogi(GL_FOG_COORD_SRC, GL_FRAGMENT_DEPTH)
    
    _setup_3d()
    glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(0.0, 0.0, 0.0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 3)(.05, .05, .05))
    glLightfv(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, (GLfloat * 1) (0.000009))
    glEnable(GL_LIGHT0)
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Render here, e.g. using pyOpenGL
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        _setup_3d()
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
        camera.update(window)
        terrain.draw()
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDisable(GL_COLOR_MATERIAL)
        
        terrain.update()
        
        # Swap front and back buffers
        glfw.swap_buffers(window)
        
        # Poll for and process events
        glfw.poll_events()
        
        frame += 1
        
    # Terminate GLFW
    glfw.terminate()

if __name__ == '__main__':
    main()

# Imports
import glfw
from OpenGL import GL as gl
from OpenGL import GLU as glu

# Create a new  window using GLFW
glfw.init()
window = glfw.create_window(640, 480, "[Currently in pre-beta stage]", None, None)
glfw.make_context_current(window)

# Run mainloop
while not glfw.window_should_close(window):
    glfw.poll_events()
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    
    gl.glClearColor(0, 0, 0, 1)
    
    # Sync events
    glfw.swap_buffers(window)
    glfw.poll_events()

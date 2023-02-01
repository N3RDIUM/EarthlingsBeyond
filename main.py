import pyglet
from pyglet.gl import *
from player import Player
from terrain import *

# Create a window
window = pyglet.window.Window(
    800, 600, caption="Earthlings Beyond", resizable=True)

# Initialize some variables
camera_position = [0, 0, 0]
camera = Player(window)
window.set_size(800, 600)


world = LoDWorld(camera, 4, 4, window=window)


def _setup_3d():
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window.width / window.height, 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


if __name__ == "__main__":
    # Create the event handler
    @window.event
    def on_draw():
        window.clear()
        _setup_3d()
        camera.draw()
        world.draw()

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        camera.on_mouse_motion(x, y, dx, dy)
        return pyglet.event.EVENT_HANDLED

    @window.event
    def on_key_press(symbol, modifiers):
        camera.on_key_press(symbol, modifiers)
        if symbol == pyglet.window.key.ESCAPE:
            return pyglet.event.EVENT_HANDLED

    @window.event
    def on_key_release(symbol, modifiers):
        camera.on_key_release(symbol, modifiers)

    @window.event
    def on_close():
        world.closed = True

    def on_update(delta_time):
        world.update(delta_time)
        camera.update(delta_time)

    # Run the application
    pyglet.clock.schedule(on_update)
    pyglet.app.run()

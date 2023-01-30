import math
import pyglet
import opensimplex
import numpy as np
from pyglet.gl import *
from player import FirstPersonCamera

# Create a window
window = pyglet.window.Window()

# Initialize some variables
camera_position = [0, 0, 0]
camera = FirstPersonCamera(window)
window.set_exclusive_mouse(True)

# Class for LoD terrain chunk
class LoDChunk:
    def __init__(self, player, position, size=16):
        self.player = player
        self.position = position
        self.size = size
        self.mesh = np.array([])
        self.heightmap = np.zeros((size + 2, size + 2))
        self.batch = pyglet.graphics.Batch()
        
    def generate(self):
        # Generate the heightmap
        for x in range(self.position[0] - 1, self.position[0] + self.size + 1):
            for z in range(self.position[1] - 1, self.position[1] + self.size + 1):
                index_x = x - self.position[0] + 1
                index_z = z - self.position[1] + 1
                self.heightmap[index_x, index_z] = opensimplex.noise2(x / 16, z / 16) * 4
        
        for x in range(self.position[0], self.position[0] + self.size):
            for z in range(self.position[1], self.position[1] + self.size):
                self.mesh = np.append(self.mesh, [
                    x, self.heightmap[x - self.position[0], z - self.position[1]], z,
                    x + 1, self.heightmap[x - self.position[0] + 1, z - self.position[1]], z,
                    x, self.heightmap[x - self.position[0], z - self.position[1] + 1], z + 1,

                    x + 1, self.heightmap[x - self.position[0] + 1, z - self.position[1]], z,
                    x + 1, self.heightmap[x - self.position[0] + 1, z - self.position[1] + 1], z + 1,
                    x, self.heightmap[x - self.position[0], z - self.position[1] + 1], z + 1
                ])
        
        # Update the batch
        self.batch.add_indexed(len(self.mesh) // 3, GL_LINES, None, range(len(self.mesh) // 3), ('v3f', self.mesh))
        
    def draw(self):
        self.batch.draw()
        
class LoDWorld:
    def __init__(self, player, chunk_size=16, render_distance=4):
        self.player = player
        self.chunk_size = chunk_size
        self.render_distance = render_distance
        self.chunks = []
        
    def generate(self):
        for x in range(-self.render_distance, self.render_distance):
            for z in range(-self.render_distance, self.render_distance):
                chunk = LoDChunk(self.player, [x * self.chunk_size, z * self.chunk_size], self.chunk_size)
                chunk.generate()
                self.chunks.append(chunk)
                
    def draw(self):
        for chunk in self.chunks:
            chunk.draw()
            
world = LoDWorld(camera, 16, 4)
world.generate()

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
        return pyglet.event.EVENT_HANDLED
    
    def on_update(delta_time):
        camera.update(delta_time)

    # Run the application
    pyglet.clock.schedule(on_update)
    pyglet.app.run()

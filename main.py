import random
import pyglet
import opensimplex
import math
import numpy as np
from pyglet.gl import *
from player import FirstPersonCamera

# Create a window
window = pyglet.window.Window(
    800, 600, caption="Earthlings Beyond", resizable=True)

# Initialize some variables
camera_position = [0, 0, 0]
camera = FirstPersonCamera(window, movement_speed=16)
window.set_exclusive_mouse(True)
window.set_size(800, 600)

# Class for LoD terrain chunk


class LoDChunk:
    def __init__(self, player, position, size=16, LoD=1):
        self.player = player
        self.position = position
        self.size = size
        self.mesh = np.array([])
        self.heightmap = np.zeros((size * 2 + 2, size * 2 + 2))
        self.batch = pyglet.graphics.Batch()
        self.color = (random.random(), random.random(), random.random())
        self.enabled = False
        self.generated = False
        self.LoD = LoD

    def generate(self):
        # Generate the heightmap
        for x in range(self.position[0] - self.size - 1, self.position[0] + self.size + 1, self.LoD):
            for z in range(self.position[1] - self.size - 1, self.position[1] + self.size + 1, self.LoD):
                index_x = x - self.position[0] + 1
                index_z = z - self.position[1] + 1
                self.heightmap[index_x, index_z] = (
                    opensimplex.noise2((x + self.position[0]) / 64, (z + self.position[1]) / 64) * 32 +
                    opensimplex.noise2((x + self.position[0]) / 32, (z + self.position[1]) / 32) * 16 +
                    opensimplex.noise2((x + self.position[0]) / 16, (z + self.position[1]) / 16) * 8 +
                    opensimplex.noise2((x + self.position[0]) / 8, (z + self.position[1]) / 8) * 4 +
                    opensimplex.noise2((x + self.position[0]) / 4, (z + self.position[1]) / 4) * 2 +
                    opensimplex.noise2((x + self.position[0]) / 2, (z + self.position[1]) / 2) +
                    opensimplex.noise2((x + self.position[0]), (z + self.position[1])) +
                    opensimplex.noise2(
                        (x + self.position[0]) * 2, (z + self.position[1]) * 2)
                )

        for x in range(self.position[0] - self.size, self.position[0] + self.size, self.LoD):
            for z in range(self.position[1] - self.size, self.position[1] + self.size, self.LoD):
                self.mesh = np.append(self.mesh, [
                    x, self.heightmap[(x - self.position[0]) * self.LoD,
                                      (z - self.position[1]) * self.LoD], z,
                    x +
                    1, self.heightmap[(x - self.position[0] +
                                      1) * self.LoD, (z - self.position[1]) * self.LoD], z,
                    x, self.heightmap[(x - self.position[0]) * self.LoD,
                                      (z - self.position[1] + 1) * self.LoD], z + 1,

                    x +
                    1, self.heightmap[(x - self.position[0] +
                                      1) * self.LoD, (z - self.position[1]) * self.LoD], z,
                    x + 1, self.heightmap[(x - self.position[0] +
                                          1) * self.LoD, (z - self.position[1] + 1) * self.LoD], z + 1,
                    x, self.heightmap[(x - self.position[0]) * self.LoD,
                                      (z - self.position[1] + 1) * self.LoD], z + 1
                ])

        # Update the batch
        self.batch.add_indexed(len(self.mesh) // 3, GL_LINES,
                               None, range(len(self.mesh) // 3), ('v3f', self.mesh))

        # Enable the chunk
        self.generated = True

    def draw(self):
        if not self.enabled:
            return
        glPushMatrix()
        glTranslatef(self.position[0], 0, self.position[1])
        glColor3f(*self.color)
        self.batch.draw()
        glPopMatrix()


class LoDWorld:
    def __init__(self, player, chunk_size=16, render_distance=12):
        self.player = player
        self.chunk_size = chunk_size
        self.render_distance = render_distance
        self.chunks = []

    def generate(self):
        for x in range(-self.render_distance, self.render_distance):
            for z in range(-self.render_distance, self.render_distance):
                chunk = LoDChunk(
                    self.player, [x * self.chunk_size, z * self.chunk_size], self.chunk_size)
                chunk.generate()
                self.chunks.append(chunk)

    def draw(self):
        for chunk in self.chunks:
            chunk.draw()

    def update(self, delta_time):
        # Based on the player's position, update the chunks
        position = [self.player.position[0] // 2,
                    self.player.position[1] // 2,
                    self.player.position[2] // 2]
        pchunk = [int(position[0] // self.chunk_size),
                  int(position[2] // self.chunk_size)]
        for chunk in self.chunks:
            if not math.dist([position[0], position[2]], chunk.position) < self.render_distance * self.chunk_size:
                chunk.enabled = False
            else:
                chunk.enabled = True

        positions = []
        for x in range(-self.render_distance+pchunk[0], self.render_distance+pchunk[0]):
            for z in range(-self.render_distance+pchunk[1], self.render_distance+pchunk[1]):
                positions.append([x, z])
        for position in positions:
            if not [position[0] * self.chunk_size, position[1] * self.chunk_size] in [chunk.position for chunk in self.chunks]:
                chunk = LoDChunk(self.player, [
                                 position[0] * self.chunk_size, position[1] * self.chunk_size], self.chunk_size)
                self.chunks.append(chunk)
        for chunk in self.chunks:
            if not [chunk.position[0] // self.chunk_size, chunk.position[1] // self.chunk_size] in positions:
                self.chunks.remove(chunk)
        for chunk in self.chunks:
            if not chunk.generated:
                chunk.generate()
                break


world = LoDWorld(camera, 16, 8)
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
        world.update(delta_time)

    # Run the application
    pyglet.clock.schedule(on_update)
    pyglet.app.run()

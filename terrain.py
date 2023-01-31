import math
import random
from pyglet.graphics import Batch
import numpy as np
from pyglet.gl import *
import noise
import threading
import time

# Class for LoD terrain chunk


class LoDChunk:
    def __init__(self, player, position, size=16, resolution=8):
        self.player = player
        self.position = position
        self.size = size
        self.mesh = np.array([])
        self.heightmap = np.zeros((resolution * 2 + 2, resolution * 2 + 2))
        self.batch = Batch()
        self.color = (0.5 + random.random() / 2, 0.5 +
                      random.random() / 2, 0.5 + random.random() / 2)
        self.enabled = False
        self.generated = False
        self.batch_updated = False
        self.resolution = resolution

    def generate(self):
        step = self.size * 2 / self.resolution

        # Generate the heightmap
        for x in range(self.resolution * 2 + 2):
            for z in range(self.resolution * 2 + 2):
                _x = (self.position[0] - self.size) + x * step / 2
                _z = (self.position[1] - self.size) + z * step / 2
                self.heightmap[x][z] = (
                    noise.snoise2(_x / 64, _z / 64) * 32 +
                    noise.snoise2(_x / 32, _z / 32) * 16 +
                    noise.snoise2(_x / 16, _z / 16) * 8 +
                    noise.snoise2(_x / 8, _z / 8) * 4 +
                    noise.snoise2(_x / 4, _z / 4) * 2 +
                    noise.snoise2(_x / 2, _z / 2) +
                    noise.snoise2(_x, _z) +
                    noise.snoise2(_x * 2, _z * 2)
                )

        # Generate the mesh
        x = self.position[0] - self.size
        z = self.position[1] - self.size
        while x < self.position[0] + self.size:
            while z < self.position[1] + self.size:
                # Get the height of the 4 corners
                h1 = self.heightmap[int((x - self.position[0] + self.size) / step)][int(
                    (z - self.position[1] + self.size) / step)]
                h2 = self.heightmap[int((x - self.position[0] + self.size) / step)][int(
                    (z + step - self.position[1] + self.size) / step)]
                h3 = self.heightmap[int((x + step - self.position[0] + self.size) / step)][int(
                    (z - self.position[1] + self.size) / step)]
                h4 = self.heightmap[int((x + step - self.position[0] + self.size) / step)][int(
                    (z + step - self.position[1] + self.size) / step)]

                # Add the vertices
                self.mesh = np.append(self.mesh, [x, h1, z])
                self.mesh = np.append(self.mesh, [x, h2, z + step])
                self.mesh = np.append(self.mesh, [x + step, h3, z])

                self.mesh = np.append(self.mesh, [x + step, h3, z])
                self.mesh = np.append(self.mesh, [x, h2, z + step])
                self.mesh = np.append(self.mesh, [x + step, h4, z + step])

                z += step
            x += step
            z = self.position[1] - self.size

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

        if self.generated and not self.batch_updated:
            # Update the batch
            self.batch.add_indexed(len(self.mesh) // 3, GL_LINES,
                                   None, range(len(self.mesh) // 3), ('v3f', self.mesh))
            self.batch_updated = True


class LoDWorld:
    def __init__(self, player, chunk_size=16, render_distance=12, window=None):
        self.player = player
        self.chunk_size = chunk_size
        self.render_distance = render_distance
        self.chunks = []
        self.to_generate = []
        self.closed = False
        
        self.thread = threading.Thread(target=self.generate)
        self.thread.start()
        

    def generate(self):
        for x in range(-self.render_distance, self.render_distance):
            for z in range(-self.render_distance, self.render_distance):
                chunk = LoDChunk(
                    self.player, [x * self.chunk_size, z * self.chunk_size], self.chunk_size)
                self.chunks.append(chunk)
                self.to_generate.append(chunk)
        
        self.generation_thread = threading.Thread(target=self.update_thread, daemon=True)
        self.generation_thread.start()

    def draw(self):
        for chunk in self.chunks:
            chunk.draw()

    def update(self, delta_time):
        # Based on the player's position, update the chunks
        position = [self.player.state["position"][0] // 2,
                    self.player.state["position"][1] // 2,
                    self.player.state["position"][2] // 2]
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
                self.to_generate.append(chunk)
        for chunk in self.chunks:
            if not [chunk.position[0] // self.chunk_size, chunk.position[1] // self.chunk_size] in positions:
                self.chunks.remove(chunk)
                
    def update_thread(self):
        while not self.closed:
            if len(self.to_generate) > 0:
                chunk = self.to_generate[random.randint(0, len(self.to_generate)-1)]
                chunk.generate()
                self.to_generate.remove(chunk)
            time.sleep(1 / 30)

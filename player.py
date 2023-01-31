from pyglet.gl import *
from pyglet.window import key
import math

class Player:
    """
    Player
    """

    def __init__(self, window=None, world=None):
        """
        Initialize the player.
        :param window: The window object.
        :param world: The world object.
        """
        # Set properties
        self.window = window
        self.world = world

        # Lock mouse pointer
        self.lock = True
        window.set_exclusive_mouse(True)
        
        # Bind keys
        self.keys = key.KeyStateHandler()
        window.push_handlers(self.keys)
        self.pressed = []

        # Default state
        self.state = {
            "position": [0, 0, 0],
            "rotation": [0, 0, 0],
            "velocity": [0, 0, 0],
            "friction": 0.9,
            "gravity": 9.81,
            "speed": 0.1,
            "zoom": False,
            "fly": False,
        }
        
    def on_mouse_motion(self, x, y, dx, dy):
        """
        Update the player on mouse motion.
        :param x: The x position.
        :param y: The y position.
        :param dx: The x delta.
        :param dy: The y delta.
        """
        # mouse rotation: get dx and dy
        if self.lock:
            self.state["rotation"][0] += dy/8  # pitch
            self.state["rotation"][1] -= dx/8  # yaw
            if self.state["rotation"][0] > 90:  # clamp pitch
                self.state["rotation"][0] = 90
            elif self.state["rotation"][0] < -90:  # clamp pitch
                self.state["rotation"][0] = -90
                
    def on_key_press(self, symbol, modifiers):
        """
        Update the player on key press.
        :param symbol: The symbol.
        :param modifiers: The modifiers.
        """
        # ESC to release mouse
        if symbol == pyglet.window.key.ESCAPE:
            self.window.set_exclusive_mouse(False)
            self.lock = False
        # L to lock mouse
        if symbol == pyglet.window.key.L:
            self.window.set_exclusive_mouse(True)
            self.lock = True
            
        self.pressed.append(symbol)
        
    def on_key_release(self, symbol, modifiers):
        """
        Update the player on key release.
        :param symbol: The symbol.
        :param modifiers: The modifiers.
        """
        if symbol in self.pressed:
            self.pressed.remove(symbol)

    def update(self, delta_time):
        """
        Update the player on drawcall.
        """
        # Get the state
        sens = self.state["speed"]
        rotY = math.radians(-self.state["rotation"][1])
        dx, dz = math.sin(rotY), math.cos(rotY)
        
        delta_ratio = delta_time * 60
        sens *= delta_ratio
        
        # Key handlers
        if key.W in self.pressed:
            self.state["velocity"][0] += dx*sens
            self.state["velocity"][2] -= dz*sens
        if key.S in self.pressed:
            self.state["velocity"][0] -= dx*sens
            self.state["velocity"][2] += dz*sens
        if key.A in self.pressed:
            self.state["velocity"][0] -= dz*sens
            self.state["velocity"][2] -= dx*sens
        if key.D in self.pressed:
            self.state["velocity"][0] += dz*sens
            self.state["velocity"][2] += dx*sens
        if key.MOD_CTRL in self.pressed or key.LCTRL in self.pressed:
            self.state["speed"] = 0.05
        else:
            self.state["speed"] = 0.03
            
        # SHIFT to fly down
        if key.MOD_SHIFT in self.pressed or key.LSHIFT in self.pressed:
            self.state["velocity"][1] -= 0.05
        # SPACE to fly up
        if key.SPACE in self.pressed:
            self.state["velocity"][1] += 0.05

        # Apply velocity
        self.state["position"][0] += self.state["velocity"][0]
        self.state["position"][1] += self.state["velocity"][1]
        self.state["position"][2] += self.state["velocity"][2]

        # Apply friction
        self.state["velocity"][0] *= self.state["friction"]
        self.state["velocity"][1] *= self.state["friction"]
        self.state["velocity"][2] *= self.state["friction"]

    def draw(self):
        """
        Draw the player.
        """
        # Draw the player
        glRotatef(-self.state["rotation"][0], 1, 0, 0)
        glRotatef(-self.state["rotation"][1], 0, 1, 0)
        glTranslatef(-self.state["position"][0], -
                     self.state["position"][1], -self.state["position"][2])

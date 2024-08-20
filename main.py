import pyglet
import math
import random
from pyglet.gl import *

# Constants
ROTATION_SPEED = 2
ACCELERATION = 200
FRICTION = 0.99
RIGHT_ACCELERATION = 200
LASER_SPEED = 500
LASER_LIFETIME = 1.0
FIRE_RATE = 0.3

# Load images
ship_image = pyglet.image.load('playerShip2_red.png')
laser_image = pyglet.image.load('laserBlue01.png')
asteroid_images = [
    pyglet.image.load('meteorBrown_big1.png'),
    pyglet.image.load('meteorGrey_big4.png'),
    pyglet.image.load('meteorGrey_small2.png'),
]

# Center image anchors
ship_image.anchor_x = ship_image.width // 2
ship_image.anchor_y = ship_image.height // 2
laser_image.anchor_x = laser_image.width // 2
laser_image.anchor_y = laser_image.height // 2

batch = pyglet.graphics.Batch()


class SpaceObject:
    def __init__(self, x, y, x_speed, y_speed, rotation, sprite):
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.rotation = rotation
        self.sprite = sprite

    def tick(self, dt):
        self.x += self.x_speed * dt
        self.y += self.y_speed * dt

        if self.x < 0:
            self.x = window.width
        elif self.x > window.width:
            self.x = 0
        if self.y < 0:
            self.y = window.height
        elif self.y > window.height:
            self.y = 0

        self.x_speed *= FRICTION
        self.y_speed *= FRICTION

        self.sprite.rotation = 90 - math.degrees(self.rotation)
        self.sprite.x = self.x
        self.sprite.y = self.y


class Spaceship(SpaceObject):
    def __init__(self, x, y):
        self.fire_cooldown = 0
        sprite = pyglet.sprite.Sprite(ship_image, batch=batch)
        super().__init__(x, y, 0, 0, 0, sprite)

    def rotate_left(self, dt):
        self.rotation -= ROTATION_SPEED * dt

    def rotate_right(self, dt):
        self.rotation += ROTATION_SPEED * dt

    def accelerate(self, dt):
        self.x_speed += dt * ACCELERATION * math.cos(self.rotation)
        self.y_speed += dt * ACCELERATION * math.sin(self.rotation)

    def move_right(self, dt):
        self.x_speed += dt * RIGHT_ACCELERATION

    def fire(self):
        if self.fire_cooldown <= 0:
            laser_sprite = pyglet.sprite.Sprite(laser_image, batch=batch)
            laser = Laser(self.x, self.y, self.x_speed, self.y_speed, self.rotation, laser_sprite)
            lasers.append(laser)
            self.fire_cooldown = FIRE_RATE


class Laser(SpaceObject):
    def __init__(self, x, y, x_speed, y_speed, rotation, sprite):
        super().__init__(x, y, x_speed + LASER_SPEED * math.cos(rotation), y_speed + LASER_SPEED * math.sin(rotation),
                         rotation, sprite)
        self.lifetime = LASER_LIFETIME

    def tick(self, dt):
        super().tick(dt)
        self.lifetime -= dt

        if self.lifetime <= 0:
            lasers.remove(self)


class Asteroid(SpaceObject):
    def __init__(self):
        x_speed = random.uniform(-50, 50)
        y_speed = random.uniform(-50, 50)
        rotation = random.uniform(0, 2 * math.pi)

        image = random.choice(asteroid_images)
        sprite = pyglet.sprite.Sprite(image, batch=batch)

        if random.choice([True, False]):
            x = random.choice([0, window.width])
            y = random.uniform(0, window.height)
        else:
            x = random.uniform(0, window.width)
            y = random.choice([0, window.height])

        super().__init__(x, y, x_speed, y_speed, rotation, sprite)


window = pyglet.window.Window()
keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)

spaceship = Spaceship(400, 300)
asteroids = [Asteroid() for _ in range(5)]
lasers = []

@window.event
def on_draw():
    window.clear()
    batch.draw()


def update(dt):
    if keys[pyglet.window.key.LEFT]:
        spaceship.rotate_left(dt)
    if keys[pyglet.window.key.RIGHT]:
        spaceship.rotate_right(dt)
    if keys[pyglet.window.key.UP]:
        spaceship.accelerate(dt)
    if keys[pyglet.window.key.D]:
        spaceship.move_right(dt)
    if keys[pyglet.window.key.SPACE]:
        spaceship.fire()

    spaceship.fire_cooldown -= dt

    spaceship.tick(dt)
    for asteroid in asteroids:
        asteroid.tick(dt)
    for laser in lasers:
        laser.tick(dt)


pyglet.clock.schedule_interval(update, 1 / 60.0)

pyglet.app.run()

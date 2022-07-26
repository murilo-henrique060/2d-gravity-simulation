from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame.locals import *
import math
import numpy as np
from cartesianPlane import Circle, Line, CartesianPlane, draw

# Gravity constant
G = 6.67408 * 10 ** -11

class Body(Circle):
    def __init__(self, plane, color: tuple | list, center: tuple | list, radius: int | float, initial_speed: tuple | list = [0, 0], initial_acceleration: tuple | list = [0, 0], mass: int = 1):
        super().__init__(plane, color, center, radius)

        self.center = np.float64(np.array(self.center))

        self.speed = np.float64(np.array(initial_speed))
        self.acceleration = np.float64(np.array(initial_acceleration))
        self.mass = mass * 10 ** 6

        self.direction = Line(self.plane, (255, 255, 255), self.center, self.center + self.speed * 10)

    def update(self):
        self.center[0] += self.speed[0]
        self.center[1] += self.speed[1]

        self.speed[0] += self.acceleration[0]
        self.speed[1] += self.acceleration[1]

        self.direction.start = self.center
        self.direction.end = self.center + self.speed * 10

    def gravity(self, other):
        distance = math.dist(self.center, other.center)
        angle = math.atan2(other.center[1] - self.center[1], other.center[0] - self.center[0]) # radians
        force = (G * ((self.mass * other.mass) / (distance ** 2)))

        self.acceleration[0] = math.cos(angle) * force / self.mass
        self.acceleration[1] = math.sin(angle) * force / self.mass

class Group():
    def __init__(self, *bodies: Body):
        self.group = []

        self.simulation = False

        self.add(*bodies)

    def add(self, *bodies: Body):
        for body in bodies:
            self.group.append(body)

    def update(self):
        if self.simulation:
            for body in self.group:
                for other in self.group:
                    if body != other:
                        body.gravity(other)

            for body in self.group:
                body.update()

pygame.init()
screen = pygame.display.set_mode((500, 500))
plane = CartesianPlane(screen)

body = Body(plane, (255, 0, 0), (0, 0), 50, [0, 0], [0, 0], 10 ** 4)
body2 = Body(plane, (0, 0, 255), (100, 100), 10, [0, 0], [0, 0], 1)
body_group = Group(body, body2)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

        if event.type == KEYUP and event.key == K_ESCAPE:
            body_group.simulation = not body_group.simulation

        plane.event_handling(event)

    plane.debug(
        fps=f'{clock.get_fps():.1f}',
        body_2_angle=f'{math.degrees(math.atan2(body2.direction.end[1] - body2.direction.start[1], body2.direction.end[0] - body2.direction.start[0])):.2f}',
        body_2_center=f'{body2.center}',
        body_2_speed=f'{body2.speed[0]*100000:.2f} {body2.speed[1]*100000:.2f}',
        body_2_acceleration=f'{body2.acceleration[0]*100000:.2f} {body2.acceleration[1]*100000:.2f}',
    )

    clock.tick()
    plane.update()
    body_group.update()
    draw.line(plane, (255, 255, 255), body.center, body2.center)
    pygame.display.update()
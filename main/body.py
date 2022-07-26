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

        self.direction = Line(self.plane, (255, 255, 255), self.center, self.center + self.speed * 100)

    def point_in_circle(self, point: tuple | list):
        return math.dist(self.center, point) <= self.radius

    def update(self):
        self.center[0] += self.speed[0]
        self.center[1] += self.speed[1]

        self.speed[0] += self.acceleration[0]
        self.speed[1] += self.acceleration[1]

        self.direction.start = self.center
        self.direction.end = self.center + self.speed * 100

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

        self.focus = None

    def point_in_group(self, point: tuple | list):
        for body in self.group:
            if body.point_in_circle(point):
                return body
        return None

    def add(self, *bodies: Body):
        for body in bodies:
            self.group.append(body)

    def update(self):
        if self.simulation:
            for i in range(1, 10):
                for body in self.group:
                    for other in self.group:
                        if body != other:
                            body.gravity(other)

                for body in self.group:
                    body.update()

            if self.focus:
                center = [self.focus.plane.size[0] // 2, self.focus.plane.size[1] // 2]
                focus_center = self.focus.plane.plane_to_screen(self.focus.center)
                diff = [
                    focus_center[0] - center[0],
                    focus_center[1] - center[1]
                ]

                self.focus.plane.offset[0] -= diff[0] / self.focus.plane.scale_factor
                self.focus.plane.offset[1] -= diff[1] / self.focus.plane.scale_factor


pygame.init()
screen = pygame.display.set_mode((500, 500))
plane = CartesianPlane(screen)

body = Body(plane, (255, 0, 0), (0, 0), 50, [0, 0], [0, 0], 10 ** 4)
body2 = Body(plane, (0, 0, 255), (0, 100), 10, [0.081, 0], [0, 0], 1)
body_group = Group(body, body2)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

        if event.type == KEYUP and event.key == K_SPACE:
            body_group.simulation = not body_group.simulation

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            body_group.focus = body_group.point_in_group(plane.screen_to_plane(pygame.mouse.get_pos()))

        plane.event_handling(event)

    plane.debug(
        fps=f'{clock.get_fps():.1f}',
        state='running' if body_group.simulation else 'paused',
    )

    clock.tick(120)
    plane.update()
    body_group.update()
    draw.line(plane, (255, 255, 255), body.center, body2.center)
    pygame.display.update()
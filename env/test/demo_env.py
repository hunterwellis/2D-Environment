"""
Basic demo of 2D robot manipulation environment, as part of my Master's thesis
Use WASD to move.

Hunter Ellis 2024
"""

import pygame
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d
import random
import math
from enum import Enum, auto

movement = {"forward": False,
            "backward": False,
            "rotate_left": False,
            "rotate_right": False}


class Shapes(Enum):
    SQUARE = auto()
    CIRCLE = auto()
    # TRIANGLE = auto()


# add shapes to the environment
def add_shape(space, size, mass, type):

    body = pymunk.Body()
    body.position = Vec2d(
        random.uniform(size, 502 - size),
        random.uniform(size, 502 - size),
    )
    body.angle = random.uniform(-math.pi, math.pi)
    space.add(body)

    if type is Shapes.SQUARE:
        shape = pymunk.Poly.create_box(body, (size, size))
    else:
        shape = pymunk.Circle(body, size)
    # else shape == TRIANGLE:

    shape.mass = mass
    shape.friction = 0.7
    shape.color = (random.randint(50, 255),
                   random.randint(50, 255),
                   random.randint(50, 255), 255)
    space.add(shape)

    pivot = pymunk.PivotJoint(space.static_body, body, (0, 0), (0, 0))
    space.add(pivot)
    pivot.max_bias = 0
    pivot.max_force = 1000

    gear = pymunk.GearJoint(space.static_body, body, 0.0, 1.0)
    space.add(gear)
    gear.max_bias = 0
    gear.max_force = 5000


# update game
def update(space, dt):
    global agent_body
    global agent_ctrl

    agent_ctrl.velocity = Vec2d(0, 0)
    agent_ctrl.angular_velocity = 0

    if movement["rotate_left"]:
        agent_ctrl.angular_velocity = -3
    if movement["rotate_right"]:
        agent_ctrl.angular_velocity = 3

    if movement["forward"]:
        direction = agent_body.rotation_vector.rotated(-math.pi / 2) * 100
        agent_ctrl.velocity = direction
    if movement["backward"]:
        direction = agent_body.rotation_vector.rotated(-math.pi / 2) * -100
        agent_ctrl.velocity = direction

    space.step(dt)

    update_sym_state(space)


def update_sym_state(space):
    None


def init():
    space = pymunk.Space()
    space.iterations = 10
    space.sleep_time_threshold = 0.5

    static_body = space.static_body

    boundaries = [
        ((0, 0), (0, 500)),
        ((0, 500), (500, 500)),
        ((500, 500), (500, 0)),
        ((500, 0), (0, 0)),
    ]

    for start, end in boundaries:
        shape = pymunk.Segment(static_body, start, end, 1.0)
        shape.elasticity = 1
        shape.friction = 1
        space.add(shape)

    for _ in range(10):
        add_shape(space, 15, 1, Shapes.CIRCLE)
    for _ in range(10):
        add_shape(space, 20, 1, Shapes.SQUARE)

    global agent_ctrl
    agent_ctrl = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    agent_ctrl.position = 250, 250
    space.add(agent_ctrl)

    global agent_body
    agent_body = pymunk.Body(10, pymunk.moment_for_box(10, (30, 30)))
    agent_body.position = 250, 250
    space.add(agent_body)

    agent_body_rectangles = [
        (0, 5, 35, 5),
        (-15, 0, 5, 10),
        (15, 0, 5, 10)
    ]

    for offset_x, offset_y, width, height in agent_body_rectangles:
        box_points = [(-width / 2, -height / 2), (width / 2, -height / 2),
                      (width / 2, height / 2), (-width / 2, height / 2)]
        box_points = [(x + offset_x, y + offset_y) for x, y in box_points]
        shape = pymunk.Poly(agent_body, box_points)
        shape.color = (255, 255, 255, 0)
        space.add(shape)

    pivot = pymunk.PivotJoint(agent_ctrl, agent_body, (0, 0), (0, 0))
    space.add(pivot)
    pivot.max_bias = 0.0
    pivot.max_force = 10000.0

    gear = pymunk.GearJoint(agent_ctrl, agent_body, 0.0, 1.0)
    space.add(gear)
    gear.error_bias = 0.0
    gear.max_bias = 1.2
    gear.max_force = 50000.0

    return space


def custom_draw(space, screen):
    for shape in space.shapes:
        if isinstance(shape, pymunk.Circle):
            pos = int(shape.body.position.x), int(shape.body.position.y)
            pygame.draw.circle(screen, shape.color, pos, int(shape.radius))
        elif isinstance(shape, pymunk.Poly):
            vertices = [v.rotated(shape.body.angle) + shape.body.position for v in shape.get_vertices()]
            vertices = [(int(v.x), int(v.y)) for v in vertices]
            pygame.draw.polygon(screen, shape.color, vertices)
        elif isinstance(shape, pymunk.Segment):
            body = shape.body
            pv1 = body.position + shape.a.rotated(body.angle)
            pv2 = body.position + shape.b.rotated(body.angle)
            p1 = int(pv1.x), int(pv1.y)
            p2 = int(pv2.x), int(pv2.y)
            pygame.draw.line(screen, pygame.Color("gray"), p1, p2, int(shape.radius))


space = init()
pygame.init()

screen = pygame.display.set_mode((502, 502))
clock = pygame.time.Clock()
draw_options = pymunk.pygame_util.DrawOptions(screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                movement["forward"] = True
            elif event.key == pygame.K_DOWN:
                movement["backward"] = True
            elif event.key == pygame.K_LEFT:
                movement["rotate_left"] = True
            elif event.key == pygame.K_RIGHT:
                movement["rotate_right"] = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                movement["forward"] = False
            elif event.key == pygame.K_DOWN:
                movement["backward"] = False
            elif event.key == pygame.K_LEFT:
                movement["rotate_left"] = False
            elif event.key == pygame.K_RIGHT:
                movement["rotate_right"] = False

    screen.fill(pygame.Color("black"))
    custom_draw(space, screen)
    fps = 60
    update(space, 1 / fps)
    pygame.display.flip()
    clock.tick(fps)

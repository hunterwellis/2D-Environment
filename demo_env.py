
"""
Basic demonstrationg of a 2D-environment where an agent can move randomly generated objects aroundself.

Use WASD to move.
"""

import random
import pygame
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d


movement = {"forward": False, "backward": False, "rotate_left": False, "rotate_right": False}

def update(space, dt, surface):
    global tank_body
    global tank_control_body

    tank_control_body.velocity = Vec2d(0, 0)
    tank_control_body.angular_velocity = 0

    if movement["rotate_left"]:
        tank_control_body.angular_velocity = -3  
    if movement["rotate_right"]:
        tank_control_body.angular_velocity = 3  

    
    if movement["forward"]:
        direction = tank_body.rotation_vector * 100
        tank_control_body.velocity = direction
    if movement["backward"]:
        direction = tank_body.rotation_vector * -100
        tank_control_body.velocity = direction

    
    space.step(dt)

    
    update_object_data(space)


def add_shape(space, size, mass, is_circle=False):
    body = pymunk.Body()
    body.position = Vec2d(
        random.uniform(size, 640 - size),
        random.uniform(size, 480 - size),
    )
    body.angle = random.uniform(-3.150, 3.150)
    space.add(body)

    
    if is_circle:
        shape = pymunk.Circle(body, size)
    else:
        shape = pymunk.Poly.create_box(body, (size, size))

    shape.mass = mass
    shape.friction = 0.7  
    shape.elasticity = 0
    shape.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255), 255)
    space.add(shape)
    
    return body


def update_object_data(space):
    print("\033[H", end="")  
    print("------------ Object Data ------------")

    objects_data = []

    
    tank_data = f"Shape: Tank, Color: (0, 255, 100, 255), Position: ({tank_body.position.x:.2f}, {tank_body.position.y:.2f}), Rotation: {tank_body.angle:.2f}"
    objects_data.append(tank_data)

    
    for shape in space.shapes:
        if shape.body == tank_body:
            continue  
        if isinstance(shape, pymunk.Circle):
            shape_type = "Circle"
        elif isinstance(shape, pymunk.Poly):
            shape_type = "Square"
        else:
            continue

        color = shape.color if hasattr(shape, "color") else (255, 255, 255, 255)
        position = shape.body.position
        rotation = shape.body.angle
        object_info = f"Shape: {shape_type}, Color: {color}, Position: ({position.x:.2f}, {position.y:.2f}), Rotation: {rotation:.2f}"
        objects_data.append(object_info)

    
    for obj in objects_data:
        print(obj)
    print("-------------------------")


def init():
    space = pymunk.Space()
    space.iterations = 10
    space.sleep_time_threshold = 0.5

    static_body = space.static_body

    
    boundaries = [
        ((1, 1), (1, 480)),
        ((640, 1), (640, 480)),
        ((1, 1), (640, 1)),
        ((1, 480), (640, 480)),
    ]
    for start, end in boundaries:
        shape = pymunk.Segment(static_body, start, end, 1.0)
        shape.elasticity = 1
        shape.friction = 1
        space.add(shape)

    
    for _ in range(25):
        body = add_shape(space, 15, 1, is_circle=True)
        pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
        space.add(pivot)
        pivot.max_bias = 0  
        pivot.max_force = 1000  

        gear = pymunk.GearJoint(static_body, body, 0.0, 1.0)
        space.add(gear)
        gear.max_bias = 0  
        gear.max_force = 5000  

    for _ in range(25):
        body = add_shape(space, 20, 1, is_circle=False)
        pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
        space.add(pivot)
        pivot.max_bias = 0  
        pivot.max_force = 1000  

        gear = pymunk.GearJoint(static_body, body, 0.0, 1.0)
        space.add(gear)
        gear.max_bias = 0  
        gear.max_force = 5000  

    
    global tank_control_body
    tank_control_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    tank_control_body.position = 320, 240
    space.add(tank_control_body)

    global tank_body
    tank_body = pymunk.Body(10, pymunk.moment_for_box(10, (30, 30)))
    tank_body.position = 320, 240
    space.add(tank_body)
    shape = pymunk.Poly.create_box(tank_body, (30, 30))
    shape.color = (0, 255, 100, 255)
    space.add(shape)

    
    pivot = pymunk.PivotJoint(tank_control_body, tank_body, (0, 0), (0, 0))
    space.add(pivot)
    pivot.max_bias = 0
    pivot.max_force = 10000

    gear = pymunk.GearJoint(tank_control_body, tank_body, 0.0, 1.0)
    space.add(gear)
    gear.error_bias = 0
    gear.max_bias = 1.2
    gear.max_force = 50000

    return space



space = init()
pygame.init()
screen = pygame.display.set_mode((640, 480))
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
    space.debug_draw(draw_options)
    fps = 60
    update(space, 1 / fps, screen)
    pygame.display.flip()
    clock.tick(fps)


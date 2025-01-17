"""
Openai/gym environment of basic demo of 2D robot manipulation environment,
as part of my Master's thesis.

Hunter Ellis 2024
"""

import gym
from gym import spaces
import numpy as np
import random
import pygame
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d


class SortEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self):
        super().__init__()
        pygame.init()

        self.width = 502
        self.height = 502
        self.fps = 60

        self.observation_space = spaces.Box(
            low=np.array([0, 0, -np.pi]),
            high=np.array([self.width, self.height, np.pi]),
            dtype=np.float32,
        )

        self.action_space = spaces.Discrete(4)

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        self.space = self._init_physics()
        self.agent_body = None
        self.agent_ctrl = None
        self.movement = {"forward": False,
                         "backward": False,
                         "rotate_left": False,
                         "rotate_right": False}
        self.reset()

    def _init_physics(self):
        """init physics for"""
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

        return space

    def _add_agent(self):

        self.agent_ctrl = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.agent_ctrl.position = self.width / 2, self.height / 2
        self.space.add(self.agent_ctrl)

        self.agent_body = pymunk.Body(10, pymunk.moment_for_box(10, (30, 30)))
        self.agent_body.position = self.width / 2, self.height / 2
        self.space.add(self.agent_body)

        agent_body_rectangles = [
            (0, 5, 35, 5),
            (-15, 0, 5, 10),
            (15, 0, 5, 10)
        ]

        for offset_x, offset_y, width, height in agent_body_rectangles:
            box_points = [(-width / 2, -height / 2), (width / 2, -height / 2),
                          (width / 2, height / 2), (-width / 2, height / 2)]
            box_points = [(x + offset_x, y + offset_y) for x, y in box_points]
            shape = pymunk.Poly(self.agent_body, box_points)
            shape.color = (255, 255, 255, 0)
            self.space.add(shape)

        pivot = pymunk.PivotJoint(self.agent_ctrl,
                                  self.agent_body, (0, 0), (0, 0))
        self.space.add(pivot)
        pivot.max_bias = 0
        pivot.max_force = 10000

        gear = pymunk.GearJoint(self.agent_ctrl,
                                self.agent_body, 0.0, 1.0)
        self.space.add(gear)
        gear.error_bias = 0
        gear.max_bias = 1.2
        gear.max_force = 50000

    def _add_shape(self, space, size, mass, is_circle=False):
        body = pymunk.Body()
        body.position = Vec2d(
            random.uniform(size, 640 - size),
            random.uniform(size, 480 - size),
        )
        body.angle = random.uniform(-3.150, 3.150)
        self.space.add(body)

        if is_circle:
            shape = pymunk.Circle(body, size)
        else:
            shape = pymunk.Poly.create_box(body, (size, size))

        shape.mass = mass
        shape.friction = 0.7
        shape.elasticity = 0
        shape.color = (random.randint(50, 255),
                       random.randint(50, 255),
                       random.randint(50, 255),
                       255)
        self.space.add(shape)

        return body

    def _add_objs(self):
        for _ in range(10):
            body = self._add_shape(self.space, 15, 1, is_circle=True)
            pivot = pymunk.PivotJoint(self.space.static_body,
                                      body,
                                      (0, 0),
                                      (0, 0))
            self.space.add(pivot)
            pivot.max_bias = 0
            pivot.max_force = 1000

            gear = pymunk.GearJoint(self.space.static_body, body, 0.0, 1.0)
            self.space.add(gear)
            gear.max_bias = 0
            gear.max_force = 5000

        for _ in range(10):
            body = self._add_shape(self.space, 20, 1, is_circle=False)
            pivot = pymunk.PivotJoint(self.space.static_body,
                                      body,
                                      (0, 0),
                                      (0, 0))
            self.space.add(pivot)
            pivot.max_bias = 0
            pivot.max_force = 1000

            gear = pymunk.GearJoint(self.space.static_body, body, 0.0, 1.0)
            self.space.add(gear)
            gear.max_bias = 0
            gear.max_force = 5000

    def reset(self):
        self.space = self._init_physics()
        self._add_agent()
        self._add_objs()
        return self._get_obs()

    def _get_obs(self):
        return np.array([
            self.agent_body.position.x,
            self.agent_body.position.y,
            self.agent_body.angle,
        ], dtype=np.float32)

    def step(self, action):

        self.movement = {
            "forward": action == 0,
            "backward": action == 1,
            "rotate_left": action == 2,
            "rotate_right": action == 3,
        }

        self.agent_ctrl.velocity = Vec2d(0, 0)
        self.agent_ctrl.angular_velocity = 0

        if self.movement["forward"]:
            direction = self.agent_body.rotation_vector * 100
            self.agent_ctrl.velocity = direction
        if self.movement["backward"]:
            direction = self.agent_body.rotation_vector * -100
            self.agent_ctrl.velocity = direction
        if self.movement["rotate_left"]:
            self.agent_ctrl.angular_velocity = -3
        if self.movement["rotate_right"]:
            self.agent_ctrl.angular_velocity = 3

        self.space.step(1 / self.fps)

        obs = self._get_obs()
        reward = 0
        done = False
        return obs, reward, done, {}

    def _custom_draw(self, space, screen):
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

    def render(self, mode="human"):
        self.screen.fill(pygame.Color("black"))
        self._custom_draw(self.space, self.screen)
        pygame.display.flip()
        self.clock.tick(self.fps)

    def close(self):
        pygame.quit()

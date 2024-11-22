import gym
from gym import spaces
import numpy as np
import random
import pygame
import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d


class TankEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self):
        super().__init__()
        pygame.init()

        
        self.width = 640
        self.height = 480
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
        self.tank_body = None
        self.tank_control_body = None
        self.movement = {"forward": False, "backward": False, "rotate_left": False, "rotate_right": False}
        self.reset()

    def _init_physics(self):
        """Initialize the physics space and objects."""
        space = pymunk.Space()
        space.iterations = 10
        space.sleep_time_threshold = 0.5

        static_body = space.static_body

        
        boundaries = [
            ((1, 1), (1, self.height)),
            ((self.width, 1), (self.width, self.height)),
            ((1, 1), (self.width, 1)),
            ((1, self.height), (self.width, self.height)),
        ]
        for start, end in boundaries:
            shape = pymunk.Segment(static_body, start, end, 1.0)
            shape.elasticity = 1
            shape.friction = 1
            space.add(shape)

        return space

    def _add_tank(self):
        """Add the tank to the physics space."""
        
        self.tank_control_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.tank_control_body.position = self.width / 2, self.height / 2
        self.space.add(self.tank_control_body)

        
        self.tank_body = pymunk.Body(10, pymunk.moment_for_box(10, (30, 30)))
        self.tank_body.position = self.width / 2, self.height / 2
        self.space.add(self.tank_body)
        shape = pymunk.Poly.create_box(self.tank_body, (30, 30))
        shape.color = (0, 255, 100, 255)
        self.space.add(shape)

        
        pivot = pymunk.PivotJoint(self.tank_control_body, self.tank_body, (0, 0), (0, 0))
        self.space.add(pivot)
        pivot.max_bias = 0
        pivot.max_force = 10000

        gear = pymunk.GearJoint(self.tank_control_body, self.tank_body, 0.0, 1.0)
        self.space.add(gear)
        gear.error_bias = 0
        gear.max_bias = 1.2
        gear.max_force = 50000

    
    def _add_shape(self, space, size, mass, is_circle=False):
        """Add a colored shape (circle or square) to the space."""
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
        shape.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255), 255)
        self.space.add(shape)

        return body
    
    def _add_objs(self):
        for _ in range(25):
            body = self._add_shape(self.space, 15, 1, is_circle=True)
            pivot = pymunk.PivotJoint(self.space.static_body, body, (0, 0), (0, 0))
            self.space.add(pivot)
            pivot.max_bias = 0  
            pivot.max_force = 1000  

            gear = pymunk.GearJoint(self.space.static_body, body, 0.0, 1.0)
            self.space.add(gear)
            gear.max_bias = 0  
            gear.max_force = 5000  

        for _ in range(25):
            body = self._add_shape(self.space, 20, 1, is_circle=False)
            pivot = pymunk.PivotJoint(self.space.static_body, body, (0, 0), (0, 0))
            self.space.add(pivot)
            pivot.max_bias = 0  
            pivot.max_force = 1000  

            gear = pymunk.GearJoint(self.space.static_body, body, 0.0, 1.0)
            self.space.add(gear)
            gear.max_bias = 0  
            gear.max_force = 5000  


    def reset(self):
        """Reset the environment to the initial state."""
        self.space = self._init_physics()
        self._add_tank()
        self._add_objs()
        return self._get_obs()

    def _get_obs(self):
        """Get the current observation (tank position and angle)."""
        return np.array([
            self.tank_body.position.x,
            self.tank_body.position.y,
            self.tank_body.angle,
        ], dtype=np.float32)

    def step(self, action):
        """Apply an action and update the environment."""
        
        self.movement = {
            "forward": action == 0,
            "backward": action == 1,
            "rotate_left": action == 2,
            "rotate_right": action == 3,
        }

        
        self.tank_control_body.velocity = Vec2d(0, 0)
        self.tank_control_body.angular_velocity = 0

        if self.movement["forward"]:
            direction = self.tank_body.rotation_vector * 100
            self.tank_control_body.velocity = direction
        if self.movement["backward"]:
            direction = self.tank_body.rotation_vector * -100
            self.tank_control_body.velocity = direction
        if self.movement["rotate_left"]:
            self.tank_control_body.angular_velocity = -3
        if self.movement["rotate_right"]:
            self.tank_control_body.angular_velocity = 3

        
        self.space.step(1 / self.fps)

        
        obs = self._get_obs()
        reward = 0  
        done = False  
        return obs, reward, done, {}

    def render(self, mode="human"):
        """Render the environment."""
        self.screen.fill(pygame.Color("black"))
        self.space.debug_draw(self.draw_options)
        pygame.display.flip()
        self.clock.tick(self.fps)

    def close(self):
        """Clean up resources."""
        pygame.quit()


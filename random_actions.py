from  env import TankEnv

env = TankEnv()

obs = env.reset()
done = False

while not done:
    action = env.action_space.sample()  # agents action
    obs, reward, done, info = env.step(action)
    env.render()

env.close()


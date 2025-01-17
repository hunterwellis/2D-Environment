import sys
import getopt

sys.path.append("../../env/")
from env import SortEnv

if __name__ == "__main__":

    argumentList = sys.argv[1:]
    options = "hmo:"

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options)

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h"):
                print("Displaying Help")

            elif currentArgument in ("-m"):
                print("Displaying file_name:", sys.argv[0])

            elif currentArgument in ("-o"):
                print(("Enabling special output mode (% s)") % (currentValue))

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))

    env = SortEnv()

    obs = env.reset()
    done = False

    while not done:
        action = env.action_space.sample()  # agents action
        obs, reward, done, info = env.step(action)
        env.render()

    env.close()

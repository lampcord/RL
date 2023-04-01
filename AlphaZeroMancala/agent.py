import numpy as np
import TicTacToeEnv
from MCTS import mcts


class Agent:
    def __init__(self, env):
        self.env = env

    def move_random(self):
        action_values = np.random.rand((9))
        valid_actions = self.env.valid_actions()
        action_values[valid_actions == 0] = 0
        action = np.argmax(action_values)
        obs, rew, done, inf = self.env.step(action)

        return obs, rew, done, inf

    def move_mcts(self):
        test_env = self.env.clone()
        action = mcts(test_env)
        obs, rew, done, inf = self.env.step(action)

        return obs, rew, done, inf

    def reset(self):
        self.env.reset()
        self.env.observation_space = np.array([1,2,2,0,1,0,0,0,0])
        self.env.turn = 1


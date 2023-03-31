import time

import gym
import pygame
import torch
import TicTacToeEnv
import numpy as np

def check_for_cuda():
    if torch.cuda.is_available():
        print("CUDA is available! PyTorch can use your GPU.")
        device = torch.device("cuda")
    else:
        print("CUDA is not available. PyTorch will use the CPU instead.")
        device = torch.device("cpu")

    print("PyTorch will use the following device for computation:", device)
    return device

env = TicTacToeEnv.TicTacToeEnv()
env.reset()
env.render()

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    action_values = np.random.rand((9))
    valid_actions = env.valid_actions()
    action_values[valid_actions == 0] = 0
    print(action_values)
    action = np.argmax(action_values)
    print(action)
    obs, rew, done, _ = env.step(action)

    env.render()
    time.sleep(1)

env.close()

# env = gym.make('YourBoardGameEnvironment')
# done = False
#
# while not done:
#     env.render()
#     action = mcts(env)
#     _, _, done, _ = env.step(action)

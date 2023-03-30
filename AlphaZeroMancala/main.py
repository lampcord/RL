import time

import gym
import pygame
import torch
import TicTacToeEnv

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
env.render()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    env.render()

env.close()

# env = gym.make('YourBoardGameEnvironment')
# done = False
#
# while not done:
#     env.render()
#     action = mcts(env)
#     _, _, done, _ = env.step(action)

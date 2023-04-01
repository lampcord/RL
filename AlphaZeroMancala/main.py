import time

import gym
import pygame
import torch
import TicTacToeEnv
import numpy as np
import agent

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

env.run_win_test()
exit()
TicTacToeAgent = agent.Agent (env)

for x in range (10):
    done = False
    TicTacToeAgent.reset()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # obs, rew, done, inf = TicTacToeAgent.move_random()
        obs, rew, done, inf = TicTacToeAgent.move_mcts()

        env.render_node()
        # env.dump()
        time.sleep(.5)

        if done:
            print(f"Reward: {rew}")
            time.sleep(3)


env.close()

# env = gym.make('YourBoardGameEnvironment')
# done = False
#
# while not done:
#     env.render()
#     action = mcts(env)
#     _, _, done, _ = env.step(action)

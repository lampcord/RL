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
# env.render()

# env.run_win_test()
# exit()
TicTacToeAgent = agent.Agent (env)

for x in range (10):
    done = False
    TicTacToeAgent.reset()
    mcts_turn = x % 2 + 1
    print(f"MCTS is player {mcts_turn}")
    turn_was_mcts = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        if mcts_turn == TicTacToeAgent.env.turn:
            turn_was_mcts = True
            obs, rew, done, inf = TicTacToeAgent.move_mcts()
        else:
            turn_was_mcts = False
            obs, rew, done, inf = TicTacToeAgent.move_random()

        env.render()
        # env.dump()
        time.sleep(.5)

        if done:
            print(f"Reward: {rew} MCTS won: {turn_was_mcts}")
            time.sleep(3)


env.close()

# env = gym.make('YourBoardGameEnvironment')
# done = False
#
# while not done:
#     env.render()
#     action = mcts(env)
#     _, _, done, _ = env.step(action)

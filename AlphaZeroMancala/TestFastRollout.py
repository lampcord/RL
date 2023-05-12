import ctypes
import os
import time
from Connect4 import c4_game
from game import GameTurn, GameResult
import random

# Load the DLL
dll_path = os.path.join("FastRollout.dll")
my_functions = ctypes.CDLL(dll_path)

# Declare the argument types and return types of the C++ functions
my_functions.C4_rollout.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64]
my_functions.C4_rollout.restype = ctypes.c_float

my_functions.C4_render.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
my_functions.C4_render.restype = None

game = c4_game.C4Game()
turn = GameTurn.PLAYER1

rollouts = 200000
positions = [game.get_initial_position(), game.get_initial_position(), game.get_initial_position(), game.get_initial_position(), game.get_initial_position()]
for position in positions:
    print('-' * 80)
    start = time.time_ns()
    result = my_functions.C4_rollout(position, GameTurn.PLAYER1.value, rollouts)
    elapsed = time.time_ns() - start
    print(f"Result {result / rollouts} Elapsed {elapsed / 1000000000.0}")

    start = time.time_ns()
    score = 0.0
    for _ in range(100):
        binary_state = position
        result = GameResult.NOT_COMPLETED
        turn = GameTurn.PLAYER1
        while result == GameResult.NOT_COMPLETED:
            moves = game.get_legal_moves(binary_state, turn)
            move = random.choice(moves)
            binary_state, result, switch_turns, info = game.move(binary_state, move, turn)
            if switch_turns:
                binary_state, turn = game.switch_players(binary_state, turn)
            if result == GameResult.PLAYER1:
                score += 1.0
            elif result == GameResult.DRAW:
                score += 0.5
    elapsed = time.time_ns() - start
    print(f"Result {score / 100} Elapsed {elapsed / 1000000000.0}")

    # bits = game.int_to_bits(position, bits=c4_game.GAME_COLS * c4_game.GAME_ROWS + c4_game.GAME_COLS * c4_game.BITS_IN_LEN)
    # for bit in bits:
    #     print(str(bit) + " ", end="")
    # print()

# c4_game.play_random_game(show=True)

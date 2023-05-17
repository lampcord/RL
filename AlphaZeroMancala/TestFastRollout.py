import ctypes
import os
import time
from connect_4.c4_game_rules import C4GameRules
from connect_4.c4_console_renderer import C4ConsoleRenderer
from game_rules import GameResult
import random

# Load the DLL
dll_path = os.path.join("./connect_4/FastRollout.dll")
my_functions = ctypes.CDLL(dll_path)

# Declare the argument types and return types of the C++ functions
my_functions.C4_rollout.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64]
my_functions.C4_rollout.restype = ctypes.c_float

my_functions.C4_render.argtypes = [ctypes.c_uint64]
my_functions.C4_render.restype = None

game_rules = C4GameRules()
renderer = C4ConsoleRenderer()
turn = 0
# result = GameResult.CONTINUE
# state = game_rules.get_initial_position()
# info = {}
# while result == GameResult.CONTINUE:
#     print('=' * 60)
#     renderer.render(state, turn, info)
#     my_functions.C4_render(state)
#     legal_moves = game_rules.get_legal_moves(state, turn)
#     move = random.choice(legal_moves)
#     state, turn, result, info = game_rules.move(state, move, turn)
#
# print('=' * 60)
# renderer.render(state, turn, info)
# my_functions.C4_render(state)
# renderer.render(17592187841462, 0)
# my_functions.C4_rollout(17592187841462, 0, 1)
rollouts = 1200
# state, turn, result, info = game_rules.move(17592187841462, 3, turn)
# renderer.render(state, 0)
#
positions = [game_rules.get_initial_position()] * 100
for position in positions:
    print('-' * 80)
    start = time.time_ns()
    result = my_functions.C4_rollout(position, 0, rollouts)
    elapsed = time.time_ns() - start
    print(f"Result {result} Elapsed {elapsed / 1000000000.0}")

    # start = time.time_ns()
    # score = 0.0
    # for _ in range(100):
    #     binary_state = position
    #     result = GameResult.CONTINUE
    #     turn = 0
    #     while result == GameResult.CONTINUE:
    #         moves = game_rules.get_legal_moves(binary_state, turn)
    #         move = random.choice(moves)
    #         binary_state, turn, result, info = game_rules.move(binary_state, move, turn)
    #         if result == GameResult.WIN and turn == 1:
    #             score += 1.0
    #         elif result == GameResult.TIE:
    #             score += 0.5
    # elapsed = time.time_ns() - start
    # print(f"Result {score / 100} Elapsed {elapsed / 1000000000.0}")
#
#     bits = game.int_to_bits(position, bits=c4_game.GAME_COLS * c4_game.GAME_ROWS + c4_game.GAME_COLS * c4_game.BITS_IN_LEN)
#     for bit in bits:
#         print(str(bit) + " ", end="")
#     print()
#
# c4_game.play_random_game(show=True)

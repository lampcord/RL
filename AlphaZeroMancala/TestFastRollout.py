import ctypes
import os
import time
from Connect4 import c4_game
from game import GameTurn

# Load the DLL
dll_path = os.path.join("FastRollout.dll")
my_functions = ctypes.CDLL(dll_path)

# Declare the argument types and return types of the C++ functions
my_functions.C4_rollout.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64]
my_functions.C4_rollout.restype = ctypes.c_float

my_functions.C4_render.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
my_functions.C4_rollout.restype = None

game = c4_game.C4Game()
turn = GameTurn.PLAYER1

positions = [game.get_initial_position(), 1283531189544341544]
for position in positions:
    print('-' * 80)
    # my_functions.C4_rollout(position, GameTurn.PLAYER1.value, 0)
    my_functions.C4_render(position, GameTurn.PLAYER1.value)
    game.render(position, GameTurn.PLAYER1)
    # my_functions.C4_rollout(position, GameTurn.PLAYER2.value, 0)
    my_functions.C4_render(position, GameTurn.PLAYER2.value)
    game.render(position, GameTurn.PLAYER2)
    # bits = game.int_to_bits(position, bits=c4_game.GAME_COLS * c4_game.GAME_ROWS + c4_game.GAME_COLS * c4_game.BITS_IN_LEN)
    # for bit in bits:
    #     print(str(bit) + " ", end="")
    # print()

# c4_game.play_random_game(show=True)

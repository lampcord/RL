import ctypes
import os
import stackprinter

from agents.random_agent import RandomAgent
from agents.user_agent import UserAgent
from agents.mcts_agent import MCTSAgent, MCTSAgentConfig

from tic_tac_toe.ttt_game_rules import TicTacToeGameRules
from tic_tac_toe.ttt_console_renderer import TicTacToeConsoleRenderer
from tic_tac_toe.ttt_gui_renderer import TicTacToeGUIRenderer

from connect_4.c4_game_rules import C4GameRules
from connect_4.c4_console_renderer import C4ConsoleRenderer
from connect_4.c4_gui_renderer import C4GuiRenderer

from tournament_director import TournamentDirector
stackprinter.set_excepthook(style='darkbg2')

game_rules = C4GameRules()
console_renderer = C4ConsoleRenderer()
gui_renderer = C4GuiRenderer()

# Load the DLL
dll_path = os.path.join("./connect_4/FastRollout.dll")
my_functions = ctypes.CDLL(dll_path)

# Declare the argument types and return types of the C++ functions
my_functions.C4_rollout.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64]
my_functions.C4_rollout.restype = ctypes.c_float
rollout_policy = my_functions.C4_rollout

# game_rules = TicTacToeGameRules()
# console_renderer = TicTacToeConsoleRenderer()
# gui_renderer = TicTacToeGUIRenderer()

mcts_config_default = MCTSAgentConfig()

mcts_config_rollout_1000 = MCTSAgentConfig()
mcts_config_rollout_1000.rollout_policy = rollout_policy
mcts_config_rollout_1000.rollout_count = 1000

mcts_config_rollout_1000_1sec = MCTSAgentConfig()
mcts_config_rollout_1000_1sec.loops = 1000000
mcts_config_rollout_1000_1sec.rollout_policy = rollout_policy
mcts_config_rollout_1000_1sec.rollout_count = 1000
mcts_config_rollout_1000_1sec.max_time = 1.0

mcts_config_rollout_1_1sec = MCTSAgentConfig()
mcts_config_rollout_1_1sec.loops = 1000000
mcts_config_rollout_1_1sec.rollout_policy = rollout_policy
mcts_config_rollout_1_1sec.rollout_count = 1
mcts_config_rollout_1_1sec.max_time = 1.0

mcts_config_rollout_vs_A0 = MCTSAgentConfig()
mcts_config_rollout_vs_A0.loops = 10000
mcts_config_rollout_vs_A0.rollout_policy = rollout_policy
mcts_config_rollout_vs_A0.rollout_count = 1000
mcts_config_rollout_vs_A0.max_time = 3.2

play_against_random_console = [game_rules, [UserAgent(game_rules, console_renderer), RandomAgent(game_rules)], 2, console_renderer]
play_against_MTCS_console = [game_rules, [UserAgent(game_rules, console_renderer), MCTSAgent(game_rules, mcts_config_rollout_1000)], 2, console_renderer]
play_against_random_gui = [game_rules, [UserAgent(game_rules, gui_renderer), RandomAgent(game_rules)], 10, gui_renderer]
play_against_MCTS_gui = [game_rules, [UserAgent(game_rules, gui_renderer), MCTSAgent(game_rules, mcts_config_rollout_vs_A0)], 10, gui_renderer]
play_random = [game_rules, [RandomAgent(game_rules), RandomAgent(game_rules)], 10000, None]
play_random_mcts = [game_rules, [RandomAgent(game_rules), MCTSAgent(game_rules, mcts_config_default)], 1000, None]
play_mcts_mcts = [game_rules, [MCTSAgent(game_rules, mcts_config_rollout_1000_1sec), MCTSAgent(game_rules, mcts_config_rollout_1_1sec)], 1000, None]
play_console_console = [game_rules, [UserAgent(game_rules, console_renderer), UserAgent(game_rules, console_renderer)], 10, console_renderer]

director = TournamentDirector(*play_mcts_mcts)
tournament_set = director.run()
director.print_tournament_set(tournament_set, detail=False)




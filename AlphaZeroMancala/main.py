from game_rules import GameResult
from agents.console_agent import ConsoleAgent

from tic_tac_toe.ttt_game_rules import TicTacToeGameRules
from tic_tac_toe.ttt_console_renderer import TicTacToeConsoleRenderer

game_rules = TicTacToeGameRules(2)
renderer = TicTacToeConsoleRenderer()
agent = ConsoleAgent(game_rules, renderer)

state = game_rules.get_initial_position()
turn = 0
result = GameResult.CONTINUE
info = {}
while result == GameResult.CONTINUE:
    state, turn, result, info = agent.move(state, turn)



from game_rules import GameResult

from agents.console_agent import ConsoleAgent
from agents.random_agent import RandomAgent

from tic_tac_toe.ttt_game_rules import TicTacToeGameRules
from tic_tac_toe.ttt_console_renderer import TicTacToeConsoleRenderer

from tournament_director import TournamentDirector

game_rules = TicTacToeGameRules(2)
renderer = TicTacToeConsoleRenderer()
agent_list = [RandomAgent(game_rules), RandomAgent(game_rules)]

director = TournamentDirector(game_rules, agent_list, 1000, None)
director.run()




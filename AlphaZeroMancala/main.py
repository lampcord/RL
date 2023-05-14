import stackprinter

from agents.console_agent import ConsoleAgent
from agents.random_agent import RandomAgent
from agents.gui_agent import GuiAgent

from tic_tac_toe.ttt_game_rules import TicTacToeGameRules
from tic_tac_toe.ttt_console_renderer import TicTacToeConsoleRenderer
from tic_tac_toe.ttt_gui_renderer import TicTacToeGUIRenderer

from tournament_director import TournamentDirector
stackprinter.set_excepthook(style='darkbg2')

game_rules = TicTacToeGameRules()
gui_renderer = TicTacToeGUIRenderer()

play_against_random_console = [
    game_rules,
    [ConsoleAgent(game_rules), RandomAgent(game_rules)],
    2,
    TicTacToeConsoleRenderer()]

play_against_random_gui = [
    game_rules,
    [GuiAgent(game_rules, gui_renderer), RandomAgent(game_rules)],
    10,
    gui_renderer]

play_1000_random = [
    game_rules,
    [RandomAgent(game_rules), RandomAgent(game_rules)],
    1000,
    None]

director = TournamentDirector(*play_1000_random)
tournament_set = director.run()
director.print_tournament_set(tournament_set, detail=True)




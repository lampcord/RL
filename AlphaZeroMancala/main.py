import stackprinter

from agents.random_agent import RandomAgent
from agents.user_agent import UserAgent
from agents.mcts_agent import MCTSAgent

from tic_tac_toe.ttt_game_rules import TicTacToeGameRules
from tic_tac_toe.ttt_console_renderer import TicTacToeConsoleRenderer
from tic_tac_toe.ttt_gui_renderer import TicTacToeGUIRenderer

from connect_4.c4_game_rules import C4GameRules
from connect_4.c4_console_renderer import C4ConsoleRenderer
from connect_4.c4_gui_renderer import C4GuiRenderer

from tournament_director import TournamentDirector
stackprinter.set_excepthook(style='darkbg2')

# game_rules = C4GameRules()
# console_renderer = C4ConsoleRenderer()
# gui_renderer = C4GuiRenderer()

game_rules = TicTacToeGameRules()
console_renderer = TicTacToeConsoleRenderer()
gui_renderer = TicTacToeGUIRenderer()

play_against_random_console = [game_rules, [UserAgent(game_rules, console_renderer), RandomAgent(game_rules)], 2, console_renderer]
play_against_MTCS_console = [game_rules, [UserAgent(game_rules, console_renderer), MCTSAgent(game_rules)], 2, console_renderer]
play_against_random_gui = [game_rules, [UserAgent(game_rules, gui_renderer), RandomAgent(game_rules)], 10, gui_renderer]
play_against_MCTS_gui = [game_rules, [UserAgent(game_rules, gui_renderer), MCTSAgent(game_rules, most_visits=True)], 10, gui_renderer]
play_random = [game_rules, [RandomAgent(game_rules), RandomAgent(game_rules)], 10000, None]
play_random_mcts = [game_rules, [RandomAgent(game_rules), MCTSAgent(game_rules, most_visits=True)], 100, None]
play_mcts_mcts = [game_rules, [MCTSAgent(game_rules, most_visits=True), MCTSAgent(game_rules, most_visits=True)], 100, None]
play_console_console = [game_rules, [UserAgent(game_rules, console_renderer), UserAgent(game_rules, console_renderer)], 10, console_renderer]

director = TournamentDirector(*play_against_random_gui)
tournament_set = director.run()
director.print_tournament_set(tournament_set, detail=False)




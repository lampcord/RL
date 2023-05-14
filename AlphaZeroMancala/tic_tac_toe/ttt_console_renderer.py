from tic_tac_toe.ttt_game_rules import TicTacToeGameRules
from renderer import Renderer
player_char = {
    0: 'X',
    1: 'O'
}
display_char = {
    0: '.',
    1: 'X',
    2: 'O'
}


class TicTacToeConsoleRenderer(Renderer):
    def __init__(self):
        super().__init__()
        self.game_rules = TicTacToeGameRules(2)

    def render(self, state, turn, info):
        moves = self.game_rules.get_legal_moves(state, turn)
        winning_set = info.get('winning_set', [])
        list_state = self.game_rules.get_decoded_list(state, turn)
        for ndx, cell in enumerate(list_state):
            if ndx % 3 == 0:
                print('')
                print('+---+---+---+')
                print('|', end='')
            if ndx in winning_set:
                label = f'({display_char[list_state[ndx]]})'
            else:
                label = f' {display_char[list_state[ndx]]} '
            print(label + '|', end='')
        print('')
        print('+---+---+---+')
        print(f"Moves: {moves} for Player {player_char[turn]}")

if __name__ == "__main__":
    print("ttt_console_renderer")

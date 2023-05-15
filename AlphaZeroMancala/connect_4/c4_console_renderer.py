from connect_4.c4_game_rules import C4GameRules, GAME_ROWS, GAME_COLS
from renderer import Renderer


class C4ConsoleRenderer(Renderer):
    def __init__(self):
        super().__init__()
        self.game_rules = C4GameRules()

    def render(self, state, turn, info=None):
        win_set = self.game_rules.check_for_win(state, turn)
        list_state = self.game_rules.get_decoded_list(state)
        data = [['   '] * GAME_COLS for _ in range(GAME_ROWS)]
        for col_idx, col in enumerate(list_state):
            for rev_row_idx, cell in enumerate(col):
                row_idx = GAME_ROWS - rev_row_idx - 1
                if win_set and (col_idx, row_idx) in win_set:
                    data[row_idx][col_idx] = f"({str(cell)})"
                else:
                    data[row_idx][col_idx] = f" {str(cell)} "
        display_state = ['|'.join(row) for row in data]
        for line in display_state:
            print('+---+---+---+---+---+---+---+')
            print('|' + line + '|')
        print('+---+---+---+---+---+---+---+')
        print('  0   1   2   3   4   5   6')
        print(state, turn)

    def get_move(self, legal_moves):
        print(f"Legal Moves: {legal_moves}")
        move = int(input(f"Choose move: "))
        return move


if __name__ == "__main__":
    pass
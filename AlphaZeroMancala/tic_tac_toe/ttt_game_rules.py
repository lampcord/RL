import time

import game_rules
import random
import tic_tac_toe.ttt_gui_renderer
import stackprinter
stackprinter.set_excepthook(style='darkbg2')
"""
TicTacToe
Position is represented as a list of 9 cells. Each cell is either:
0 - Empty
1 - Player1
2 - Player2
"""
winning_patterns = {
    0: [[1, 2], [3, 6], [4, 8]],
    1: [[0, 2], [4, 7]],
    2: [[0, 1], [4, 6], [5, 8]],
    3: [[0, 6], [4, 5]],
    4: [[0, 8], [1, 7], [2, 6], [3, 5]],
    5: [[2, 8], [3, 4]],
    6: [[0, 3], [2, 4], [7, 8]],
    7: [[1, 4], [6, 8]],
    8: [[0, 4], [2, 5], [6, 7]]
    }

symbol_for_player = {
    0: 1,
    1: 2
}


class TicTacToeGameRules(game_rules.GameRules):
    def __init__(self, number_of_players=2):
        super().__init__(number_of_players)

    def get_initial_position(self):
        return self.get_encoded_binary([0] * 9, 0)

    def get_player_bounds(self):
        return 2, 2

    def move(self, state, move, turn):
        legal_moves = self.get_legal_moves(state, turn)

        assert move in legal_moves

        list_state = self.get_decoded_list(state, turn)
        assert list_state[move] == 0

        assert turn in [0, 1]

        list_state[move] = symbol_for_player[turn]

        new_state = self.get_encoded_binary(list_state, turn)
        new_turn = 1 - turn
        result = game_rules.GameResult.CONTINUE
        info = {}

        for check_set in winning_patterns[move]:
            winning_set = [move]
            for check_cell in check_set:
                if list_state[check_cell] != symbol_for_player[turn]:
                    break
                winning_set.append(check_cell)
            if len(winning_set) == 3:
                info['winning_set'] = winning_set
                result = game_rules.GameResult.WIN
                break

        if result == game_rules.GameResult.CONTINUE and len(legal_moves) == 1:
            result = game_rules.GameResult.TIE

        return new_state, new_turn, result, info

    def get_legal_moves(self, state, turn):
        list_state = self.get_decoded_list(state, turn)
        legal_moves = []
        for ndx, cell in enumerate(list_state):
            if cell == 0:
                legal_moves.append(ndx)
        return legal_moves

    def get_encoded_binary(self, list_state, turn):
        encoded_state = 0
        player_1_symbol = symbol_for_player[0]
        player_2_symbol = symbol_for_player[1]
        for symbol in (player_1_symbol, player_2_symbol):
            for cell in list_state:
                encoded_state *= 2
                if cell == symbol:
                    encoded_state += 1
        return encoded_state

    def get_decoded_list(self, state, turn):
        list_state = []
        player_1_symbol = symbol_for_player[0]
        player_2_symbol = symbol_for_player[1]
        for _ in range(9):
            if state % 2 == 1:
                list_state.append(player_2_symbol)
            else:
                list_state.append(0)
            state //= 2
        for ndx in range(9):
            if state % 2 == 1:
                list_state[ndx] = player_1_symbol
            state //= 2
        return list_state[::-1]



def play_random_games(num_games=1):
    for _ in range(num_games):
        ttt = TicTacToeGameRules()
        board = tic_tac_toe.ttt_board.TicTacToeBoard()
        state = ttt.get_initial_position()
        turn = game.GameTurn.PLAYER1
        while True:
            legal_moves = ttt.get_legal_moves(state, turn)
            if len(legal_moves) == 0:
                break
            move = random.choice(legal_moves)
            state, result, switch_players, info = ttt.move(state, move, turn)

            if switch_players:
                state, turn = ttt.switch_players(state, turn)
            ttt.render(state, info.get('winning_set', []))
            board.render(state, info.get('winning_set', []))
            time.sleep(1)

            if result != game.GameResult.NOT_COMPLETED:
                print(f'Result {result.name}')
                break


def test_1():
    print('test_1', end='')
    ttt = TicTacToeGameRules(2)
    turn = 0
    for _ in range(100):
        print('.', end='')
        list_state = []
        for _ in range(9):
            list_state.append(random.randint(0, 2))
        state = ttt.get_encoded_binary(list_state, turn)
        new_list_state = ttt.get_decoded_list(state, turn)
        new_state = ttt.get_encoded_binary(new_list_state, turn)
        turn = 1 - turn
        assert state == new_state
        assert list_state == new_list_state
    print('passed.')



if __name__ == "__main__":
    # ttt = TicTacToeGameRules(2)
    # state = ttt.get_initial_position()
    # print(ttt.get_legal_moves(state, 0))
    # test_1()
    play_random_games(10)

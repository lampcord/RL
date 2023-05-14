import time

import game_rules
import random
import tic_tac_toe.ttt_gui_renderer
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
    game.GameTurn.PLAYER1: 1,
    game.GameTurn.PLAYER2: 2
}

display_char = {
    0: '.',
    1: 'X',
    2: 'O'
}

class TicTacToeGame(game.Game):
    def __init__(self):
        super().__init__()

    def get_initial_position(self):
        return self.get_encoded_binary([0] * 9, game.GameTurn.PLAYER1)

    def move(self, binary_state, move, turn):
        legal_moves = self.get_legal_moves(binary_state, turn)

        assert move in legal_moves

        list_state = self.get_decoded_list(binary_state, turn)
        assert list_state[move] == 0

        assert turn in [game.GameTurn.PLAYER1, game.GameTurn.PLAYER2]

        list_state[move] = symbol_for_player[turn]

        new_binary_state = self.get_encoded_binary(list_state, turn)
        switch_turns = True
        result = game.GameResult.NOT_COMPLETED
        info = {}

        for check_set in winning_patterns[move]:
            winning_set = [move]
            for check_cell in check_set:
                if list_state[check_cell] != symbol_for_player[turn]:
                    break
                winning_set.append(check_cell)
            if len(winning_set) == 3:
                info['winning_set'] = winning_set
                result = game.game_result_for_turn[turn]
                break

        if result == game.GameResult.NOT_COMPLETED and len(legal_moves) == 1:
            result = game.GameResult.DRAW

        return new_binary_state, result, switch_turns, info

    def get_legal_moves(self, binary_state, turn):
        list_state = self.get_decoded_list(binary_state, turn)
        legal_moves = []
        for ndx, cell in enumerate(list_state):
            if cell == 0:
                legal_moves.append(ndx)
        return legal_moves

    def get_encoded_binary(self, list_state, turn):
        encoded_state = 0
        player_symbol = symbol_for_player[turn]
        opponent_symbol = symbol_for_player[self.get_oponents_turn(turn)]
        for symbol in (player_symbol, opponent_symbol):
            for cell in list_state:
                encoded_state *= 2
                if cell == symbol:
                    encoded_state += 1
        return encoded_state

    def get_decoded_list(self, binary_state, turn):
        list_state = []
        player_symbol = symbol_for_player[turn]
        opponent_symbol = symbol_for_player[self.get_oponents_turn(turn)]
        for _ in range(9):
            if binary_state % 2 == 1:
                list_state.append(opponent_symbol)
            else:
                list_state.append(0)
            binary_state //= 2
        for ndx in range(9):
            if binary_state % 2 == 1:
                list_state[ndx] = player_symbol
            binary_state //= 2
        return list_state[::-1]

    def render(self, binary_state, turn, winning_set=[]):
        list_state = self.get_decoded_list(binary_state, turn)
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


def play_random_games(num_games=1):
    for _ in range(num_games):
        ttt = TicTacToeGame()
        board = tic_tac_toe.ttt_board.TicTacToeBoard()
        binary_state = ttt.get_initial_position()
        turn = game.GameTurn.PLAYER1
        while True:
            legal_moves = ttt.get_legal_moves(binary_state, turn)
            if len(legal_moves) == 0:
                break
            move = random.choice(legal_moves)
            binary_state, result, switch_players, info = ttt.move(binary_state, move, turn)

            if switch_players:
                binary_state, turn = ttt.switch_players(binary_state, turn)
            ttt.render(binary_state, info.get('winning_set', []))
            board.render(binary_state, info.get('winning_set', []))
            time.sleep(1)

            if result != game.GameResult.NOT_COMPLETED:
                print(f'Result {result.name}')
                break


def test_1():
    print('test_1', end='')
    ttt = TicTacToeGame()
    turn = game.GameTurn.PLAYER1
    for _ in range(100):
        print('.', end='')
        list_state = []
        for _ in range(9):
            list_state.append(random.randint(0, 2))
        binary_state = ttt.get_encoded_binary(list_state, turn)
        new_list_state = ttt.get_decoded_list(binary_state, turn)
        new_binary_state = ttt.get_encoded_binary(new_list_state, turn)
        turn = ttt.get_oponents_turn(turn)
        assert binary_state == new_binary_state
        assert list_state == new_list_state
    print('passed.')


def test_2():
    ttt = TicTacToeGame()
    board = tic_tac_toe.ttt_board.TicTacToeBoard()
    turn = game.GameTurn.PLAYER1
    for move in range(9):
        for test_set in winning_patterns[move]:
            list_state = [0] * 9
            list_state[move] = 1
            winning_set = [move]
            for m in test_set:
                list_state[m] = 1
                winning_set.append(m)
            binary_state = ttt.get_encoded_binary(list_state, turn)
            ttt.render(binary_state, turn, winning_set)
            board.render(binary_state, turn, winning_set)
            time.sleep(.5)
            print('-' * 20)

def test_3():
    print('test_3', end='')
    ttt = TicTacToeGame()
    turn = game.GameTurn.PLAYER1
    opponents_turn = game.GameTurn.PLAYER2
    for _ in range(100):
        print('.', end='')
        list_state = []
        for _ in range(9):
            list_state.append(random.randint(0, 2))
        binary_state = ttt.get_encoded_binary(list_state, turn)
        rev_list_state = []
        for symbol in list_state:
            if symbol == 1:
                rev_list_state.append(2)
            elif symbol == 2:
                rev_list_state.append(1)
            else:
                rev_list_state.append(0)
        rev_binary_state = ttt.get_encoded_binary(rev_list_state, opponents_turn)

        assert binary_state == rev_binary_state
    print('passed.')


if __name__ == "__main__":
    test_1()
    test_2()
    test_3()
    # play_random_games(10)

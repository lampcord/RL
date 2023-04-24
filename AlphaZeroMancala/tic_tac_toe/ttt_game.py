import time

import game
import random
import tic_tac_toe.ttt_board
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
        return self.get_encoded_binary([0] * 9)

    def move(self, binary_state, move, turn):
        legal_moves = self.get_legal_moves(binary_state, turn)

        assert move in legal_moves

        list_state = self.get_decoded_list(binary_state)
        assert list_state[move] == 0

        assert turn in [game.GameTurn.PLAYER1, game.GameTurn.PLAYER2]

        list_state[move] = symbol_for_player[turn]

        new_binary_state = self.get_encoded_binary(list_state)
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
        list_state = self.get_decoded_list(binary_state)
        legal_moves = []
        for ndx, cell in enumerate(list_state):
            if cell == 0:
                legal_moves.append(ndx)
        return legal_moves

    def get_encoded_binary(self, list_state):
        encoded_state = 0
        for cell in list_state:
            encoded_state *= 4
            encoded_state += cell
        return encoded_state

    def get_decoded_list(self, binary_state):
        list_state = []
        for _ in range(9):
            list_state.append(int(binary_state) % 4)
            binary_state /= 4
        return list_state[::-1]

    def render(self, binary_state, winning_set=[]):
        list_state = self.get_decoded_list(binary_state)
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
                turn = ttt.switch_players(turn)
            ttt.render(binary_state, info.get('winning_set', []))
            board.render(binary_state, info.get('winning_set', []))
            time.sleep(1)

            if result != game.GameResult.NOT_COMPLETED:
                print(f'Result {result.name}')
                break


def test_1():
    print('test_1', end='')
    ttt = TicTacToeGame()
    for _ in range(100):
        print('.', end='')
        list_state = []
        for _ in range(9):
            list_state.append(random.randint(0, 2))
        binary_state = ttt.get_encoded_binary(list_state)
        new_list_state = ttt.get_decoded_list(binary_state)
        new_binary_state = ttt.get_encoded_binary(new_list_state)
        assert binary_state == new_binary_state
        assert list_state == new_list_state
    print('passed.')


def test_2():
    ttt = TicTacToeGame()
    board = tic_tac_toe.ttt_board.TicTacToeBoard()
    for move in range(9):
        for test_set in winning_patterns[move]:
            list_state = [0] * 9
            list_state[move] = 1
            winning_set = [move]
            for m in test_set:
                list_state[m] = 1
                winning_set.append(m)
            binary_state = ttt.get_encoded_binary(list_state)
            ttt.render(binary_state, winning_set)
            board.render(binary_state, winning_set)
            time.sleep(.5)
            print('-' * 20)

if __name__ == "__main__":
    # test_1()
    # test_2()
    play_random_games(10)

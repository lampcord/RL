import game
import random

"""
TicTacToe
Position is represented as a list of 9 cells. Each cell is either:
0 - Empty
1 - Player1
2 - Player2
012
345
678
"""
winning_patterns = {
    0: [[1, 2], [4, 8], [3, 6]],
    1: [[0, 2], [4, 7]],
    2: [[0, 1], [5, 8], [4, 6]],
    3: [[0, 6], [4, 5]],
    4: [[0, 8], [1, 7], [2, 6], [3, 5]],
    5: [[2, 8], [3, 4]],
    6: [[0, 3], [2, 4], [7, 8]],
    7: [[1, 4], [6, 8]],
    8: [[0, 4], [2, 5], [6, 7]]
    }
class TicTacToeGame(game.Game):
    def __init__(self):
        super().__init__()

    def reset(self):
        return self.get_encoded_binary([0] * 9)

    def move(self, binary_state, move, turn):
        legal_moves = self.get_legal_moves(binary_state)
        assert move in legal_moves

        list_state = self.get_decoded_list(binary_state)
        assert list_state[move] == 0

        assert turn in [game.GameTurn.PLAYER1, game.GameTurn.PLAYER2]

        list_state[move] = 1 if turn == game.GameTurn.PLAYER1 else 2

        new_binary_state = self.get_encoded_binary(list_state)
        result = game.GameResult.NOT_COMPLETED
        switch_turns = True
        return new_binary_state, result, True

    def get_legal_moves(self, binary_state):
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

    def render(self, binary_state):
        list_state = self.get_decoded_list(binary_state)
        for ndx, cell in enumerate(list_state):
            label = '.'
            if cell == 1:
                label = 'X'
            elif cell == 2:
                label = 'O'
            print(label, end='')
            if (ndx + 1) % 3 == 0:
                print('')

def play_random_game():
    ttt = TicTacToeGame()
    binary_state = ttt.reset()
    turn = game.GameTurn.PLAYER1
    while True:
        legal_moves = ttt.get_legal_moves(binary_state)
        if len(legal_moves) == 0:
            break
        move = random.choice(legal_moves)
        binary_state, result, switch_players = ttt.move(binary_state, move, turn)
        turn = ttt.switch_players(turn)
        # print(ttt.get_decoded_list(binary_state))
        ttt.render(binary_state)


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
    for move in range(9):
        for test_set in winning_patterns[move]:
            list_state = [0] * 9
            list_state[move] = 2
            for m in test_set:
                list_state[m] = 1
            binary_state = ttt.get_encoded_binary(list_state)
            ttt.render(binary_state)
            print('-' * 20)

if __name__ == "__main__":
    # test_1()
    test_2()

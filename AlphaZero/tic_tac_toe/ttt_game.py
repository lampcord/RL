import game
import random

"""
TicTacToe
Position is represented as a list of 9 cells. Each cell is either:
0 - Empty
1 - Player1
2 - Player2
"""

class TicTacToeGame(game.Game):
    def __init__(self):
        super().__init__()

    def reset(self):
        return self.get_encoded_binary([0] * 9)

    def move(self, binary_state, move, turn):
        new_binary_state = 0
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


if __name__ == "__main__":
    # test_1()
    ttt = TicTacToeGame()
    legal_moves = ttt.get_legal_moves(ttt.get_encoded_binary([1, 0, 2, 2, 1, 2, 1, 0, 0]))
    print(legal_moves)

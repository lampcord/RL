"""
4-in-a-row game-related functions.

Field is 6*7 with pieces falling from the top to the bottom. There are two kinds of pieces: black and white,
which are encoded by 1 (black) and 0 (white).

There are two representation of the game:
1. List of 7 lists with elements ordered from the bottom. For example, this field

0     1
0     1
10    1
10  0 1
10  1 1
101 111

Will be encoded as [
  [1, 1, 1, 1, 0, 0],
  [0, 0, 0, 0],
  [1],
  [],
  [1, 1, 0],
  [1],
  [1, 1, 1, 1, 1, 1]
]

2. integer number consists from:
    a. 7*6 bits (column-wise) encoding the field. Unoccupied bits are zero
    b. 7*3 bits, each 3-bit number encodes amount of free entries on the top.
In this representation, the field above will be equal to those bits:
[
    111100,
    000000,
    100000,
    000000,
    110000,
    100000,
    111111,
    000,
    010,
    101,
    110,
    011,
    101,
    000
]

All the code is generic, so, in theory you can try to adjust the field size.
But tests could become broken.
"""
import game

GAME_ROWS = 6
GAME_COLS = 7
BITS_IN_LEN = 3
PLAYER_BLACK = 1
PLAYER_WHITE = 0
COUNT_TO_WIN = 4


class C4Game(game.Game):
    def __init__(self):
        super().__init__()

    def get_initial_position(self):
        return self.get_encoded_binary([[]] * GAME_COLS, game.GameTurn.PLAYER1)

    def move(self, binary_state, move, turn):
        raise NotImplementedError("move")

    def get_legal_moves(self, binary_state, turn):
        raise NotImplementedError("get_legal_moves")

    def get_encoded_binary(self, list_state, turn):
        assert isinstance(list_state, list)
        assert len(list_state) == GAME_COLS

        bits = []
        len_bits = []
        for col in list_state:
            bits.extend(col)
            free_len = GAME_ROWS - len(col)
            bits.extend([0] * free_len)
            len_bits.extend(self.int_to_bits(free_len, bits=BITS_IN_LEN))
        bits.extend(len_bits)
        return self.bits_to_int(bits)

    def get_decoded_list(self, binary_state, turn):
        assert isinstance(binary_state, int)
        bits = self.int_to_bits(binary_state, bits=GAME_COLS * GAME_ROWS + GAME_COLS * BITS_IN_LEN)
        res = []
        len_bits = bits[GAME_COLS * GAME_ROWS:]
        for col in range(GAME_COLS):
            vals = bits[col * GAME_ROWS:(col + 1) * GAME_ROWS]
            lens = self.bits_to_int(len_bits[col * BITS_IN_LEN:(col + 1) * BITS_IN_LEN])
            if lens > 0:
                vals = vals[:-lens]
            res.append(vals)
        return res

    def bits_to_int(self, bits):
        res = 0
        for b in bits:
            res *= 2
            res += b
        return res

    def int_to_bits(self, num, bits):
        res = []
        for _ in range(bits):
            res.append(num % 2)
            num //= 2
        return res[::-1]

    def render(self, binary_state, turn):
        list_state = self.get_decoded_list(binary_state, turn)
        data = [[' '] * GAME_COLS for _ in range(GAME_ROWS)]
        for col_idx, col in enumerate(list_state):
            for rev_row_idx, cell in enumerate(col):
                row_idx = GAME_ROWS - rev_row_idx - 1
                data[row_idx][col_idx] = str(cell)
        display_state = [''.join(row) for row in data]
        for line in display_state:
            print(line)

if __name__ == "__main__":
    c4_game = C4Game()
    list_state = [
      [1, 1, 1, 1, 0, 0],
      [0, 0, 0, 0],
      [1],
      [],
      [1, 1, 0],
      [1],
      [1, 1, 1, 1, 1, 1]
    ]

    turn = game.GameTurn.PLAYER1

    binary_state = c4_game.get_encoded_binary(list_state, turn)

    c4_game.render(binary_state, turn)

    list_state = c4_game.get_decoded_list(binary_state, turn)
    new_binary_state = c4_game.get_encoded_binary(list_state, turn)
    print(binary_state, new_binary_state)
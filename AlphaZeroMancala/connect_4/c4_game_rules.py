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
import numpy as np
from game_rules import GameResult, GameRules

GAME_ROWS = 6
GAME_COLS = 7
BITS_IN_LEN = 3
PLAYER_BLACK = 1
PLAYER_WHITE = 0
COUNT_TO_WIN = 4

winning_sets = [
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1)
]


class C4GameRules(GameRules):
    def __init__(self):
        super().__init__(number_of_players=2)

    def get_player_bounds(self):
        return 2, 2

    def get_initial_position(self):
        return self.get_encoded_binary([[]] * GAME_COLS)

    def move(self, state, move, turn):
        assert isinstance(state, int)
        assert isinstance(move, int)
        assert 0 <= move < GAME_COLS
        assert turn in [0, 1]
        list_state = self.get_decoded_list(state)
        assert len(list_state[move]) < GAME_ROWS
        list_state[move].append(turn)
        # check for victory: the simplest vertical case
        suff = list_state[move][-COUNT_TO_WIN:]
        won = suff == [turn] * COUNT_TO_WIN
        if not won:
            won = self._check_won(list_state, move, 0) or self._check_won(list_state, move, 1) or self._check_won(
                list_state, move, -1)

        state = self.get_encoded_binary(list_state)
        new_turn = 1 - turn

        result = GameResult.CONTINUE
        if won:
            result = GameResult.WIN
        else:
            if len(self.get_legal_moves(state, turn)) == 0:
                result = GameResult.TIE

        return state, new_turn, result, {}

    def get_legal_moves(self, state, turn):
        assert isinstance(state, int)
        field = self.get_decoded_list(state)
        return [idx for idx, col in enumerate(field) if len(col) < GAME_ROWS]

    def get_encoded_binary(self, list_state):
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

    def get_decoded_list(self, state):
        assert isinstance(state, int)
        bits = self.int_to_bits(state, bits=GAME_COLS * GAME_ROWS + GAME_COLS * BITS_IN_LEN)
        list_state = []
        len_bits = bits[GAME_COLS * GAME_ROWS:]
        for col in range(GAME_COLS):
            vals = bits[col * GAME_ROWS:(col + 1) * GAME_ROWS]
            lens = self.bits_to_int(len_bits[col * BITS_IN_LEN:(col + 1) * BITS_IN_LEN])
            if lens > 0:
                vals = vals[:-lens]
            list_state.append(vals)

        return list_state

    def _check_won(self, field, col, delta_row):
        player = field[col][-1]
        coord = len(field[col]) - 1
        total = 1
        # negative dir
        cur_coord = coord - delta_row
        for c in range(col - 1, -1, -1):
            if len(field[c]) <= cur_coord or cur_coord < 0 or cur_coord >= GAME_ROWS:
                break
            if field[c][cur_coord] != player:
                break
            total += 1
            if total == COUNT_TO_WIN:
                return True
            cur_coord -= delta_row
        # positive dir
        cur_coord = coord + delta_row
        for c in range(col + 1, GAME_COLS):
            if len(field[c]) <= cur_coord or cur_coord < 0 or cur_coord >= GAME_ROWS:
                break
            if field[c][cur_coord] != player:
                break
            total += 1
            if total == COUNT_TO_WIN:
                return True
            cur_coord += delta_row
        return False

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

    def check_for_win(self, state, turn):
        table = np.full((GAME_COLS, GAME_ROWS), -1)
        list_state = self.get_decoded_list(state)
        data = [[-1] * GAME_COLS for _ in range(GAME_ROWS)]
        for col_idx, col in enumerate(list_state):
            for rev_row_idx, cell in enumerate(col):
                row_idx = GAME_ROWS - rev_row_idx - 1
                table[col_idx][row_idx] = str(cell)
        for row in range(GAME_ROWS):
            for col in range(GAME_COLS):
                for winning_set in winning_sets:
                    start_x = col
                    start_y = row
                    win = [(start_x, start_y)]
                    start_symbol = table[start_x][start_y]
                    if start_symbol < 0:
                        continue

                    for pos in range(COUNT_TO_WIN - 1):
                        start_x += winning_set[0]
                        start_y += winning_set[1]
                        if start_x >= 0 and start_x < GAME_COLS and start_y >= 0 and start_y < GAME_ROWS:
                            if table[start_x][start_y] == start_symbol:
                                win.append((start_x, start_y))
                            else:
                                break
                    if len(win) == 4:
                        return win
        return None

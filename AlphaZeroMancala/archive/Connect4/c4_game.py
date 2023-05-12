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
import ctypes
import os
import random
import time

import numpy as np
import game_rules
import pygame
from Connect4 import c4_board
from Connect4.c4_board import C4Board

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
class C4Game(game.Game):
    def __init__(self):
        super().__init__()

    def get_initial_position(self):
        return self.get_encoded_binary([[]] * GAME_COLS, game.GameTurn.PLAYER1)

    def move(self, binary_state, move, turn):
        assert isinstance(binary_state, int)
        assert isinstance(move, int)
        assert 0 <= move < GAME_COLS
        assert turn == game.GameTurn.PLAYER1 or turn == game.GameTurn.PLAYER2
        list_state = self.get_decoded_list(binary_state, turn)
        assert len(list_state[move]) < GAME_ROWS
        list_state[move].append(turn.value)
        # check for victory: the simplest vertical case
        suff = list_state[move][-COUNT_TO_WIN:]
        won = suff == [turn.value] * COUNT_TO_WIN
        if not won:
            won = self._check_won(list_state, move, 0) or self._check_won(list_state, move, 1) or self._check_won(list_state, move, -1)

        binary_state = self.get_encoded_binary(list_state, turn)

        result = game.GameResult.NOT_COMPLETED
        if won:
            result = game.GameResult.PLAYER1 if turn == game.GameTurn.PLAYER1 else game.GameResult.PLAYER2
        else:
            if len(self.get_legal_moves(binary_state, turn)) == 0:
                result = game.GameResult.DRAW

        return binary_state, result, True, {}

    def get_legal_moves(self, binary_state, turn):
        assert isinstance(binary_state, int)
        field = self.get_decoded_list(binary_state, turn)
        return [idx for idx, col in enumerate(field) if len(col) < GAME_ROWS]

    def get_encoded_binary(self, list_state, turn):
        assert isinstance(list_state, list)
        assert len(list_state) == GAME_COLS

        if turn == game.GameTurn.PLAYER2:
            list_state = self.flip_board(list_state)

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
        list_state = []
        len_bits = bits[GAME_COLS * GAME_ROWS:]
        for col in range(GAME_COLS):
            vals = bits[col * GAME_ROWS:(col + 1) * GAME_ROWS]
            lens = self.bits_to_int(len_bits[col * BITS_IN_LEN:(col + 1) * BITS_IN_LEN])
            if lens > 0:
                vals = vals[:-lens]
            list_state.append(vals)

        if turn == game.GameTurn.PLAYER2:
            list_state = self.flip_board(list_state)

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

    def flip_board(selfs, list_state):
        for col in list_state:
            for ndx in range(len(col)):
                col[ndx] = 1 - col[ndx]
        return list_state


    def render(self, binary_state, turn, win=None):
        list_state = self.get_decoded_list(binary_state, turn)
        data = [['   '] * GAME_COLS for _ in range(GAME_ROWS)]
        for col_idx, col in enumerate(list_state):
            for rev_row_idx, cell in enumerate(col):
                row_idx = GAME_ROWS - rev_row_idx - 1
                if win and (col_idx, row_idx) in win:
                    data[row_idx][col_idx] = f"({str(cell)})"
                else:
                    data[row_idx][col_idx] = f" {str(cell)} "
        display_state = ['|'.join(row) for row in data]
        for line in display_state:
            print('+---+---+---+---+---+---+---+')
            print('|' + line + '|')
        print('+---+---+---+---+---+---+---+')
        print('  0   1   2   3   4   5   6')
        print(binary_state, turn.name)

    def check_for_win(self, binary_state, turn):
        table = np.full((GAME_COLS, GAME_ROWS), -1)
        list_state = self.get_decoded_list(binary_state, turn)
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


def play_random_game(show=False, use_board=False):
    c4_game = C4Game()
    if use_board:
        board = C4Board()
    turn = game.GameTurn.PLAYER1
    binary_state = c4_game.get_initial_position()

    result = game.GameResult.NOT_COMPLETED
    win_set = None
    while result == game.GameResult.NOT_COMPLETED:
        if show:
            print(binary_state)
            c4_game.render(binary_state, turn, win_set)
            print()
        legal_moves = c4_game.get_legal_moves(binary_state, turn)
        if len(legal_moves) == 0:
            break
        if use_board:
            board_list_state = c4_game.get_decoded_list(binary_state, turn)
            board.draw_board(board_list_state, turn.value, legal_moves, "", win_set)
            pygame.display.update()
            move = board.get_move(legal_moves)
            time.sleep(.3)
        else:
            move = random.choice(legal_moves)
        binary_state, result, swap_players, info = c4_game.move(binary_state, move, turn)
        win_set = c4_game.check_for_win(binary_state, turn)

        if win_set:
            if result == game.GameResult.NOT_COMPLETED or result == game.GameResult.DRAW:
                print(f"win_set {str(win_set)} result {result}")
                print(binary_state)
                c4_game.render(binary_state, turn, win_set)
        else:
            if result == game.GameResult.PLAYER1 or result == game.GameResult.PLAYER2:
                print(f"win_set {str(win_set)} result {result}")
                print(binary_state)
                c4_game.render(binary_state, turn, win_set)

        if swap_players:
            binary_state, turn = c4_game.switch_players(binary_state, turn)
    if show:
        print(binary_state)
        c4_game.render(binary_state, turn, win_set)
    if use_board:
        board_list_state = c4_game.get_decoded_list(binary_state, turn)
        board.draw_board(board_list_state, turn.value, legal_moves, "", win_set)
        board.get_move(legal_moves)
        time.sleep(.3)


if __name__ == "__main__":
    screen = pygame.display.set_mode((c4_board.WINDOW_WIDTH, c4_board.WINDOW_HEIGHT))
    pygame.display.set_caption("Connect 4")
    play_random_game(show=True, use_board=True)




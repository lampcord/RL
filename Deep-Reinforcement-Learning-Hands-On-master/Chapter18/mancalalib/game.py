'''
Encoding:

We encode by using a binary number where the 0's represent stones and the 1's represent separators between them.

For example:

Imagine the starting position:

4, 4, 4, 4, 4, 4, 0
4, 4, 4, 4, 4, 4, 0

This will be encoded as follows:

0000100001000010000100001000011000010000100001000010000100001
---- ---- ---- ---- ---- ----  ---- ---- ---- ---- ---- ----
  4    4    4    4    4    4  0  4    4    4    4    4    4  0

This uses 13 separators + 48 stones or 61 bits. We need one more bit to represent which players turn it is (0 or 1).
This makes 62 so we can fit the entire board in a single 64 bit integer.


'''
import random

WHITE_FIRST_BUCKET = 0
WHITE_CASTOFF_BUCKET = 6
BLACK_FIRST_BUCKET = 7
BLACK_CASTOFF_BUCKET = 13
BOARDSIZE = 14
SEPARATORS = 13
TOTALSTONES = 48
PLAYER_BLACK = 1
PLAYER_WHITE = 0
MAX_MOVE_INDEX = 6


def bits_to_int(bits):
    res = 0
    for b in bits:
        res *= 2
        res += b
    return res


def int_to_bits(num, bits):
    res = []
    for _ in range(bits):
        res.append(num % 2)
        num //= 2
    return res[::-1]


def encode_lists(field_lists):
    """
    Encode lists representation into the binary numbers
    :param field_lists: list of BOARDSIZE lists with numbers between 0 and 48
    :return: integer number with encoded game state
    """
    assert isinstance(field_lists, list)
    assert len(field_lists) == BOARDSIZE

    bits = []
    for stones in field_lists:
        for stone in range(stones):
            bits.append(0)
        bits.append(1)
    return bits_to_int(bits)

INITIAL_STATE = encode_lists([4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4,  0])

def decode_binary(state_int):
    """
    Decode binary representation into the list view
    :param state_int: integer representing the field
    :return: list of BOARDSIZE integers
    """
    assert isinstance(state_int, int)
    bits = int_to_bits(state_int, bits=TOTALSTONES + SEPARATORS + 1)
    state_list = [0] * BOARDSIZE

    bucket_index = WHITE_FIRST_BUCKET

    for bit in bits:
        if bit == 0:
            state_list[bucket_index] += 1
        else:
            bucket_index += 1

    return state_list


def get_opponent(player):
    return 1 - player


def possible_moves(state_int, turn):
    """
    This function could be calculated directly from bits, but I'm too lazy
    :param state_int: field representation
    :return: the list of buckets which we can make a move
    """
    assert isinstance(state_int, int)
    state_list = decode_binary(state_int)
    if turn == PLAYER_WHITE:
        first = WHITE_FIRST_BUCKET
    else:
        first = BLACK_FIRST_BUCKET
    return [idx for idx in range(6) if state_list[idx + first] > 0]

def move(state_int, move, player):
    """
    Perform move into given column. Assume the move could be performed, otherwise, assertion will be raised
    :param state_int: current state
    :param move: starting bucket from players pov
    :param player: player index (PLAYER_WHITE or PLAYER_BLACK
    :return: tuple of (state_new, winner, swap_players)
    :    state_new: state after move
    :    winner None or player that just won, NOT always player that just moved!
    :    swap_players: False if move allows same player to continue
    """
    assert isinstance(state_int, int)
    assert isinstance(move, int)
    assert 0 <= move < MAX_MOVE_INDEX
    assert player == PLAYER_BLACK or player == PLAYER_WHITE
    state_list = decode_binary(state_int)

    if player == PLAYER_WHITE:
        start_bucket = move + WHITE_FIRST_BUCKET
        skip_bucket = BLACK_CASTOFF_BUCKET
    else:
        start_bucket = move + BLACK_FIRST_BUCKET
        skip_bucket = WHITE_CASTOFF_BUCKET

    # pickup all stones from start bucket
    num_stones = state_list[start_bucket]
    state_list[start_bucket] = 0

    # sequentially drop stones in each bucket moving counterclockwise around board
    target_bucket = start_bucket
    while num_stones > 0:
        target_bucket = (target_bucket + 1) % BOARDSIZE

        # skip opponent's castoff bucket
        if target_bucket == skip_bucket:
            continue

        state_list[target_bucket] += 1
        num_stones -= 1

    winning_player = None
    if state_list[WHITE_CASTOFF_BUCKET] > 24:
        winning_player = PLAYER_WHITE
    elif state_list[BLACK_CASTOFF_BUCKET] > 24:
        winning_player = PLAYER_BLACK

    swap_players = True
    state_int_new = encode_lists(state_list)

    return state_int_new, winning_player, swap_players


def generate_random_board():
    state_list = [0] * BOARDSIZE
    total_stones = TOTALSTONES
    for x in range(TOTALSTONES):
        bucket = random.randint(0, BOARDSIZE - 1)
        stones = random.randint(1, total_stones)
        stones = min(stones, 4)
        state_list[bucket] += stones
        total_stones -= stones
        if total_stones <= 0:
            break
    return state_list

if __name__ == "__main__":
    encoded = INITIAL_STATE
    print (encoded)
    decoded = decode_binary(encoded)
    print(decoded)
    print(possible_moves(encoded, PLAYER_WHITE))
    print(possible_moves(encoded, PLAYER_BLACK))

    for test in range(1_000):
        if test % 100 == 0:
            print('')
        print('.', end='')

        state_list = generate_random_board()
        encoded = encode_lists(state_list)
        decoded = decode_binary(encoded)
        reencoded = encode_lists(decoded)
        if test < 10:
            print(decoded)
            print(possible_moves(encoded, PLAYER_WHITE))
            print(possible_moves(encoded, PLAYER_BLACK))
        assert encoded == reencoded

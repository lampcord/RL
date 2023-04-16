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

AFIRST = 0
ACAPTURED = 6
BFIRST = 7
BCAPTURED = 13
BOARDSIZE = 14
SEPARATORS = 13
TOTALSTONES = 48


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

    bucket_index = AFIRST

    for bit in bits:
        if bit == 0:
            state_list[bucket_index] += 1
        else:
            bucket_index += 1

    return state_list

if __name__ == "__main__":
    encoded = INITIAL_STATE
    print (encoded)
    decoded = decode_binary(encoded)
    print(decoded)

    for test in range(1_000_000):
        if test % 100000 == 0:
            print('')
        if test % 1000 == 0:
            print('.', end='')
        state_list = [0] * BOARDSIZE
        for x in range(TOTALSTONES):
            bucket = random.randint(0, BOARDSIZE - 1)
            state_list[bucket] += 1

        encoded = encode_lists(state_list)
        decoded = decode_binary(encoded)
        reencoded = encode_lists(decoded)
        assert encoded == reencoded

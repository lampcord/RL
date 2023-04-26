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


class C4Game(game.Game):
    def __init__(self):
        super().__init__()

    def get_initial_position(self):

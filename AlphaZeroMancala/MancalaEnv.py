'''
Encoding:

We encode by using a binary number where the 0's represent stones and the 1's represent seperators between them.

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
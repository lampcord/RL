/*

Format for storing a backgammon position:


+------+------+
|X....O|.O...X|
|X....O|.O...X|
|.....O|.O...X|
|.....O|.....X|
|.....O|.....X|
|......|......|
+------+------+
|      |      |
+------+------+
|......|......|
|.....X|.....O|
|.....X|.....O|
|.....X|.X...O|
|O....X|.X...O|
|O....X|.X...O|
+------+------+

The board consists of 24 slots along with 2 cast off areas for each player and 2 bar areas for each player.
Each slot can contain a maximum of 15 pieces. This fits into 4 bits. Adding a slot to indicate black or white brings this to 5 for a total of 120 bits.
For the bar, we only need 4 bits since we have 1 for each, black and white.
The castoff is implied by 15 - total on board and bar. This allows the entire position to be stored in 128 bits.

    0     1     2     3     4     5      6     7     8     9    10    11  White Bar 
 (2W)                    (5B)         (3B)                          (5W) 
00010 00000 00000 00000 10101 00000  10011 00000 00000 00000 00000 00101  0000
10010 00000 00000 00000 00101 00000  00011 00000 00000 00000 00000 10101  0000
 (2B)                    (5W)         (3W)                          (5B)
   23    22    21    20    19    18     17    16    15    14    13    12  Black Bar


To facilitate faster move geneation, we can create 2 move masks:
1) Moving player's candidate slots:

100000 000001 000010 100000 (candidate slots for white player)
If moving player has pieces on the bar, this will be all 0's since the only place you can move from is the bar.

2) Blocked slots:

000001 010000 100000 000001 (blocked slots for black player)

This represents any slot that has > 1 enemy pieces.

This is always represented from the moving players POV moving left to right.

This scheme should allow the use of masks to quickly generate the possible moves.

The die rolls will be handled by 
roll = rand % 36

We can then get the two dice by 
d1 = (roll % 6) + 1 
d2 = (roll / 6) + 1

This allows die rolls with only 1 call to rand.

















*/
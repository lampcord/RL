#include "backgammon.h"
#include <tuple>
#include <iostream>
#include <array>
/*

Format for storing a backgammon position:


+-----------+-----------+
|X . . . . O|. O . . . X|
|X . . . . O|. O . . . X|
|. . . . . O|. O . . . X|
|. . . . . O|. . . . . X|
|. . . . . O|. . . . . X|
|. . . . . .|. . . . . .|
+-----------+-----------+
|           |           |
+-----------+-----------+
|. . . . . .|. . . . . .|
|. . . . . X|. . . . . O|
|. . . . . X|. . . . . O|
|. . . . . X|. X . . . O|
|O . . . . X|. X . . . O|
|O . . . . X|. X . . . O|
+-----------+-----------+

The board consists of 24 slots along with 2 cast off areas for each player and 2 bar areas for each player.
Each slot can contain a maximum of 15 pieces. This fits into 4 bits. Adding a slot to indicate black or white brings this to 5 for a total of 120 bits.
For the bar, we only need 4 bits since we have 1 for each, black and white.
The castoff is implied by 15 - total on board and bar. This allows the entire position to be stored in 128 bits.

WBar      0     1     2     3     4     5      6     7     8     9    10    11  
       (2W)                          (5B)         (3B)                    (5W)
0000  00010 00000 00000 00000 00000 10101  00000 00011 00000 00000 00000 00101  
0000  10101 00000 00000 00000 00011 00000  00101 00000 00000 00000 00000 10010  
       (5B)                    (3W)         (5W)                          (2B)
BBar     12    13    14    15    16    17     18    19    20    21    22    23  

Shift for slot = 55 - (slot % 12) * 5
Word for slot = slot / 12

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

using namespace std;

namespace BackgammonNS
{
    typedef tuple<unsigned char, unsigned char> slot_info;
    
    slot_info get_bar_info(const PositionType& position)
    {
        unsigned long long workspace = 0x0;
        const unsigned char shift = 60;
        workspace = position.position[0];
        workspace >>= shift;
        unsigned int player_0_bar = workspace & 0b1111;
        workspace = position.position[1];
        workspace >>= shift;
        unsigned int player_1_bar = workspace & 0b1111;

        return slot_info{ player_0_bar, player_1_bar };
    }

    slot_info get_slot_info(const PositionType& position, unsigned char slot)
    {
        unsigned long long workspace = 0x0;
        const unsigned char shift = 55 - (slot % 12) * 5;
        const unsigned char position_ndx = slot / 12;

        workspace = position.position[position_ndx];
        workspace >>= shift;
        unsigned char num_checkers = workspace & 0b1111;
        unsigned char player = workspace & 0b10000;
        player >>= 4;

        return slot_info{ player, num_checkers };
    }

    void Backgammon::get_initial_position(PositionType& position)
    {
        position.position[0] = 0b0000000100000000000000000000010101000001001100000000000000000101;
        position.position[1] = 0b0000101010000000000000000001100000001010000000000000000000010010;
    }

    void Backgammon::render_board_section(const BackgammonNS::PositionType& position, bool top)
    {
        array<unsigned int, 6> top_lines{0, 1, 2, 3, 4, 5};
        array<unsigned int, 6> bot_lines{5, 4, 3, 2, 1, 0};
        array<unsigned int, 6>* lines;

        array<unsigned int, 12> top_slots{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
        array<unsigned int, 12> bot_slots{23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12};
        array<unsigned int, 12>* slots;

        if (top)
        {
            lines = &top_lines;
            slots = &top_slots;
        }
        else
        {
            lines = &bot_lines;
            slots = &bot_slots;
        }

        for (auto line: *lines)
        {
            cout << '|';
            for (auto slot: *slots)
            {
                const auto [player, num_checkers] = get_slot_info(position, slot);
                if (num_checkers > line)
                {
                    if (line >= 5)
                    {
                        cout << (int)num_checkers - 5;
                    }
                    else
                    {
                        cout << (player == 0 ? 'O' : 'X');
                    }
                }
                else
                {
                    cout << '.';
                }
                switch (slot)
                {
                case 5:
                case 18:
                    cout << '|';
                    break;
                case 11:
                case 12:
                    break;
                default:
                    cout << ' ';
                }
            }
            cout << '|' << endl;
        }
    }

    void Backgammon::render(const PositionType& position)
    {
        const auto [player_0_bar, player_1_bar] = get_bar_info(position);

        cout << "+-----------+-----------+" << endl;
        render_board_section(position, true);
        cout << "+-----------+-----------+" << endl;
        cout << '|';
        for (auto bar = 0; bar < 11; bar++) cout << (player_0_bar > bar ? 'O' : ' ');
        cout << '|';
        for (auto bar = 0; bar < 11; bar++) cout << (player_1_bar > bar ? 'X' : ' ');
        cout << "|" << endl;
        cout << '|';
        for (auto bar = 11; bar < 15; bar++) cout << (player_0_bar > bar ? 'O' : ' ');
        cout << "       |";
        for (auto bar = 11; bar < 15; bar++) cout << (player_1_bar > bar ? 'X' : ' ');
        cout << "       |" << endl;
        cout << "+-----------+-----------+" << endl;
        render_board_section(position, false);
        cout << "+-----------+-----------+" << endl;

    }
}

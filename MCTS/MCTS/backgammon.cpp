#include "backgammon.h"
#include <tuple>
#include <iostream>
#include <array>
#include <bitset>
#include <vector>
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

A move can be represented by a collection of starting locations (5 bits) and die values (3 bits).
Worst case is a double (5 + 3) * 4 = 32 bits.

Example, moving 1-1 from starting position for player 0:
10000 001 10000 001 10010 001 10010 001

Test Positions:

*/

using namespace std;

namespace BackgammonNS
{
    typedef tuple<unsigned char, unsigned char> slot_info;
    
    const unsigned int max_move_list = 1024;
    const unsigned char bar_indicator = 0b11111000;

    static MoveStruct move_list[max_move_list];
    static unsigned int move_list_size = 0;
    static unordered_map<PositionStruct, unsigned char, PositionStructHash> duplicate_positions;

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

    void update_slot(PositionType &position, unsigned char player, unsigned char slot, bool increment)
    {
        const unsigned char shift = 55 - (slot % 12) * 5;
        const unsigned char position_ndx = slot / 12;

        if (increment)
        {
            // check for single enemy piece.
            auto [slot_player, num_checkers] = get_slot_info(position, slot);
            if (num_checkers == 1 && slot_player != player)
            // if found, this is a hit, move oponent's piece to bar.
            {
                // if found, this is a hit, move oponent's piece to bar.
                position.position[slot_player] += (1ull << 60);
            }
            else
            {
                // normal move onto empty slot or existing player stack.
                position.position[position_ndx] += (1ull << shift);
            }

            // update control. (No op for non hit)
            unsigned long long control_mask = ~(1ull << (shift + 4));
            position.position[position_ndx] &= control_mask;
            position.position[position_ndx] |= ((unsigned long long)player << (shift + 4));
        }
        else
        {
            // moved from bar
            if (slot == bar_indicator)
            {
                position.position[player] -= (1ull << 60);
            }
            else
            {
                // normal move from board.
                position.position[position_ndx] -= (1ull << shift);
            }
        }
    }

    void Backgammon::position_from_string(const string str_pos, BackgammonNS::PositionType& position)
    {
        auto player = 0;
        unsigned long long workspace = atoi(str_pos.substr(24 * 3, 3).c_str());
        for (auto slot = 0; slot < 12; slot++)
        {
            workspace <<= 5;
            auto str_value = str_pos.substr(slot * 3, 3);
            player = str_value[0] == 'B' ? 0b10000 : 0b00000;
            auto value = atoi(str_value.substr(1, 2).c_str());
            workspace |= (player + value);
        }
        cout << bitset<64>(workspace) << endl;
        position.position[0] = workspace;
        workspace = atoi(str_pos.substr(25 * 3, 3).c_str());
        for (auto slot = 0; slot < 12; slot++)
        {
            workspace <<= 5;
            auto str_value = str_pos.substr((slot + 12) * 3, 3);
            player = str_value[0] == 'B' ? 0b10000 : 0b00000;
            auto value = atoi(str_value.substr(1, 2).c_str());
            workspace |= (player + value);
        }
        cout << bitset<64>(workspace) << endl;
        position.position[1] = workspace;
    }

    void Backgammon::get_initial_position(PositionType& position)
    {
        //position.position[0] = 0b0000000100000000000000000000010101000001001100000000000000000101;
        //position.position[1] = 0b0000101010000000000000000001100000001010000000000000000000010010;

        //position.position[0] = 0b0000000100000000000000000000010101000001001100000000000000000101;
        //position.position[1] = 0b0000101010000000000000000001100000001011000100000000000000010001;

        //position.position[0] = 0b0000000100000000000000000000010101000001001100000000000000000101;
        //position.position[1] = 0b0001101010000000000000000001100000001000000000000000000000110001;

        position.position[0] = 0b0000000100000000000000000000010101000001001100000000000000000101;
        position.position[1] = 0b0000101010000000000000000001100000001010000000000000000000010010;

    }

    bool gen_moves_for_1_die(const unsigned int pos_ndx, const unsigned int& blocked, const unsigned char player, const unsigned int die, unsigned int move_ndx, castoff_available can_castoff)
    {
        unsigned long long workspace = 0x0;
        const unsigned char oponent_test = player == 0 ? 0b10000 : 0x0;
        unsigned int blocked_ndx = 1 << 23;
        char delta = player == 0 ? die : -(char)die;
        bool expanded = false;

        auto [bar_0_count, bar_1_count] = get_bar_info(move_list[pos_ndx].result_position);
        auto bar_count = player == 0 ? bar_0_count : bar_1_count;

        // Initial position wasn't ready for castoff but was close enough that 
        // it might be after some checkers are moved.
        if (can_castoff == castoff_available::pending)
        {
            auto starting_slot = player == 0 ? 0 : 6;
            auto ending_slot = player == 0 ? 17 : 23;
            bool can_castoff_check = true;
            for (auto slot = starting_slot; slot <= ending_slot; slot++)
            {
                auto [slot_player, num_checkers] = get_slot_info(move_list[pos_ndx].result_position, slot);
                if (slot_player == player && num_checkers > 0)
                {
                    can_castoff_check = false;
                    break;
                }
            }
            if (can_castoff_check) can_castoff = castoff_available::available;
        }

        // Position is valid for casting off.
        if (can_castoff == castoff_available::available)
        {
            // Check if we have a checker on the slot of the die roll.
            auto slot = player == 1 ? die - 1 : 24 - die;
            auto [slot_player, num_checkers] = get_slot_info(move_list[pos_ndx].result_position, slot);
            if (slot_player == player && num_checkers > 0)
            {
                expanded = true;
                unsigned char move = (slot << 3) + die;

                move_list[move_list_size] = move_list[pos_ndx];
                move_list[move_list_size].moves[move_ndx] = move;
                update_slot(move_list[move_list_size].result_position, player, slot, false);

                auto loc = duplicate_positions.find(move_list[move_list_size].result_position);
                if (loc == duplicate_positions.end())
                {
                    duplicate_positions[move_list[move_list_size].result_position] = 1;
                    move_list_size++;
                }
                else
                {
                    loc->second++;
                }
            }
            else
            {
                // We don't have a piece on the slot of the die roll,
                // Check if all of the slots above it are also open.
                auto start_slot = player == 0 ? 18 : 5;
                auto delta = player == 0 ? 1 : -1;
                auto first_slot_with_pieces = start_slot;
                auto slot = player == 1 ? die - 1 : 24 - die;

                for (auto x = 0; x < 6; x++)
                {
                    auto [slot_player, num_checkers] = get_slot_info(move_list[pos_ndx].result_position, first_slot_with_pieces);
                    if (slot_player == player && num_checkers > 0)
                    {
                        break;
                    }
                    first_slot_with_pieces += delta;
                }

                if ((player == 1 && first_slot_with_pieces < slot) ||
                    (player == 0 && first_slot_with_pieces > slot))
                {
                    expanded = true;
                    unsigned char move = (first_slot_with_pieces << 3) + die;

                    move_list[move_list_size] = move_list[pos_ndx];
                    move_list[move_list_size].moves[move_ndx] = move;
                    update_slot(move_list[move_list_size].result_position, player, first_slot_with_pieces, false);

                    auto loc = duplicate_positions.find(move_list[move_list_size].result_position);
                    if (loc == duplicate_positions.end())
                    {
                        duplicate_positions[move_list[move_list_size].result_position] = 1;
                        move_list_size++;
                    }
                    else
                    {
                        loc->second++;
                    }
                }
            }
        }

        if (bar_count > 0)
        {
            // Move pieces off the bar.
            char target = player == 0 ? delta - 1 : 23 + delta;
            if (target >= 0 && target < 24 && (blocked & (blocked_ndx >> target)) == 0)
            {
                expanded = true;
                cout << "Die " << (int)die << " From Bar To " << (int)target << endl;
                unsigned char move = bar_indicator + die;

                move_list[move_list_size] = move_list[pos_ndx];
                move_list[move_list_size].moves[move_ndx] = move;
                update_slot(move_list[move_list_size].result_position, player, target, true);
                update_slot(move_list[move_list_size].result_position, player, bar_indicator, false);

                auto loc = duplicate_positions.find(move_list[move_list_size].result_position);
                if (loc == duplicate_positions.end())
                {
                    duplicate_positions[move_list[move_list_size].result_position] = 1;
                    move_list_size++;
                }
                else
                {
                    loc->second++;
                }
            }
        }
        else
        {
            // Normal move.
            for (auto slot = 0; slot < 24; slot++)
            {
                auto [position_player, num_checkers] = get_slot_info(move_list[pos_ndx].result_position, slot);
                if (position_player == player && num_checkers > 0)
                {
                    char target = slot + delta;
                    if (target < 0 || target >= 24) continue;
                    if (blocked & (blocked_ndx >> target)) continue;
                    expanded = true;

                    cout << "Die " << (int)die << " From " << (int)slot << " To " << (int)target << endl;
                    unsigned char move = (slot << 3) + die;

                    move_list[move_list_size] = move_list[pos_ndx];
                    move_list[move_list_size].moves[move_ndx] = move;
                    update_slot(move_list[move_list_size].result_position, player, target, true);
                    update_slot(move_list[move_list_size].result_position, player, slot, false);

                    auto loc = duplicate_positions.find(move_list[move_list_size].result_position);
                    if (loc == duplicate_positions.end())
                    {
                        duplicate_positions[move_list[move_list_size].result_position] = 1;
                        move_list_size++;
                    }
                    else
                    {
                        loc->second++;
                    }
                }
            }
        }
        return expanded;
    }
    void Backgammon::get_legal_moves(const PositionType& position, const unsigned char player, const unsigned int roll)
    {
        unsigned long long workspace = position.position[0];
        unsigned int blocked = 0x0;
        unsigned int blocked_ndx = 0x1 << 12;
        const unsigned char oponent_test = player == 0 ? 0b10000 : 0x0;

        unsigned char moves_to_castoff = 0;
        auto [bar_0_count, bar_1_count] = get_bar_info(position);
        auto bar_count = player == 0 ? bar_0_count : bar_1_count;
        moves_to_castoff += (4 * bar_count);
        auto castoff_counter = player == 1 ? 1 : 2;
        auto castoff_delta = player == 1 ? -1 : 1;

        for (auto slot = 0; slot < 12; slot++)
        {
            unsigned char slot_value = (workspace & 0b1110) != 0;
            unsigned char is_oponent = (workspace & 0b10000) == oponent_test;
            blocked |= (blocked_ndx * slot_value * is_oponent);

            moves_to_castoff += (castoff_counter * (workspace & 0b1111) * !is_oponent);

            blocked_ndx <<= 1;
            workspace >>= 5;

            castoff_counter += ((slot == 5) * castoff_delta);
        }

        workspace = position.position[1];
        blocked_ndx = 0x1;
        castoff_counter = player == 0 ? 0 : 3;

        for (auto slot = 0; slot < 12; slot++)
        {
            unsigned char slot_value = (workspace & 0b1110) != 0;
            unsigned char is_oponent = (workspace & 0b10000) == oponent_test;
            blocked |= (blocked_ndx * slot_value * is_oponent);

            moves_to_castoff += (castoff_counter * (workspace & 0b1111) * !is_oponent);

            blocked_ndx <<= 1;
            workspace >>= 5;

            castoff_counter += ((slot == 5) * castoff_delta);
        }

        auto die1 = roll % 6 + 1;
        auto die2 = roll / 6 + 1;

        move_list[0].clear();
        move_list[0].result_position = position;
        move_list_size = 1;
        duplicate_positions.clear();

        auto max_moves = 0;

        auto can_castoff = moves_to_castoff == 0 ? castoff_available::available : castoff_available::unavailable;
        if (die1 == die2)
        {
            if (moves_to_castoff > 0 && moves_to_castoff < 4)
            {
                can_castoff = castoff_available::pending;
            }
            auto start_move_list = move_list_size;
            if (gen_moves_for_1_die(0, blocked, player, die1, 0, can_castoff)) max_moves++;
            auto end_move_list = move_list_size;
            for (auto turn = 0; turn < 3; turn++)
            {
                bool expanded = false;
                for (auto x = start_move_list; x < end_move_list; x++)
                {
                    expanded |= gen_moves_for_1_die(x, blocked, player, die2, turn + 1, can_castoff);
                }
                if (expanded) max_moves++;
                start_move_list = end_move_list;
                end_move_list = move_list_size;
            }
        }
        else
        {
            if (moves_to_castoff == 1)
            {
                can_castoff = castoff_available::pending;
            }
            auto max_moves_die1 = 0;
            auto start_move_list = move_list_size;
            if (gen_moves_for_1_die(0, blocked, player, die1, 0, can_castoff)) max_moves_die1++;
            auto end_move_list = move_list_size;
            bool expanded = false;
            for (auto x = start_move_list; x < end_move_list; x++)
            {
                expanded |= gen_moves_for_1_die(x, blocked, player, die2, 1, can_castoff);
            }
            if (expanded) max_moves_die1++;

            auto max_moves_die2 = 0;
            start_move_list = move_list_size;
            if (gen_moves_for_1_die(0, blocked, player, die2, 0, can_castoff)) max_moves_die2++;
            end_move_list = move_list_size;
            expanded = false;
            for (auto x = start_move_list; x < end_move_list; x++)
            {
                expanded |= gen_moves_for_1_die(x, blocked, player, die1, 1, can_castoff);
            }
            if (expanded) max_moves_die2++;
            max_moves = max_moves_die1 > max_moves_die2 ? max_moves_die1 : max_moves_die2;
        }
        cout << "Max Moves: " << max_moves << " moves_to_castoff " << (int)moves_to_castoff << endl;

        auto duplicates = 0;
        auto total_valid = 0;
        vector<string> rolls;
        for (auto x = 0; x < move_list_size; x++)
        {
            bool valid = (max_moves > 0 && move_list[x].moves[max_moves - 1] != 0);
            if (valid)
            {
                string roll_desc = "";
                cout << "-----------------------------------------" << endl;
                cout << "Position " << x << endl;
                for (auto y = 0; y < 4; y++)
                {
                    if (move_list[x].moves[y] == 0) continue;
                    auto die = move_list[x].moves[y] & 0b111;
                    auto slot = move_list[x].moves[y] >> 3;
                    if (slot == (bar_indicator >> 3)) cout << "Die " << (int)die << " From Bar " << endl;
                    else cout << "Die " << (int)die << " From " << (int)slot << endl;
                    roll_desc += to_string(slot);
                    roll_desc += " to ";
                    roll_desc += to_string(player == 0 ? slot + die : slot - die);
                    roll_desc += ", ";
                }
                rolls.push_back(roll_desc);
                render(move_list[x].result_position);
                total_valid++;
            }
            cout << (valid ? "OK" : "INVALID") << endl;
            auto loc = duplicate_positions.find(move_list[x].result_position);
            if (loc != duplicate_positions.end())
            {
                cout << "Found " << (int)loc->second << " duplicates. " << endl;
                duplicates += loc->second;
            }
        }
        for (auto s : rolls)
        {
            cout << s << endl;
        }
        cout << "Total Moves Generated: " << move_list_size << endl;
        cout << "Total Duplicates: " << duplicates << endl;
        cout << "Total Valid: " << total_valid << endl;
    }

    void Backgammon::render_board_section(const BackgammonNS::PositionType& position, bool top, unsigned char casted_off)
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
            cout << '|';
            for (auto col = 0; col < 3; col++)
            {
                if (casted_off > line * 3 + col) cout << (top ? 'X' : 'O');
            }
            cout << endl;
        }
    }

    void Backgammon::render_bar_section(const BackgammonNS::PositionType& position)
    {
        const auto [player_0_bar, player_1_bar] = get_bar_info(position);
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
    }
    void Backgammon::render(const PositionType& position)
    {
        array<unsigned char, 2> casted_off = { 15, 15 };
        for (auto slot = 0; slot < 24; slot++)
        {
            auto [player, num_checkers] = get_slot_info(position, slot);
            casted_off[player] -= num_checkers;
        }
        const auto [player_0_bar, player_1_bar] = get_bar_info(position);
        casted_off[0] -= player_0_bar;
        casted_off[1] -= player_1_bar;

        cout << "                     1 1" << endl;
        cout << " 0 1 2 3 4 5 6 7 8 9 0 1" << endl;
        cout << "+-----------+-----------+" << endl;
        render_board_section(position, true, casted_off[1]);
        cout << "+-----------+-----------+" << endl;
        render_bar_section(position);
        cout << "+-----------+-----------+" << endl;
        render_board_section(position, false, casted_off[0]);
        cout << "+-----------+-----------+" << endl;
        cout << " 2 2 2 2 1 1 1 1 1 1 1 1" << endl;
        cout << " 3 2 1 0 9 8 7 6 5 4 3 2" << endl;

        cout << "position.position[0] = 0b" << bitset<64>(position.position[0]) << ";" << endl;
        cout << "position.position[1] = 0b" << bitset<64>(position.position[1]) << ";" << endl;
        cout << (int)casted_off[0] << " " << (int)casted_off[1] << endl;
    }
}
#include "backgammon.h"
#include "movelist.h"
#include "analyzer.h"
#include <tuple>
#include <iostream>
#include <iomanip>
#include <array>
#include <bitset>
#include <vector>
#include <fstream>

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
    slot_info Backgammon::get_bar_info(const PositionStruct& position)
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

    slot_info Backgammon::get_slot_info(const PositionStruct& position, unsigned char slot)
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

    void Backgammon::update_slot(PositionStruct&position, unsigned char player, unsigned char slot, bool increment)
    {
        const unsigned char shift = 55 - (slot % 12) * 5;
        const unsigned char position_ndx = slot / 12;

        auto [slot_player, num_checkers] = get_slot_info(position, slot);
        if (increment)
        {
            // check for single enemy piece.
            if (num_checkers == 1 && slot_player != player)
            // if found, this is a hit, move opponent's piece to bar.
            {
                // if found, this is a hit, move opponent's piece to bar.
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

                // clear control when no checkers left because it messes up position comparison
                if (num_checkers == 1)
                {
                    unsigned long long control_mask = ~(1ull << (shift + 4));
                    position.position[position_ndx] &= control_mask;
                }
            }
        }
    }


    void Backgammon::position_from_string(const string str_pos, BackgammonNS::PositionStruct& position)
    {
        auto player = 0u;
        unsigned long long workspace = atoi(str_pos.substr(24 * 3, 3).c_str());
        for (auto slot = 0; slot < 12; slot++)
        {
            workspace <<= 5;
            auto str_value = str_pos.substr(slot * 3, 3);
            player = str_value[0] == 'B' ? 0b10000 : 0b00000;
            auto value = atoi(str_value.substr(1, 2).c_str());
            workspace |= (player + value);
        }
        //cout << bitset<64>(workspace) << endl;
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
        //cout << bitset<64>(workspace) << endl;
        position.position[1] = workspace;
    }

    std::string Backgammon::string_from_position(const BackgammonNS::PositionStruct& position)
    {
        string pos_string;

        for (auto slot = 0u; slot < 24; slot++)
        {
            auto [player, num_checkers] = get_slot_info(position, slot);
            if (num_checkers > 0)
            {
                pos_string += player == 0 ? "W" : "B";
                if (num_checkers < 10) pos_string += "0";
                pos_string += to_string(num_checkers);
            }
            else
            {
                pos_string += "  0";
            }
        }
        auto [player_0_bar, player_1_bar] = get_bar_info(position);
        pos_string += " ";
        if (player_0_bar < 10) pos_string += " ";
        pos_string += to_string(player_0_bar);
        pos_string += " ";
        if (player_1_bar < 10) pos_string += " ";
        pos_string += to_string(player_1_bar);

        return pos_string;
    }

    void Backgammon::get_initial_position(PositionStruct& position)
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

    bool Backgammon::gen_moves_for_1_die(const unsigned int pos_ndx, const unsigned int& blocked, const unsigned char player, const unsigned int die, unsigned int move_ndx, castoff_availability can_castoff, MoveList& move_list, bool no_duplicates)
    {
        unsigned long long workspace = 0x0;
        const unsigned char opponent_test = player == 0 ? 0b10000 : 0x0;
        unsigned int blocked_ndx = 1 << 23;
        char delta = player == 0 ? die : -(char)die;
        bool expanded = false;

        auto [bar_0_count, bar_1_count] = get_bar_info(move_list.move_list[pos_ndx].result_position);
        auto bar_count = player == 0 ? bar_0_count : bar_1_count;

        // Initial position wasn't ready for castoff but was close enough that 
        // it might be after some checkers are moved.
        if (can_castoff == castoff_availability::pending)
        {
            auto starting_slot = player == 0 ? 0 : 6;
            auto ending_slot = player == 0 ? 17 : 23;
            bool can_castoff_check = true;
            for (auto slot = starting_slot; slot <= ending_slot; slot++)
            {
                auto [slot_player, num_checkers] = get_slot_info(move_list.move_list[pos_ndx].result_position, slot);
                if (slot_player == player && num_checkers > 0)
                {
                    can_castoff_check = false;
                    break;
                }
            }
            if (can_castoff_check) can_castoff = castoff_availability::available;
        }

        // Position is valid for casting off.
        if (can_castoff == castoff_availability::available)
        {
            // Check if we have a checker on the slot of the die roll.
            auto slot = player == 1 ? die - 1 : 24 - die;
            auto [slot_player, num_checkers] = get_slot_info(move_list.move_list[pos_ndx].result_position, slot);
            if (slot_player == player && num_checkers > 0)
            {
                expanded = true;
                unsigned char move = (slot << 3) + die;

                move_list.move_list[move_list.move_list_size] = move_list.move_list[pos_ndx];
                move_list.move_list[move_list.move_list_size].moves[move_ndx] = move;
                update_slot(move_list.move_list[move_list.move_list_size].result_position, player, slot, false);

                if (no_duplicates)
                {
                    auto loc = move_list.duplicate_positions.find(move_list.move_list[move_list.move_list_size].result_position);
                    if (loc == move_list.duplicate_positions.end() || loc->second != move_ndx + 1)
                    {
                        move_list.duplicate_positions[move_list.move_list[move_list.move_list_size].result_position] = move_ndx + 1;
                        if (move_list.max_sub_moves < move_ndx + 1)
                        {
                            move_list.move_list_ndx_size = 0;
                            move_list.max_sub_moves = move_ndx + 1;
                        }
                        move_list.move_list_ndx[move_list.move_list_ndx_size++] = move_list.move_list_size;
                        move_list.move_list_size++;
                    }
                }
                else
                {
                    if (move_list.max_sub_moves < move_ndx + 1)
                    {
                        move_list.move_list_ndx_size = 0;
                        move_list.max_sub_moves = move_ndx + 1;
                    }
                    move_list.move_list_ndx[move_list.move_list_ndx_size++] = move_list.move_list_size;
                    move_list.move_list_size++;
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
                    auto [slot_player, num_checkers] = get_slot_info(move_list.move_list[pos_ndx].result_position, first_slot_with_pieces);
                    if (slot_player == player && num_checkers > 0)
                    {
                        break;
                    }
                    first_slot_with_pieces += delta;
                }

                if (first_slot_with_pieces >= 0 && first_slot_with_pieces < 24)
                {
                    if ((player == 1 && first_slot_with_pieces < (int)slot) ||
                        (player == 0 && first_slot_with_pieces > (int)slot))
                    {
                        expanded = true;
                        unsigned char move = (first_slot_with_pieces << 3) + die;

                        move_list.move_list[move_list.move_list_size] = move_list.move_list[pos_ndx];
                        move_list.move_list[move_list.move_list_size].moves[move_ndx] = move;
                        update_slot(move_list.move_list[move_list.move_list_size].result_position, player, first_slot_with_pieces, false);

                        if (no_duplicates)
                        {
							auto loc = move_list.duplicate_positions.find(move_list.move_list[move_list.move_list_size].result_position);
							if (loc == move_list.duplicate_positions.end() || loc->second != move_ndx + 1)
							{
								move_list.duplicate_positions[move_list.move_list[move_list.move_list_size].result_position] = move_ndx + 1;
                                if (move_list.max_sub_moves < move_ndx + 1)
                                {
                                    move_list.move_list_ndx_size = 0;
                                    move_list.max_sub_moves = move_ndx + 1;
                                }
                                move_list.move_list_ndx[move_list.move_list_ndx_size++] = move_list.move_list_size;
                                move_list.move_list_size++;
							}
                        }
                        else
                        {
                            if (move_list.max_sub_moves < move_ndx + 1)
                            {
                                move_list.move_list_ndx_size = 0;
                                move_list.max_sub_moves = move_ndx + 1;
                            }
                            move_list.move_list_ndx[move_list.move_list_ndx_size++] = move_list.move_list_size;
                            move_list.move_list_size++;
                        }

                    }
                }
            }
        }

        if (bar_count > 0)
        {
            // Move pieces off the bar.
            char target = player == 0 ? delta - 1 : 24 + delta;
            if (target >= 0 && target < 24 && (blocked & (blocked_ndx >> target)) == 0)
            {
                expanded = true;
                //cout << "Die " << (int)die << " From Bar To " << (int)target << endl;
                unsigned char move = bar_indicator + die;

                move_list.move_list[move_list.move_list_size] = move_list.move_list[pos_ndx];
                move_list.move_list[move_list.move_list_size].moves[move_ndx] = move;
                update_slot(move_list.move_list[move_list.move_list_size].result_position, player, target, true);
                update_slot(move_list.move_list[move_list.move_list_size].result_position, player, bar_indicator, false);

                if (no_duplicates)
                {
                    auto loc = move_list.duplicate_positions.find(move_list.move_list[move_list.move_list_size].result_position);
                    if (loc == move_list.duplicate_positions.end())
                    {
                        move_list.duplicate_positions[move_list.move_list[move_list.move_list_size].result_position] = move_ndx + 1;
                        if (move_list.max_sub_moves < move_ndx + 1)
                        {
                            move_list.move_list_ndx_size = 0;
                            move_list.max_sub_moves = move_ndx + 1;
                        }
                        move_list.move_list_ndx[move_list.move_list_ndx_size++] = move_list.move_list_size;
                        move_list.move_list_size++;
                    }
                }
                else
                {
                    if (move_list.max_sub_moves < move_ndx + 1)
                    {
                        move_list.move_list_ndx_size = 0;
                        move_list.max_sub_moves = move_ndx + 1;
                    }
                    move_list.move_list_ndx[move_list.move_list_ndx_size++] = move_list.move_list_size;
                    move_list.move_list_size++;
                }
            }
        }
        else
        {
            // Normal move.
            for (auto slot = 0; slot < 24; slot++)
            {
                auto [position_player, num_checkers] = get_slot_info(move_list.move_list[pos_ndx].result_position, slot);
                if (position_player == player && num_checkers > 0)
                {
                    char target = slot + delta;
                    if (target < 0 || target >= 24) continue;
                    if (blocked & (blocked_ndx >> target)) continue;
                    expanded = true;

                    //cout << "Die " << (int)die << " From " << (int)slot << " To " << (int)target << endl;
                    unsigned char move = (slot << 3) + die;

                    move_list.move_list[move_list.move_list_size] = move_list.move_list[pos_ndx];
                    move_list.move_list[move_list.move_list_size].moves[move_ndx] = move;
                    update_slot(move_list.move_list[move_list.move_list_size].result_position, player, target, true);
                    update_slot(move_list.move_list[move_list.move_list_size].result_position, player, slot, false);

                    if (no_duplicates)
                    {
                        auto loc = move_list.duplicate_positions.find(move_list.move_list[move_list.move_list_size].result_position);
                        if (loc == move_list.duplicate_positions.end())
                        {
                            move_list.duplicate_positions[move_list.move_list[move_list.move_list_size].result_position] = move_ndx + 1;
                            if (move_list.max_sub_moves < move_ndx + 1)
                            {
                                move_list.move_list_ndx_size = 0;
                                move_list.max_sub_moves = move_ndx + 1;
                            }
                            move_list.move_list_ndx[move_list.move_list_ndx_size++] = move_list.move_list_size;
                            move_list.move_list_size++;
                        }
                    }
                    else
                    {
                        if (move_list.max_sub_moves < move_ndx + 1)
                        {
                            move_list.move_list_ndx_size = 0;
                            move_list.max_sub_moves = move_ndx + 1;
                        }
                        move_list.move_list_ndx[move_list.move_list_ndx_size++] = move_list.move_list_size;
                        move_list.move_list_size++;
                    }
                }
            }
        }
        return expanded;
    }

    void Backgammon::generate_legal_moves(const PositionStruct& position, const unsigned char player, const unsigned int roll, MoveList& move_list, bool no_duplicates)
    {
        unsigned long long workspace = position.position[0];
        unsigned int blocked = 0x0;
        unsigned int blocked_ndx = 0x1 << 12;
        const unsigned char opponent_test = player == 0 ? 0b10000 : 0x0;

        unsigned char moves_to_castoff = 0;
        auto [bar_0_count, bar_1_count] = get_bar_info(position);
        auto bar_count = player == 0 ? bar_0_count : bar_1_count;
        moves_to_castoff += (4 * bar_count);
        auto castoff_counter = player == 1 ? 1 : 2;
        auto castoff_delta = player == 1 ? -1 : 1;

        for (auto slot = 0; slot < 12; slot++)
        {
            unsigned char slot_value = (workspace & 0b1110) != 0;
            unsigned char is_opponent = (workspace & 0b10000) == opponent_test;
            blocked |= (blocked_ndx * slot_value * is_opponent);

            moves_to_castoff += (unsigned char)(castoff_counter * (workspace & 0b1111) * !is_opponent);

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
            unsigned char is_opponent = (workspace & 0b10000) == opponent_test;
            blocked |= (blocked_ndx * slot_value * is_opponent);

            moves_to_castoff += (unsigned char)(castoff_counter * (workspace & 0b1111) * !is_opponent);

            blocked_ndx <<= 1;
            workspace >>= 5;

            castoff_counter += ((slot == 5) * castoff_delta);
        }

        auto die1 = roll % 6 + 1;
        auto die2 = roll / 6 + 1;

        move_list.initialize(position);

        //auto max_sub_moves = 0;

        auto can_castoff = moves_to_castoff == 0 ? castoff_availability::available : castoff_availability::unavailable;
        if (die1 == die2)
        {
            if (moves_to_castoff > 0 && moves_to_castoff < 4)
            {
                can_castoff = castoff_availability::pending;
            }
            auto start_move_list = move_list.move_list_size;
            gen_moves_for_1_die(0, blocked, player, die1, 0, can_castoff, move_list, no_duplicates);
            auto end_move_list = move_list.move_list_size;
            for (auto turn = 0; turn < 3; turn++)
            {
                for (auto x = start_move_list; x < end_move_list; x++)
                {
                    gen_moves_for_1_die(x, blocked, player, die2, turn + 1, can_castoff, move_list, no_duplicates);
                }
                start_move_list = end_move_list;
                end_move_list = move_list.move_list_size;
            }
        }
        else
        {
            if (moves_to_castoff == 1)
            {
                can_castoff = castoff_availability::pending;
            }
            auto max_moves_die1 = 0;
            auto start_move_list = move_list.move_list_size;
            if (gen_moves_for_1_die(0, blocked, player, die1, 0, can_castoff, move_list, no_duplicates)) max_moves_die1++;
            auto end_move_list = move_list.move_list_size;
            bool expanded = false;
            for (auto x = start_move_list; x < end_move_list; x++)
            {
                expanded |= gen_moves_for_1_die(x, blocked, player, die2, 1, can_castoff, move_list, no_duplicates);
            }
            if (expanded) max_moves_die1++;

            auto max_moves_die2 = 0;
            start_move_list = move_list.move_list_size;
            if (gen_moves_for_1_die(0, blocked, player, die2, 0, can_castoff, move_list, no_duplicates)) max_moves_die2++;
            end_move_list = move_list.move_list_size;
            expanded = false;
            for (auto x = start_move_list; x < end_move_list; x++)
            {
                expanded |= gen_moves_for_1_die(x, blocked, player, die1, 1, can_castoff, move_list, no_duplicates);
            }
            if (expanded) max_moves_die2++;

            // if you can move either die but not both, you must move larger number
            if (move_list.max_sub_moves == 1)
            {
                if (max_moves_die1 > 0 && max_moves_die2 > 0)
                {
                    auto largest_die = die1 > die2 ? die1 : die2;
                    for (auto x = 0u; x < move_list.move_list_size; x++)
                    {
                        auto move = move_list.move_list[x].moves[0];
                        auto test_die = move & 0b111;
                        if (test_die != largest_die)
                        {
                            move_list.move_list[x].moves[0] = 0;
                        }
                    }
                }
            }
        }
        
        move_list.build_index();
    }

    void Backgammon::render_roll(const unsigned char roll)
    {
        auto die1 = roll % 6 + 1;
        auto die2 = roll / 6 + 1;
        cout << "(" << (int)die1 << "," << (int)die2 << ")";
    }

    void Backgammon::render_board_section(const BackgammonNS::PositionStruct& position, bool top, unsigned char casted_off)
    {
        array<unsigned int, 6> top_lines{0, 1, 2, 3, 4, 5};
        array<unsigned int, 6> bot_lines{5, 4, 3, 2, 1, 0};
        array<unsigned int, 6>* lines;

        array<unsigned int, 12> top_slots{11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0};
        array<unsigned int, 12> bot_slots{12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23};
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
                        cout << setw(2) << (int)num_checkers;
                    }
                    else
                    {
                        cout << (player == 0 ? " O" : " X");
                    }
                }
                else
                {
                    cout << " .";
                }
                switch (slot)
                {
                case 6:
                case 17:
                    cout << " |";
                    break;
                case 0:
                case 23:
                    break;
                default:
                    cout << " ";
                }
            }
            cout << " |";
            for (auto col = 0; col < 3; col++)
            {
                if (casted_off > line * 3 + col) cout << (top ? 'X' : 'O');
            }
            cout << endl;
        }
    }

    void Backgammon::render_bar_section(const BackgammonNS::PositionStruct& position, unsigned char player)
    {
        AnalyzerScan scan;
        Analyzer::scan_position(position, scan);
        const auto [player_0_bar, player_1_bar] = get_bar_info(position);
        cout << "|";
        for (auto bar = 0; bar < 8; bar++) cout << (player_0_bar > bar ? 'O' : ' ');
        cout << "      | " << fixed << setprecision(0) << setw(3) << scan.stat[1].data[AC_pip_count] << " X" << (player == 1 ? "*" : " ") << "|      ";
        for (auto bar = 0; bar < 8; bar++) cout << (player_1_bar + 1 > (8 - bar) ? 'X' : ' ');
        cout << "|" << endl;
        cout << "|";
        for (auto bar = 8; bar < 15; bar++) cout << (player_0_bar > bar ? 'O' : ' ');
        cout << "       | " << fixed << setprecision(0) << setw(3) << scan.stat[0].data[AC_pip_count] << " O" << (player == 0 ? "*" : " ") << "|       ";
        for (auto bar = 8; bar < 15; bar++) cout << (player_1_bar > (22 - bar) ? 'X' : ' ');
        cout << "|" << endl;
    }
    void Backgammon::render(const PositionStruct& position, unsigned char player, bool verbose)
    {
        const string far_numbers  = " 13 14 15 16 17 18  19 20 21 22 23 24 ";
        const string near_numbers = " 12 11 10  9  8  7   6  5  4  3  2  1 ";
        const string sep          = "+------------------+------------------+";
        const string sep2         = "+--------------+---+---+--------------+";


        array<unsigned char, 2> casted_off = { 15, 15 };
        for (auto slot = 0; slot < 24; slot++)
        {
            auto [player, num_checkers] = get_slot_info(position, slot);
            casted_off[player] -= num_checkers;
        }
        const auto [player_0_bar, player_1_bar] = get_bar_info(position);
        casted_off[0] -= player_0_bar;
        casted_off[1] -= player_1_bar;

        if (verbose)
        {
            cout << (player == 0 ? far_numbers : near_numbers) << endl;
            cout << sep << endl;
            render_board_section(position, true, casted_off[1]);
            cout << sep2 << endl;
            render_bar_section(position, player);
            cout << sep2 << endl;
            render_board_section(position, false, casted_off[0]);
            cout << sep << endl;
            cout << (player == 1 ? far_numbers : near_numbers) << endl;

            cout << "position.position[0] = 0b" << bitset<64>(position.position[0]) << ";" << endl;
            cout << "position.position[1] = 0b" << bitset<64>(position.position[1]) << ";" << endl;
        }
        cout << string_from_position(position) << endl;
    }

    void Backgammon::run_position_tests(const string filename, bool verbose, MoveList &move_list, int max_positions)
    {
        ifstream infile(filename);
        string line;
        PositionStruct position = { 0 };
        PositionStruct max_move_position;
        auto roll = 0;
        auto max_move_roll = 0;
        auto player = 0;
        auto max_move_player = 0;
        string last_move;

        auto total_positions = 0;
        auto total_moves = 0;
        auto total_errors = 0;
        auto total_warnings = 0;
        auto max_moves = 0;
        auto moves_for_this_position = 0;
        
        while (getline(infile, line))
        {
            //cout << line << endl;
            string token = line.substr(0, 4);
            string data = line.substr(4);
            if (token == "POS:")
            {
                if (!verbose)
                {
                    if (total_positions % 100 == 0)
                    {
                        cout << " " << total_positions << endl;
                    }
                    cout << ".";
                }
                if (move_list.max_sub_moves > 0)
                {
                    for (auto ndx = 0u; ndx < move_list.move_list_ndx_size; ndx++)
                    {
                        auto move = move_list.move_list[move_list.move_list_ndx[ndx]];
                        auto pos = move_list.duplicate_positions.find(move.result_position);
                        if (pos == move_list.duplicate_positions.end())
                        {
                            total_errors++;
                            cout << "MOVE GENERATED BUT NOT IN DUPLICATE POSITIONS" << endl;
                        }
                        else if (pos->second != 0)
                        {
                            total_warnings++;
                            cout << "MOVE GENERATED BUT DOES NOT EXIST IN TEST DATA" << endl;
                            render(position, player);
                            for (auto y = 0; y < 4; y++)
                            {
                                if (move.moves[y] == 0) continue;
                                auto die = move.moves[y] & 0b111;
                                auto slot = move.moves[y] >> 3;
                                if (slot == (bar_indicator >> 3)) cout << "Die " << (int)die << " From Bar " << endl;
                                else cout << "Die " << (int)die << " From " << (int)slot << endl;
                            }
                            render(move.result_position, player);
                        }
                    }
                }
                total_positions++;
                if (moves_for_this_position > max_moves)
                {
                    max_moves = moves_for_this_position;
                    max_move_position = position;
                    max_move_player = player;
                    max_move_roll = roll;
                }
                moves_for_this_position = 0;
                if (verbose) cout << "------------------------------------" << endl;
                if (verbose) cout << "Processing position... " << data << endl;
                position_from_string(data, position);
                auto test_string = string_from_position(position);
                if (test_string != data)
                {
                    cout << data << endl;
                    cout << test_string << endl;
                    return;
                }

                //render(position);
                if (verbose) cout << "------------------------------------" << endl;
            }
            else if (token == "ROL:")
            {
                if (verbose) cout << "Processing roll...     ";
                auto die1 = atoi(data.substr(0, 3).c_str());
                auto die2 = atoi(data.substr(3, 3).c_str());
                roll = (die1 - 1) * 6 + die2 - 1;
                if (verbose) cout << data << " => " << die1 << ", " << die2 << " " << roll << endl;
            }
            else if (token == "PLY:")
            {
                if (verbose) cout << "Processing player...   ";
                player = 1 - atoi(data.c_str());
                if (verbose) cout << data << " => " << player << endl;
                generate_legal_moves(position, player, roll, move_list, true);
            }
            else if (token == "RES:")
            {
                if (verbose) cout << "Processing result...   ";
                PositionStruct test_position;
                position_from_string(data, test_position);
                auto test_string = string_from_position(test_position);
                if (test_string != data)
                {
                    cout << data << endl;
                    cout << test_string << endl;
                    return;
                }
                auto pos = move_list.duplicate_positions.find(test_position);
                if (pos == move_list.duplicate_positions.end())
                {
                    total_errors++;
                    cout << "MISSING POSITION!!!" << endl;
                    render(position, player);
                    cout << last_move << endl;
                    cout << line << endl;
                    render(test_position, player);
                }
                else
                {
                    pos->second = 0;
                    if (verbose) cout << "Found" << endl;
                }
            }
            else if (token == "MOV:")
            {
                total_moves++;
                moves_for_this_position++;
                last_move = line;
            }

            if (max_positions > 0 && total_positions >= max_positions) break;

        }
        infile.close();
        cout << endl;
        cout << "total_positions          " << total_positions << endl;
        cout << "total_moves              " << total_moves << endl;
        cout << "average moves / position " << (float)total_moves / (float)total_positions << endl;

        cout << "total_errors             " << total_errors << endl;
        cout << "total_warnings           " << total_warnings << endl;
        cout << "max_moves                " << max_moves << endl;
        render(max_move_position, player);
        cout << "Player: " << max_move_player << endl;
        cout << "Roll:   " << max_move_roll << " (" << (max_move_roll / 6) + 1 << ", " << (max_move_roll % 6) + 1 << ")" << endl;
    }

    int Backgammon::get_roll_from_string(std::string s)
    {
        int roll = -1;

        if (s.size() >= 2)
        {
            auto d1 = s.substr(0, 1);
            auto die1 = atoi(d1.c_str()) - 1;
            auto d2 = s.substr(1, 1);
            auto die2 = atoi(d2.c_str()) - 1;
            roll = die1 * 6 + die2;
        }
        return roll;
    }

    std::vector<std::tuple<int, int>> Backgammon::parse_move_string(std::string s)
    {
        std::vector<std::tuple<int, int>> moves;
        string working_digit = "";
        auto d1 = -1;
        auto d2 = -1;
        auto spaces_in_a_row = 0;
        auto repeats = 1;

        for (auto c : s)
        {
            if (c == '/')
            {
                //cout << "D1: " << working_digit << " " << atoi(working_digit.c_str()) << endl;
                auto test = atoi(working_digit.c_str());
                if (test > 0) d1 = test;
                working_digit = "";
                spaces_in_a_row = 0;
                continue;
            }
            if (c == ' ')
            {
                if (spaces_in_a_row > 0) break;
                //cout << "D2: " << working_digit << " " << atoi(working_digit.c_str()) << endl;
                auto test = atoi(working_digit.c_str());
                if (test > 0) d2 = test;
                if (d1 != -1 || d2 != -1) moves.push_back(make_tuple(d1, d2));
                d1 = -1;
                d2 = -1;
                working_digit = "";
                spaces_in_a_row++;
                continue;
            }
            if (c == '(')
            {
                auto test = atoi(working_digit.c_str());
                if (test > 0) d2 = test;
                if (d1 != -1 || d2 != -1) moves.push_back(make_tuple(d1, d2));
                d1 = -1;
                d2 = -1;
                working_digit = "";
                spaces_in_a_row = 0;
                continue;
            }
            if (c == ')')
            {
                auto test = atoi(working_digit.c_str());
                if (test > 0 && moves.size() > 0)
                {
                    auto last_tuple = moves[moves.size() - 1];
                    for (auto x = 0u; x < test - 1; x++)
                    {
                        moves.push_back(last_tuple);
                    }
                }
                d1 = -1;
                d2 = -1;
                working_digit = "";
                spaces_in_a_row = 0;
                continue;
            }
            working_digit += c;
            spaces_in_a_row = 0;

        }

        return moves;
    }

    int Backgammon::get_winner(const PositionStruct& position)
    {
        auto result = 0;

        AnalyzerScan scan;
        Analyzer::scan_position(position, scan);
        
        if (scan.stat[0].data[AC_pip_count] == 0)
        {
            result = 1;
        }
        else if (scan.stat[0].data[AC_pip_count] == 0)
        {
            result = -1;
        }
        
        return result;
    }

    bool Backgammon::transform_game_log(std::string from_filename, std::string to_filename, bool verbose)
    {
        const string training_path = "C:\\GitHub\\RL\\Gammon\\training_games\\";


        ifstream infile(training_path + from_filename);
        string line;
        auto player = 0u;
        PositionStruct position = { 0 };

        while (getline(infile, line))
        {
            if (line.size() < 5) continue;

            auto check = line.substr(1, 4);
            //cout << line << endl;
            //cout << "[" << check << "]" << endl;
            if (check == "Game")
            {
                get_initial_position(position);
                if (verbose) cout << "------------------------------------------------------------------------------------------------------" << endl;
                if (verbose) cout << "-                                                                                                    -" << endl;
                if (verbose) cout << "------------------------------------------------------------------------------------------------------" << endl;
                render(position, player, verbose);
                continue;
            }

            if (line.size() < 20) continue;

            check = line.substr(3, 1);
            if (check == ")")
            {
                auto roll0 = line.substr(5, 2);
                auto play0 = line.substr(9, 30);
                auto roll1 = line.size() > 40 ? line.substr(39, 2): "";
                auto play1 = line.size() > 44 ? line.substr(43, 30): "";
                auto int_roll0 = get_roll_from_string(roll0);
                auto int_roll1 = get_roll_from_string(roll1);
                if (verbose)
                {
                    cout << "[" << roll0;
                    cout << "] [" << int_roll0;
                    cout << "] [" << roll1;
                    cout << "] [" << int_roll1;
                    cout << "] [" << play0;
                    cout << "] [" << play1;
                    cout << "]" << endl;
                }
                if (int_roll0 >= 0)
                {
                    auto moves0 = parse_move_string(play0);
                    for (auto move : moves0)
                    {
                        auto [m1, m2] = move;
                        unsigned char slot = bar_indicator;
                        if (m1 > 0)
                        {
                            slot = 24 - m1;
                        }
                        update_slot(position, 0, slot, false);
                        if (m2 > 0)
                        {
                            slot = 24 - m2;
                            update_slot(position, 0, slot, true);
                        }
                        if (verbose) cout << "(" << m1 << "," << m2 << ") ";
                    }
                    if (verbose) cout << endl;
                    render(position, 1, verbose);
                    if (!is_valid_position(position))
                    {
                        cout << endl << endl << "!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!" << endl << endl;
                        cout << line << endl;
                        render(position, 1, true);
                        cout << endl << endl << "!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!" << endl << endl;
                        break;
                    }
                }
                if (int_roll1 >= 0)
                {
                    auto moves1 = parse_move_string(play1);
                    for (auto move : moves1)
                    {
                        auto [m1, m2] = move;
                        unsigned char slot = bar_indicator;
                        if (m1 > 0)
                        {
                            slot = m1 - 1;
                        }
                        update_slot(position, 1, slot, false);
                        if (m2 > 0)
                        {
                            slot = m2 - 1;
                            update_slot(position, 1, slot, true);
                        }
                        if (verbose) cout << "(" << m1 << "," << m2 << ") ";
                    }
                    if (verbose) cout << endl;
                    render(position, 0, verbose);
                    if (!is_valid_position(position))
                    {
                        cout << endl << endl << "!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!" << endl << endl;
                        cout << line << endl;
                        render(position, 0, true);
                        cout << endl << endl << "!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!" << endl << endl;
                        break;
                    }
                }
            }
        }

        return false;
    }

    bool Backgammon::is_valid_position(PositionStruct& position)
    {
        unsigned char totals[2] = { 0, 0 };
        for (auto slot = 0u; slot < 24; slot++)
        {
            auto [player, num_checkers] = get_slot_info(position, slot);

            totals[player] += num_checkers;
            if (totals[player] > 15) return false;

        }

        auto [bar_0, bar_1] = get_bar_info(position);
        if (totals[0] + bar_0 > 15) return false;
        if (totals[1] + bar_1 > 15) return false;

        return true;
    }


}

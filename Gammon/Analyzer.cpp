#include <iostream>
#include <iomanip>
#include <bitset>
#include <array>
#include <string>
#include <map>
#include <fstream>
#include "analyzer.h"
#include "PerfTimer.h"
#include "flat_hash_map-master/bytell_hash_map.hpp"

/*
The AI will be heuristic and use the following structure.

At the top end, we attempt to chose the best strategy of these 4:
1) Priming
Primary goal is to build a perfect prime.
Need at least one opponent checker back.
Purity is important.
Timing is important.
Efficiency is important.
Lead is not important.

2) Blitzing
Need at least one opponent checker back.
Primary goal is to shut out opponent.
Purity is not important.
Timing is not important.
Efficiency is not important.
Should have at least 10 checkers in the zone.
Lead is good but not critical.

3) Racing
Contact has been broken and it is just a race to the end.
Purity is not important.
Timing is not important.
Efficiency is not important.
Lead is critical.

4) Contact
Primary goal is to maintain contact. While doing so you need to be building a prime.
Timing is very important.
Purity is important.
Timing is important.
Efficiency is important.
Lead is detrimental.

In addition there are two types of structures:
1) Prime
2) Blitz

These obviously feed into the above strategies. These can be detected by static analysis of the initial position and used to prioritize different tactics:

Breakdown of 4 possible conditions:
(You / opponent)
Priming / Priming
Split back checkers for high anchor.
    Number of blots in opponents home board
    Number of blocks in opponents home board
    Location of high anchor.
Try and make a prime.
    Raw block score
    Raw slot score
    Raw checkers in range of slot
Make points in order.
    Raw block score
    Purity
Implied
    Number of opponents blots in home board
    Number of opponents blocks in home board
    Location of high opponents anchor.

Priming / Blitzing
Never split your back anchors.
    Number of blots in opponents home board
    Number of blocks in opponents home board
Low anchors are fine.
Slot.
    Purity.
    Raw block score
    Raw slot score
    Raw checkers in range of slot
Implied
    opponents on bar
    Number of opponents blots in home board
    Number of opponents blocks in home board
    Location of high opponents anchor.

Blitzing / Priming
Attack if possible.
    opponents on bar
    Blocks in your home board.
    Number of opponents blots in home board
    Number of opponents blocks in home board
    Location of high opponents anchor.
Escape back checkers if attack is not possible.
    Number of checkers in opponents home board
Do Not Slot!
    Raw slot score

Blitzing / Blitzing
Attack if possilbe.
    opponents on bar
    Blocks in your home board.
    Number of opponents blots in home board
    Number of opponents blocks in home board
    Location of high opponents anchor.
Anchor anywhere you can.
Don't give up your anchor!
    Number of blots in opponents home board
    Number of blocks in opponents home board

Split raw home board score into:
Raw block score
Raw slot score
Raw checkers in range of slot

Consolidates to 
    Blocks in your home board
    Location of high anchor
    Location of high blot
    Number of blocks in home board
    Number of blots in home board
    Checkers on bar
    Purity
    Raw block score
    Raw checkers in range of slot
    Raw slot score

We will calculate a number of primitives for both sides and use those to choose the category and score moves.
1) Pip count - total number of moves needed to bear out.
2) Board strength - how difficult will it be for our opponent to get in if hit. Measured in pct of rolls that get in 1-4 checkers.
3) Containment - what is the average number of rolls it will take for our opponent to escape our prime if we don't move.
4) Timing - how many moves can we make before having to break our prime.
5) Safety - how likely is it for you to be hit by opponent.

We will supplement this with rollouts to determine which is the best move for a given strategy.

Next we will add a minmax search.

Next we will add alpha beta pruning.

Next we will add bad move pruning based on chosen strategy.

4 basic strategies:
*/
using namespace std;

namespace BackgammonNS
{
    static std::map<const unsigned int, std::string> stat_descriptions = {
        {AC_pip_count, "PiP"},
        {AC_total_in_the_zone, "InZn"},
        {AC_blots_in_the_zone, "BInZn"},
        {AC_stripped_in_the_zone, "SInZn"},
        {AC_triples_in_the_zone, "TInZn"},
        {AC_mountains_in_the_zone, "MInZn"},
        {AC_anchors_in_opp_board, "Anch"},
        {AC_blots_in_opp_board, "B OP"},
        {AC_checkers_on_bar, "Bar"},
        {AC_location_of_high_anchor, "H Anc"},
        {AC_location_of_high_blot, "H Blt"},
        {AC_blocks_in_home_board, "BL HB"},
        {AC_blots_in_home_board, "BT HB"},
        {AC_structure, "STR"},
        {AC_impurity, "IMP"},
        {AC_waste, "WASTE"},
        {AC_first, "First"},
        {AC_last, "Last"},
        {AC_mountains, "Mnt"},
        {AC_raw_block_value, "BL V"},
        {AC_raw_slot_value, "SL V"},
        {AC_raw_range_value, "RN V"},
        {AC_hit_pct, "HtPct"},
        {AC_hit_loss, "HtLoss"}
    };

    static ska::bytell_hash_map<unsigned short, unsigned long long> block_masks_for_rolls = {
        {36, 0b100000000000000000000000},
        {72, 0b110000000000000000000000},
        {73, 0b110000000000000000000000},
        {108, 0b111000000000000000000000},
        {110, 0b101000000000000000000000},
        {115, 0b010000000000000000000000},
        {147, 0b100100000000000000000000},
        {152, 0b011000000000000000000000},
        {184, 0b100010000000000000000000},
        {187, 0b010100000000000000000000},
        {189, 0b010100000000000000000000},
        {194, 0b001000000000000000000000},
        {221, 0b100001000000000000000000},
        {226, 0b010010000000000000000000},
        {231, 0b001100000000000000000000},
        {259, 0b010101000000000000000000},
        {263, 0b010001000000000000000000},
        {268, 0b001010000000000000000000},
        {273, 0b000100000000000000000000},
        {302, 0b001001000000000000000000},
        {305, 0b001001000000000000000000},
        {310, 0b000110000000000000000000},
        {347, 0b000101000000000000000000},
        {352, 0b000010000000000000000000},
        {389, 0b000011000000000000000000},
        {410, 0b001001001000000000000000},
        {417, 0b000100010000000000000000},
        {431, 0b000001000000000000000000},
        {532, 0b000010000100000000000000},
        {561, 0b000100010001000000000000},
        {647, 0b000001000001000000000000},
        {712, 0b000010000100001000000000},
        {863, 0b000001000001000001000000}
    };

    static MoveList hit_move_list;

    static array<unsigned long long, 24> distance_roll_table = {
        0b111111000000000000000000000000000000,
        0b110000011111000000000000000000000000,
        0b111000001000001111000000000000000000,
        0b101100010100000100000111000000000000,
        0b000110001010000010000010000011000000,
        0b000011010101001001000001000001000001,
        0b000001000010000100000000000000000000,
        0b000000010001000010000100000000000000,
        0b000000000000001001000010000000000000,
        0b000000000000000000000001000010000000,
        0b000000000000000000000000000001000000,
        0b000000000000001000000100000000000001,
        0b000000000000000000000000000000000000,
        0b000000000000000000000000000000000000,
        0b000000000000000000000000000010000000,
        0b000000000000000000000100000000000000,
        0b000000000000000000000000000000000000,
        0b000000000000000000000000000000000001,
        0b000000000000000000000000000000000000,
        0b000000000000000000000000000010000000,
        0b000000000000000000000000000000000000,
        0b000000000000000000000000000000000000,
        0b000000000000000000000000000000000000,
        0b000000000000000000000000000000000001 
    };

    static array<string, 15> blitz_prime_test_data = {
        "W02B02  0  0  0B04  0B02  0  0  0W05B05  0  0  0W03  0W05  0  0  0  0B02  0  0 U B",
        "W02  0B02  0  0B05  0B03  0  0  0W05B03  0  0  0W02  0W04  0W02  0  0B02  0  0 P B",
        "W02  0  0  0B03B03  0B02  0  0B01W03B04  0  0  0W03  0W05  0  0W02  0B02  0  0 B P",
        "W02  0  0  0  0B05  0B04  0  0B01W05B03  0  0  0W02  0W04W02  0  0  0B02  0  0 P B",
        "W02  0  0  0  0B04  0B03B02  0B01W05B03  0  0  0W02  0W04  0  0W02B02  0  0  0 B P",
        "W02  0  0  0B02B05  0B03  0  0  0W05B03  0  0  0W02  0W04W02  0  0  0B02  0  0 P B",
        "W02B02  0  0  0B05B02B01  0  0  0W04B03  0  0  0W02W02W05  0  0  0  0B02  0  0 P B",
        "  0W01  0  0B02B05B01B03  0  0  0W04B02  0  0  0W04  0W05  0  0  0  0B02  1  0 P B",
        "W02B02  0B02  0B04  0B02  0  0  0W05B03  0  0  0W03  0W03W02  0  0  0B02  0  0 P B",
        "W02  0  0B02B02B03  0B01  0  0  0W03B05W01  0  0W03  0W04W02  0  0  0B02  0  0 P P",
        "W02  0  0B02B02B04  0B02  0  0  0W03B03  0  0  0W02W02W04W02  0  0  0B02  0  0 P P",
        "W02  0  0  0  0B05  0B03  0  0B01W04B05  0  0  0W01W02W04  0  0W02  0B01  0  0 B U",
        "W02  0B02  0  0B04  0B03  0  0  0W02B04  0B01  0W01W02W04W02  0  0W02B01  0  0 B B",
        "W02  0  0  0  0B05B02B02B01  0  0W03B03  0W01  0W02  0W05W02  0  0B01B01  0  0 B P",
        "B02  0  0B02  0B03W02B03  0  0  0W03B03  0  0  0W02W02W04B01  0B01W02  0  0  0 B B"
    };

    string Analyzer::get_board_structure_desc(const BoardStructure& structure)
    {
        string result = "";

        switch (structure)
        {
        case BoardStructure::blitz:
            result = "Blitzing Structure";
            break;
        case BoardStructure::prime:
            result = "Priming Structure";
            break;
        case BoardStructure::unclear:
            result = "Undefined Structure";
            break;
        }
        return result;
    }
    short Analyzer::get_best_move_index(const PositionStruct& position, MoveList& move_list, unsigned char player, TStructVec& struct_v, bool verbose)
    {
        const int num_scores = 3;
        auto best_score = -1000.0f;
        short best_ndx = -1;
        float scores[num_scores] = {};
        AnalyzerScan scan;
        scan_position(position, scan);
        scan.render();
        auto [player_0_structure, player_1_structure] = get_board_structure(scan, struct_v, verbose);

        for (auto ndx = 0u; ndx < move_list.move_list_ndx_size; ndx++)
        {
            auto move_set = move_list.move_list[move_list.move_list_ndx[ndx]];

            scan_position(move_set.result_position, scan);
            scan.stat[AC_hit_pct].element[player] = (float)get_number_of_hits(move_set.result_position, 1 - player, hit_move_list, false) / 36.0f;

            float score = analyze(scan , player, player_0_structure, player_1_structure, verbose);
            if (verbose) {
                cout << MoveList::get_move_desc(move_set, player) << " " << score << endl;
                //scan.render();
            }
            if (score > best_score)
            {
                best_score = score;
                best_ndx = ndx;
            }
        }
        return best_ndx;
    }

    std::tuple<BoardStructure, BoardStructure> Analyzer::get_board_structure(const AnalyzerScan& scan, TStructVec& v, bool verbose)
    {
        auto [total_blitz_pct_0, total_blitz_pct_1, s0, s1] = get_board_structure_score(scan, v, verbose);

        BoardStructure board_structure_0 = total_blitz_pct_0 > 0.5f ? BoardStructure::blitz : BoardStructure::prime;
        BoardStructure board_structure_1 = total_blitz_pct_1 > 0.5f ? BoardStructure::blitz : BoardStructure::prime;
        
        return {board_structure_0, board_structure_1};
    }

    /*
[/]  0.30583319| Correct: 25 variance 0.123021  //s[player].data[slot_number++] = scan.stat[AC_impurity].element[player];
[/]  0.05395765| Correct: 21 variance 0.232195  //s[player].data[slot_number++] = scan.stat[AC_total_in_the_zone].element[player];
[/]  0.25804806| Correct: 20 variance 0.225101  //s[player].data[slot_number++] = scan.stat[AC_blocks_in_home_board].element[player];
[/]  0.63632870| Correct: 20 variance 0.351558  //s[player].data[slot_number++] = scan.stat[AC_blots_in_opp_board].element[opponent];
[/]  0.03884967| Correct: 20 variance 0.400102  //s[player].data[slot_number++] = scan.stat[AC_pip_count].element[opponent] - scan.stat[AC_pip_count].element[player];
[/]  1.31567311| Correct: 19 variance 0.246167  //s[player].data[slot_number++] = scan.stat[AC_raw_range_value].element[player];
[/]  1.31080449| Correct: 18 variance 0.382054  //s[player].data[slot_number++] = scan.stat[AC_raw_slot_value].element[player];
[/]  0.16324097| Correct: 17 variance 0.237452  //s[player].data[slot_number++] = scan.stat[AC_structure].element[player];
[/]  0.14519614| Correct: 16 variance 0.260769  //s[player].data[slot_number++] = scan.stat[AC_waste].element[player];
[-]  0.25469363| Correct: 16 variance 0.279434  //s[player].data[slot_number++] = scan.stat[AC_stripped_in_the_zone].element[player];
[/]  0.99915594| Correct: 16 variance 0.466667  //s[player].data[slot_number++] = scan.stat[AC_checkers_on_bar].element[opponent];
[/]  0.07245214| Correct: 15 variance 0.256864  //s[player].data[slot_number++] = scan.stat[AC_last].element[player];
[-]  0.46911812| Correct: 15 variance 0.265738  //s[player].data[slot_number++] = scan.stat[AC_mountains].element[player];
[-]  0.46911812| Correct: 15 variance 0.265738  //s[player].data[slot_number++] = scan.stat[AC_mountains_in_the_zone].element[player];
[ ]  0.15125528| Correct: 15 variance 0.295740  //s[player].data[slot_number++] = scan.stat[AC_raw_block_value].element[player];
[ ]  0.37421587| Correct: 15 variance 0.387581  //s[player].data[slot_number++] = scan.stat[AC_anchors_in_opp_board].element[opponent];
[ ]  0.49948177| Correct: 15 variance 0.400083  //s[player].data[slot_number++] = scan.stat[AC_blots_in_the_zone].element[player];
[ ]  0.09065428| Correct: 15 variance 0.408061  //s[player].data[slot_number++] = scan.stat[AC_first].element[player];
[ ]  0.25067779| Correct: 15 variance 0.429308  //s[player].data[slot_number++] = scan.stat[AC_triples_in_the_zone].element[player];
[ ]  0.09350595| Correct: 15 variance 0.484970  //s[player].data[slot_number++] = scan.stat[AC_location_of_high_anchor].element[opponent];
[ ]  0.00000000| Correct: 15 variance 0.500000  //s[player].data[slot_number++] = scan.stat[AC_checkers_on_bar].element[player];
[ ]  0.00000000| Correct: 15 variance 0.500000  //s[player].data[slot_number++] = scan.stat[AC_blots_in_home_board].element[player];
[ ]  0.00000000| Correct: 15 variance 0.500000  //s[player].data[slot_number++] = scan.stat[AC_hit_pct].element[player];
[ ] -0.00482754| Correct: 15 variance 0.501729  //s[player].data[slot_number++] = scan.stat[AC_location_of_high_blot].element[opponent];

    */
    std::tuple<float, float, TStructVec, TStructVec> Analyzer::get_board_structure_score(const AnalyzerScan& scan, TStructVec& v, bool verbose)
    {
        float total_blitz_pct[2] = { 0.0f, 0.0f };
        TStructVec s[2];
        for (auto player = 0; player < 2; player++)
        {
            auto opponent = 1 - player;

            auto slot_number = 0;
            s[player].data[slot_number++] = scan.stat[AC_pip_count].element[opponent] - scan.stat[AC_pip_count].element[player];
            s[player].data[slot_number++] = scan.stat[AC_total_in_the_zone].element[player];
            s[player].data[slot_number++] = scan.stat[AC_blots_in_opp_board].element[opponent];
            s[player].data[slot_number++] = scan.stat[AC_checkers_on_bar].element[opponent];
            s[player].data[slot_number++] = scan.stat[AC_blocks_in_home_board].element[player];
            s[player].data[slot_number++] = scan.stat[AC_structure].element[player];
            s[player].data[slot_number++] = scan.stat[AC_impurity].element[player];
            s[player].data[slot_number++] = scan.stat[AC_waste].element[player];
            s[player].data[slot_number++] = scan.stat[AC_last].element[player];
            s[player].data[slot_number++] = scan.stat[AC_raw_slot_value].element[player];
            s[player].data[slot_number++] = scan.stat[AC_raw_range_value].element[player];

            total_blitz_pct[player] = v.evaluate(s[player]);
        }
        if (verbose)
        {
            cout << "Blitz PCT       " << setprecision(4) << setw(12) << total_blitz_pct[0] << " " << setw(12) << total_blitz_pct[1] << endl;
        }

        return { total_blitz_pct[0], total_blitz_pct[1], s[0], s[1]};
    }



    void Analyzer::scan_position(const PositionStruct& position, AnalyzerScan& scan)
    {
        scan.clear();

        auto [player_0_bar, player_1_bar] = Backgammon::get_bar_info(position);
        scan.stat[AC_pip_count].element[0] = player_0_bar * 25;
        scan.stat[AC_pip_count].element[1] = player_1_bar * 25;

        unsigned int player_mask[2] = { 0b000000000000000000000001, 0b100000000000000000000000 };
        float total_blot_position[2] = { 0.0f, 0.0f };

        for (auto slot = 0u; slot < 24; slot++)
        {
            bool in_player_1_home_board = slot >= 0 && slot < 6;
            bool in_player_0_home_board = slot >= 18 && slot < 24;
            short player_0_position = (short)(slot + 1);
            short player_1_position = (short)(24 - slot);

            auto [slot_player, num_checkers] = Backgammon::get_slot_info(position, slot);
            auto [player_0_bar, player_1_bar] = Backgammon::get_bar_info(position);
            scan.stat[AC_checkers_on_bar].element[0] = player_0_bar;
            scan.stat[AC_checkers_on_bar].element[1] = player_1_bar;
         
            scan.stat[AC_pip_count].element[slot_player] += slot_player == 0 ? (24 - slot) * num_checkers : (slot + 1) * num_checkers;

            if (slot_player == 0 && slot > 12) {
                scan.stat[AC_total_in_the_zone].element[0] += num_checkers;
                if (num_checkers == 1) scan.stat[AC_blots_in_the_zone].element[0] += 1;
                if (num_checkers == 2) scan.stat[AC_stripped_in_the_zone].element[0] += 1;
                if (num_checkers == 3) scan.stat[AC_triples_in_the_zone].element[0] += 1;
                if (num_checkers > 3) scan.stat[AC_mountains_in_the_zone].element[0] += 1;
            }
            if (slot_player == 1 && slot < 11) {
                scan.stat[AC_total_in_the_zone].element[1] += num_checkers;
                if (num_checkers == 1) scan.stat[AC_blots_in_the_zone].element[1] += 1;
                if (num_checkers == 2) scan.stat[AC_stripped_in_the_zone].element[1] += 1;
                if (num_checkers == 3) scan.stat[AC_triples_in_the_zone].element[1] += 1;
                if (num_checkers > 3) scan.stat[AC_mountains_in_the_zone].element[1] += 1;
            }
            if (num_checkers >= 2) {
                scan.blocked_points_mask[slot_player] |= player_mask[slot_player];
                if (slot_player == 0 && in_player_0_home_board) scan.stat[AC_blocks_in_home_board].element[0]++;
                if (slot_player == 1 && in_player_1_home_board) scan.stat[AC_blocks_in_home_board].element[1]++;
                if (slot_player == 0 && in_player_1_home_board)
                {
                    scan.stat[AC_anchors_in_opp_board].element[0]++;
                    if (player_0_position > scan.stat[AC_location_of_high_anchor].element[0]) scan.stat[AC_location_of_high_anchor].element[0] = player_0_position;
                }
                if (slot_player == 1 && in_player_0_home_board)
                {
                    scan.stat[AC_anchors_in_opp_board].element[1]++;
                    if (player_1_position > scan.stat[AC_location_of_high_anchor].element[1]) scan.stat[AC_location_of_high_anchor].element[1] = player_1_position;
                }
            }
            if (num_checkers == 1) 
            {
                scan.blots_mask[slot_player] |= player_mask[slot_player];
                scan.stat[AC_hit_loss].element[slot_player] += slot_player == 0 ? (24 - slot): (slot + 1);
                if (slot_player == 0 && in_player_0_home_board) scan.stat[AC_blots_in_home_board].element[0]++;
                if (slot_player == 1 && in_player_1_home_board) scan.stat[AC_blots_in_home_board].element[1]++;
                if (slot_player == 0 && in_player_1_home_board)
                {
                    scan.stat[AC_blots_in_opp_board].element[0]++;
                    if (player_0_position > scan.stat[AC_location_of_high_blot].element[0]) scan.stat[AC_location_of_high_blot].element[0] = player_0_position;
                }
                if (slot_player == 1 && in_player_0_home_board)
                {
                    scan.stat[AC_blots_in_opp_board].element[1]++;
                    if (player_1_position > scan.stat[AC_location_of_high_blot].element[1]) scan.stat[AC_location_of_high_blot].element[1] = player_1_position;
                }
            }
            if (num_checkers == 2) scan.stripped_mask[slot_player] |= player_mask[slot_player];
            if (num_checkers == 3) scan.triples_mask[slot_player] |= player_mask[slot_player];
            if (num_checkers > 3) scan.mountains_mask[slot_player] |= player_mask[slot_player];

            player_mask[0] <<= 1;
            player_mask[1] >>= 1;
        }

        //                                         1     2     3     4     5     6     7     8     9    10    11    12    13    14    15    16
        const float raw_value_for_points[16] = { 0.1f, 0.1f, 0.3f, 0.8f, 0.9f, 1.0f, 0.7f, 0.6f, 0.3f, 0.2f, 0.2f, 0.1f, 0.3f, 0.1f, 0.1f, 0.1f};
        unsigned int mask = 0b100000000000000000000000;

        for (auto x = 0; x < 16; x++)
        {
            if (x < 10)
            {
                if ((mask & scan.triples_mask[0]) != 0) scan.stat[AC_raw_block_value].element[0] += raw_value_for_points[x] * 0.4f;
                if ((mask & scan.triples_mask[1]) != 0) scan.stat[AC_raw_block_value].element[1] += raw_value_for_points[x] * 0.4f;
                if ((mask & scan.blocked_points_mask[0]) != 0) scan.stat[AC_raw_block_value].element[0] += raw_value_for_points[x];
                if ((mask & scan.blocked_points_mask[1]) != 0) scan.stat[AC_raw_block_value].element[1] += raw_value_for_points[x];
                if ((mask & scan.blots_mask[0]) != 0) scan.stat[AC_raw_slot_value].element[0] += raw_value_for_points[x];
                if ((mask & scan.blots_mask[1]) != 0) scan.stat[AC_raw_slot_value].element[1] += raw_value_for_points[x];
            }
            else
            {
                if ((mask & scan.triples_mask[0]) != 0) scan.stat[AC_raw_range_value].element[0] += raw_value_for_points[x] * 0.4f;
                if ((mask & scan.triples_mask[1]) != 0) scan.stat[AC_raw_range_value].element[1] += raw_value_for_points[x] * 0.4f;
                if ((mask & scan.blocked_points_mask[0]) != 0) scan.stat[AC_raw_range_value].element[0] += raw_value_for_points[x];
                if ((mask & scan.blocked_points_mask[1]) != 0) scan.stat[AC_raw_range_value].element[1] += raw_value_for_points[x];
                if ((mask & scan.blots_mask[0]) != 0) scan.stat[AC_raw_range_value].element[0] += raw_value_for_points[x] * 0.4f;
                if ((mask & scan.blots_mask[1]) != 0) scan.stat[AC_raw_range_value].element[1] += raw_value_for_points[x] * 0.4f;
            }
            mask >>= 1;
        }

        mask = 0b100000000000000000000000;
        for (auto ndx = 0; ndx < 11; ndx++)
        {
            for (auto player = 0; player < 2; player++)
            {
                if ((scan.mountains_mask[player] & mask) != 0) scan.stat[AC_mountains].element[player]++;
                if ((scan.blocked_points_mask[player] & mask) != 0)
                {
                    scan.stat[AC_structure].element[player]++;
                    if (scan.stat[AC_first].element[player] < 0) scan.stat[AC_first].element[player] = ndx;
                    scan.stat[AC_last].element[player] = ndx;
                }
            }
            mask >>= 1;
        }
        scan.stat[AC_waste].element[0] = scan.stat[AC_total_in_the_zone].element[0] - scan.stat[AC_structure].element[0] * 2;
        scan.stat[AC_waste].element[1] = scan.stat[AC_total_in_the_zone].element[1] - scan.stat[AC_structure].element[1] * 2;
        scan.stat[AC_impurity].element[0] = scan.stat[AC_last].element[0] + 1 - scan.stat[AC_first].element[0] - scan.stat[AC_structure].element[0];
        scan.stat[AC_impurity].element[1] = scan.stat[AC_last].element[1] + 1 - scan.stat[AC_first].element[1] - scan.stat[AC_structure].element[1];
    }

    /*


    */
    float Analyzer::analyze(AnalyzerScan& scan, unsigned char player, const BoardStructure& player_0_structure, const BoardStructure& player_1_structure, bool verbose)
    {
        cout << "Board Structures: " << get_board_structure_desc(player_0_structure) << " " << get_board_structure_desc(player_1_structure) << endl;
        auto pip_lead = player == 0 ? (float)scan.stat[AC_pip_count].element[1] - (float)scan.stat[AC_pip_count].element[0] : (float)scan.stat[AC_pip_count].element[0] - (float)scan.stat[AC_pip_count].element[1];
        auto score = 0.0f; 
        auto opponent = 1 - player;

        auto player_board_structure = player == 0 ? player_0_structure : player_1_structure;
        auto opponent_board_structure = player == 1 ? player_0_structure : player_1_structure;
        //(float)pip_lead / 100.0f;
        //score += (float)scan.raw_block_value[player];
        //score += (float)scan.raw_slot_value[player] / 3.0f;

        AnalyzerVector mult_vec;
        mult_vec.clear();
        if (player_board_structure == BoardStructure::prime && opponent_board_structure == BoardStructure::prime)
        {
            /*
            Priming / Priming
            Split back checkers for high anchor.
                Number of blots in opponents home board
                Number of blocks in opponents home board
                Location of high anchor.
            Try and make a prime.
                Raw block score
                Raw slot score
                Raw checkers in range of slot
            Make points in order.
                Raw block score
                Purity
            Implied
                Number of opponents blots in home board
                Number of opponents blocks in home board
                Location of high opponents anchor.
            */
            auto test_total = 0.0f;
            mult_vec.stat[AC_location_of_high_anchor].element[player] = 1.0f / 5.0f;
            mult_vec.stat[AC_location_of_high_blot].element[player] = 1.0f / 15.0f;
            mult_vec.stat[AC_anchors_in_opp_board].element[player] = -1.0f;
            mult_vec.stat[AC_blots_in_opp_board].element[player] = -1.0f;

            mult_vec.stat[AC_raw_block_value].element[player] = 1.0f;
            mult_vec.stat[AC_raw_slot_value].element[player] = 1.0f / 3.0f;
            mult_vec.stat[AC_raw_range_value].element[player] = 1.0f / 3.0f;

            mult_vec.stat[AC_pip_count].element[player] = 1.0f / 16.0f;
            mult_vec.stat[AC_pip_count].element[opponent] = -1.0f / 16.0f;
            mult_vec.stat[AC_hit_pct].element[player] = -1.0f / 3.0f;

            for (auto ac = 0u; ac < AC_max_value; ac++)
            {
                test_total += mult_vec.stat[ac].element[0] * scan.stat[ac].element[0];
                test_total += mult_vec.stat[ac].element[1] * scan.stat[ac].element[1];
            }
            //test_total -= pip_lead / 16.0f;
            //test_total -= hit_pct / 3.0f;
            cout << "test_total " << test_total << endl;

            score += scan.stat[AC_location_of_high_anchor].element[player] / 5.0f;
            score += scan.stat[AC_location_of_high_blot].element[player] / 15.0f;
            score -= scan.stat[AC_anchors_in_opp_board].element[player];
            score -= scan.stat[AC_blots_in_opp_board].element[player];

            score += (float)scan.stat[AC_raw_block_value].element[player];
            score += (float)scan.stat[AC_raw_slot_value].element[player] / 3.0f;
            score += (float)scan.stat[AC_raw_range_value].element[player] / 3.0f;
            score -= pip_lead / 16.0f;
            score -= scan.stat[AC_hit_pct].element[player] / 3.0;
        }
        else if (player_board_structure == BoardStructure::prime && opponent_board_structure == BoardStructure::blitz)
        {
            /*
            Priming / Blitzing
            Never split your back anchors.
                Number of blots in opponents home board
                Number of blocks in opponents home board
            Low anchors are fine.
            Slot.
                Purity.
                Raw block score
                Raw slot score
                Raw checkers in range of slot
            Implied
                opponents on bar
                Number of opponents blots in home board
                Number of opponents blocks in home board
                Location of high opponents anchor.
            */
            score -= scan.stat[AC_blots_in_opp_board].element[player];
            
            score += (float)scan.stat[AC_raw_block_value].element[player];
            score += (float)scan.stat[AC_raw_slot_value].element[player] / 3.0f;
            score += (float)scan.stat[AC_raw_range_value].element[player] / 3.0f;
            score -= pip_lead / 16.0f;
            score -= scan.stat[AC_hit_pct].element[player] / 3.0;
        }
        else if (player_board_structure == BoardStructure::blitz && opponent_board_structure == BoardStructure::prime)
        {
            /*
            Blitzing / Priming
            Attack if possible.
                opponents on bar
                Blocks in your home board.
                Number of opponents blots in home board
                Number of opponents blocks in home board
                Location of high opponents anchor.
            Escape back checkers if attack is not possible.
                Number of checkers in opponents home board
            Do Not Slot!
                Raw slot score
            */
            score += scan.stat[AC_checkers_on_bar].element[opponent];
            score += scan.stat[AC_blocks_in_home_board].element[player];
            score -= scan.stat[AC_blots_in_opp_board].element[player] / 2.0f;
            score -= scan.stat[AC_anchors_in_opp_board].element[player] / 2.0f;
            score += pip_lead / 8.0f;
        }
        else if (player_board_structure == BoardStructure::blitz && opponent_board_structure == BoardStructure::blitz)
        {
            /*
            Blitzing / Blitzing
            Attack if possilbe.
                opponents on bar
                Blocks in your home board.
                Number of opponents blots in home board
                Number of opponents blocks in home board
                Location of high opponents anchor.
            Anchor anywhere you can.
            Don't give up your anchor!
                Number of blots in opponents home board
                Number of blocks in opponents home board
            */
            score += scan.stat[AC_checkers_on_bar].element[opponent];
            score += scan.stat[AC_blocks_in_home_board].element[player];
            score -= scan.stat[AC_blots_in_opp_board].element[player];
            score += pip_lead / 8.0f;
        }
        if (verbose)
        {
            scan.dump_stat_line(0);
            cout << endl;
            scan.dump_stat_line(1);
            cout << endl;
            mult_vec.dump_stat_line(0);
            cout << endl;
            mult_vec.dump_stat_line(1);
            cout << endl;
        }


        return score;
    }

    bool Analyzer::test_board_structure()
    {
        TStructVec v;
        v.set(0.0f);

        auto best_score = 0;
        auto best_variance = 1000.0f;
        TStructVec best_v;
        auto total = 0.0f;
        for (auto x = 0; x < 8000; x++)
        {
            total = 0.0f;
            auto correct = 0.0f;
            auto variance = 0.0f;
            for (auto& s : blitz_prime_test_data)
            {
                //cout << setw(3) << ndx ++ << ") " << s << endl;
                PositionStruct position;
                Backgammon::position_from_string(s, position);
                //Backgammon::render(position, 0);
                auto player_0_test_struct_char = s[79];
                auto player_1_test_struct_char = s[81];
                AnalyzerScan scan;
                scan_position(position, scan);
                //auto [player_0_structure, player_1_structure] = get_board_structure(scan);
                auto [total_blitz_pct_0, total_blitz_pct_1, s0, s1] = get_board_structure_score(scan, v, false);

                BoardStructure player_0_structure = total_blitz_pct_0 > 0.5f ? BoardStructure::blitz : BoardStructure::prime;
                BoardStructure player_1_structure = total_blitz_pct_1 > 0.5f ? BoardStructure::blitz : BoardStructure::prime;

                //scan.render();
                BoardStructure player_0_test_struct = player_0_test_struct_char == 'B' ? BoardStructure::blitz : BoardStructure::prime;
                BoardStructure player_1_test_struct = player_1_test_struct_char == 'B' ? BoardStructure::blitz : BoardStructure::prime;
                //cout << player_0_test_struct_char << " " << player_1_test_struct_char << endl;
                //cout << get_board_structure_desc(player_0_test_struct) << " " << get_board_structure_desc(player_1_test_struct) << endl;
                if (player_0_test_struct == player_0_structure) correct++;
                if (player_1_test_struct == player_1_structure) correct++;
                total += 2.0f;

                auto diff = player_0_test_struct == BoardStructure::blitz ? 1.0f - total_blitz_pct_0 : 0.0f - total_blitz_pct_0;
                variance += diff * diff;
                diff = player_1_test_struct == BoardStructure::blitz ? 1.0f - total_blitz_pct_1 : 0.0f - total_blitz_pct_1;
                variance += diff * diff;

                auto target = player_0_test_struct == BoardStructure::blitz ? 1.0f : 0.0f;
                v.move_towards(s0, target);
                target = player_1_test_struct == BoardStructure::blitz ? 1.0f : 0.0f;
                v.move_towards(s1, target);
            }
            if (correct > best_score)
            {
                best_score = correct;
                best_variance = variance;
                best_v = v;
            }
            else if (correct == best_score && best_variance > variance)
            {
                best_variance = variance;
                best_v = v;
            }
            //v.dump(8);
            //cout << " Correct: " << correct << " Total: " << total << " pct " << correct / total << " variance " << setprecision(6) << variance / total << endl;
        }
        best_v.dump(8);
        cout << " Correct: " << best_score << " variance " << setprecision(6) << best_variance / total << endl;
        best_v.save(brain_dir + "structure.vec");
        /*
        if impurity <= 0: P
        if impurity >= 3: B
        */
        return false;
    }

    unsigned short Analyzer::get_number_of_hits(const PositionStruct& position, unsigned char player, MoveList& move_list, bool verbose)
    {
        auto [player_0_hit, player_1_hit] = Backgammon::get_bar_info(position);
        auto player_hit = player == 0 ? player_1_hit : player_0_hit;

        if (verbose) cout << "HITS: ";
        auto total_hits = 0u;
        for (auto roll = 0u; roll < 36; roll++)
        {
            Backgammon::generate_legal_moves(position, player, roll, move_list, true);

            for (auto ndx = 0u; ndx < move_list.move_list_ndx_size; ndx++)
            {
                auto move_set = move_list.move_list[move_list.move_list_ndx[ndx]];
                auto [test_player_0_hit, test_player_1_hit] = Backgammon::get_bar_info(move_set.result_position);
                auto test_player_hit = player == 0 ? test_player_1_hit : test_player_0_hit;
                if (test_player_hit > player_hit)
                {
                    if (verbose) Backgammon::render_roll(roll);
                    total_hits++;
                    break;
                }
            }
        }
        if (verbose) cout << endl;
        if (verbose) cout << "Number of dice that hit: " << total_hits << " (" << (float)total_hits / 36.0f << ")." << endl;
        return total_hits;
    }

    unsigned short Analyzer::get_number_of_hits_fast(const PositionStruct& position, unsigned char player, AnalyzerScan& scan, bool verbose)
    {
        unsigned long long double_mask = 0b100000010000001000000100000010000001;
        unsigned short total_hits = 0u;
        auto opponent = 1 - player;

        if (scan.blots_mask[opponent] == 0) return 0;

        if (verbose) scan.render();

        auto hitters = scan.blocked_points_mask[player];
        hitters |= scan.blots_mask[player];
        if (verbose)
        {
            cout << "Hitters:  ";
            AnalyzerScan::print_mask_desc(hitters);
            cout << endl;
        }
        auto blockers = 0u;
        auto from_bl_mask = 0b1;
        auto to_bl_mask = 0b100000000000000000000000;
        for (auto bndx = 0u; bndx < 24; bndx++)
        {
            if ((scan.blocked_points_mask[opponent] & from_bl_mask) != 0)
            {
                blockers |= to_bl_mask;
            }
            from_bl_mask <<= 1;
            to_bl_mask >>= 1;
        }
        if (verbose)
        {
            cout << "Blockers: ";
            AnalyzerScan::print_mask_desc(blockers);
            cout << endl;
        }
        unsigned long blot_test_mask = 0b1;
        unsigned long long total_hit_mask = 0u;
        for (auto distance = 0; distance < 24; distance++)
        {
            if ((blot_test_mask & scan.blots_mask[opponent]) != 0)
            {
                if (verbose)cout << "Blot at position " << distance << endl;

                auto adjusted_hitters = (hitters << (distance + 1)) & 0b111111111111111111111111;
                auto adjusted_blockers = (blockers << (distance + 1)) & 0b111111111111111111111111;

                auto hit_test_ndx = 0u;
                auto distance_to_blot = 0;
                while (adjusted_hitters != 0)
                {
                    if (verbose) {
                        cout << "Adj hit   ";
                        AnalyzerScan::print_mask_desc(adjusted_hitters);
                        cout << endl;

                        cout << "Adj Blk:  ";
                        AnalyzerScan::print_mask_desc(adjusted_blockers);
                        cout << endl;

                        cout << "Dist2blt:  " << distance_to_blot << endl;
                    }
                    if ((adjusted_hitters & 0b100000000000000000000000) != 0)
                    {
                        auto hit_mask = distance_roll_table[hit_test_ndx];
                        if (verbose) {
                            cout << "          ";
                            AnalyzerScan::print_mask_desc(hit_mask);
                            cout << endl;
                        }
                        unsigned long long roll_mask = 0b100000000000000000000000000000000000;
                        for (auto roll = 0; roll < 36; roll++)
                        {
                            if ((roll_mask & hit_mask) != 0)
                            {
                                bool add_roll = true;
                                auto block_mask_for_rolls_key = distance_to_blot * 36 + roll;
                                if (verbose) cout << endl << block_mask_for_rolls_key << endl;
                                auto pos = block_masks_for_rolls.find(block_mask_for_rolls_key);
                                if (pos != block_masks_for_rolls.end())
                                {
                                    if (verbose) cout << bitset<24>(pos->second) << endl;
                                    if ((roll_mask & double_mask) == 0)
                                    {
                                        if ((pos->second & adjusted_blockers) == pos->second) add_roll = false;
                                    }
                                    else
                                    {
                                        if ((pos->second & adjusted_blockers) != 0) add_roll = false;
                                    }
                                }
                                if (verbose) Backgammon::render_roll(roll);
                                if (add_roll)
                                {
                                    total_hit_mask |= roll_mask;
                                    if (verbose) cout << "Added " << endl;
                                }
                            }
                            roll_mask >>= 1;
                        }
                        if (verbose) cout << endl;
                        //total_hit_mask |= hit_mask;
                    }
                    hit_test_ndx++;
                    adjusted_hitters <<= 1;
                    adjusted_hitters &= 0b111111111111111111111111;
                    //adjusted_blockers <<= 1;
                    //adjusted_blockers &= 0b111111111111111111111111;
                    distance_to_blot++;
                }
            }
            blot_test_mask <<= 1;
		}
		if (verbose) {
			cout << "Final:    ";
			cout << bitset<36>(total_hit_mask);
			cout << endl;
			unsigned long long roll_mask = 0b100000000000000000000000000000000000;
			for (auto roll = 0; roll < 36; roll++)
			{
				if ((roll_mask & total_hit_mask) != 0)
				{
					Backgammon::render_roll(roll);
				}
				roll_mask >>= 1;
			}
			cout << endl;
		}

        unsigned long long final_roll_mask = 0b1;
        for (auto ndx = 0; ndx < 36; ndx++)
        {
            total_hits += (final_roll_mask & total_hit_mask) != 0;
            total_hits += ((final_roll_mask & total_hit_mask) != 0) && ((final_roll_mask & double_mask) == 0);
            final_roll_mask <<= 1;
        }
        return total_hits;
    }

    bool Analyzer::test_number_of_hits(std::string filename, MoveList& move_list)
    {
        struct record {
            PositionStruct position;
            unsigned char player;
            unsigned int expected_number_of_hits;
        };
        vector<record> records;
        auto result = true;

        ifstream infile(filename);
        string line;
        auto num_tests = 0u;
        while (getline(infile, line))
        {
            //cout << line << endl;
            //cout << atoi(line.substr(78, 3).c_str()) << endl;
            //cout << atoi(line.substr(81, 3).c_str()) << endl;
            unsigned char player = atoi(line.substr(78, 3).c_str());
            auto expected_number_of_hits = atoi(line.substr(81, 3).c_str());
            PositionStruct position;
            Backgammon::position_from_string(line, position);
            auto [bar_0, bar_1] = Backgammon::get_bar_info(position);
            auto bar = player == 0 ? bar_0 : bar_1;
            if (bar > 0) continue;
            record rec;
            rec.position = position;
            rec.player = player;
            rec.expected_number_of_hits = expected_number_of_hits;
            records.push_back(rec);
        }
        infile.close();

        PerfTimer pf(true, true, true);
        pf.start();
        for (auto rec : records)
        {
            num_tests++;
            //cout << '.';
            //if (num_tests % 100 == 0) cout << endl;
            auto number_of_hits = get_number_of_hits(rec.position, rec.player, move_list, false);
            if (number_of_hits != rec.expected_number_of_hits)
            {
                cout << "ERROR!! " << number_of_hits << " " << rec.expected_number_of_hits << endl;
                Backgammon::render(rec.position, rec.player);
                result = false;
                break;
            }
        }
        pf.stop();
        pf.print();
        auto total_time = pf.GetElapsedProcessTime();

        cout << (float)num_tests * 10000000.0f / (float)pf.GetElapsedThreadTime() << endl;
        
        num_tests = 0u;
        auto total_misses = 0u;
        auto total_miscount = 0u;
        pf.start();
        for (auto rec : records)
        {
            num_tests++;
            //if (num_tests > 1000) break;

            AnalyzerScan scan;
            scan_position(rec.position, scan);
            auto number_of_hits = get_number_of_hits_fast(rec.position, rec.player, scan, false);
            if (number_of_hits != rec.expected_number_of_hits)
            {
                //cout << "ERROR!! " << number_of_hits << " " << rec.expected_number_of_hits << endl;
                //Backgammon::render(rec.position, rec.player);
                result = false;
                total_miscount += number_of_hits - rec.expected_number_of_hits;
                total_misses++;
            }
            
        }
        pf.stop();
        pf.print();
        total_time = pf.GetElapsedProcessTime();
        cout << (float)num_tests * 10000000.0f / (float)pf.GetElapsedThreadTime() << endl;
        cout << "Total misses " << total_misses << "/" << num_tests << " " << total_miscount << endl;
        return result;
    }

    void Analyzer::dump_block_mask_for_rolls()
    {
        for (auto distance = 0; distance < 24; distance++)
        {
            auto roll_mask = distance_roll_table[distance];
            auto roll_test_mask = 0b100000000000000000000000000000000000;

            for (auto roll = 0; roll < 36; roll++)
            {
                if ((roll_mask & roll_test_mask) != 0)
                {
                    auto block_mask = 0ull;
                    cout << setw(3) << distance + 1 << " ";
                    unsigned short key = distance * 36 + roll;
                    Backgammon::render_roll(roll);
                    cout << " " << setw(4) << key << " " << bitset<36>(roll_mask) << endl;
                }
                roll_test_mask >>= 1;
            }
        }
    }

    void AnalyzerScan::render()
    {
        dump_stat_header();
        cout << endl;
        dump_stat_line(0);
        cout << endl;
        dump_stat_line(1);
        cout << endl;

        cout << "Blocked Mask:        ";
        print_mask_desc(blocked_points_mask[0]);
        cout << "   ";
        print_mask_desc(blocked_points_mask[1]);
        cout << endl;
        
        cout << "Blots Mask:          ";
        print_mask_desc(blots_mask[0]);
        cout << "   ";
        print_mask_desc(blots_mask[1]);
        cout << endl;

        cout << "Stripped Mask:       ";
        print_mask_desc(stripped_mask[0]);
        cout << "   ";
        print_mask_desc(stripped_mask[1]);
        cout << endl;

        cout << "Triples Mask:        ";
        print_mask_desc(triples_mask[0]);
        cout << "   ";
        print_mask_desc(triples_mask[1]);
        cout << endl;

        cout << "Mountains Mask:      ";
        print_mask_desc(mountains_mask[0]);
        cout << "   ";
        print_mask_desc(mountains_mask[1]);
        cout << endl;
    }

    void AnalyzerScan::dump_stat_line(int player)
    {
        for (auto ac = 0u; ac < AC_max_value; ac++)
        {
            cout << fixed << setprecision(2) << setw(6) << stat[ac].element[player] << "|";
        }
    }

    void AnalyzerScan::dump_stat_header()
    {
        for (unsigned int ac = 0u; ac < AC_max_value; ac++)
        {
            cout << setw(6) << stat_descriptions[ac] << "|";
        }
    }

    void AnalyzerScan::print_mask_desc(unsigned int mask)
    {
        cout << bitset<6>(mask >> 18) << " ";
        cout << bitset<6>(mask >> 12) << " ";
        cout << bitset<6>(mask >> 6) << " ";
        cout << bitset<6>(mask) << " ";
    }

    void AnalyzerScan::clear()
    {
        for (auto x = 0u; x < 2; x++)
        {
            stat[AC_pip_count].element[x] = 0;
            stat[AC_total_in_the_zone].element[x] = 0;
            stat[AC_anchors_in_opp_board].element[x] = 0;
            stat[AC_checkers_on_bar].element[x] = 0;
            stat[AC_blots_in_opp_board].element[x] = 0;
            stat[AC_location_of_high_anchor].element[x] = -1;
            stat[AC_location_of_high_blot].element[x] = -1;
            stat[AC_blocks_in_home_board].element[x] = 0;
            stat[AC_blots_in_home_board].element[x] = 0;

            stat[AC_raw_block_value].element[x] = 0.0f;
            stat[AC_raw_slot_value].element[x] = 0.0f;
            stat[AC_raw_range_value].element[x] = 0.0f;

            stat[AC_structure].element[x] = 0;
            stat[AC_impurity].element[x] = 0;
            stat[AC_waste].element[x] = 0;
            stat[AC_first].element[x] = -1;
            stat[AC_last].element[x] = 0;
            stat[AC_mountains].element[x] = 0;
            stat[AC_hit_pct].element[x] = 0;
            stat[AC_blots_in_the_zone].element[x] = 0;
            stat[AC_stripped_in_the_zone].element[x] = 0;
            stat[AC_triples_in_the_zone].element[x] = 0;
            stat[AC_mountains_in_the_zone].element[x] = 0;
            stat[AC_hit_loss].element[x] = 0;

            blocked_points_mask[x] = 0;
            blots_mask[x] = 0;
            stripped_mask[x] = 0;
            triples_mask[x] = 0;
            mountains_mask[x] = 0;
        }
    }

    void AnalyzerVector::clear()
    {
        for (auto ac = 0u; ac < AC_max_value; ac++)
        {
            for (auto x = 0u; x < 2; x++)
            {
                stat[ac].element[x] = 0.0f;
            }
        }
    }

    void AnalyzerVector::dump_stat_line(int player)
    {
        for (auto ac = 0u; ac < AC_max_value; ac++)
        {
            cout << fixed << setprecision(2) << setw(6) << stat[ac].element[player] << "|";
        }
    }

}
#include <iostream>
#include <iomanip>
#include <bitset>
#include "analyzer.h"

/*
The AI will be heuristic and use the following structure.

At the top end, we attempt to chose the best strategy of these 4:
1) Priming - building a blocking structure on our home board.
2) Blitzing - attacking enemy pieces and trying to shut them out and run.
3) Racing - trying to get around the board without being hit and out running oponent.
4) Backgame - trying to stay back and play for a turnaround hit.

We will calculate a number of primitives for both sides and use those to choose the category and score moves.
1) Pip count - total number of moves needed to bear out.
2) Board strength - how difficult will it be for our oponent to get in if hit. Measured in pct of rolls that get in 1-4 checkers.
3) Containment - what is the average number of rolls it will take for our oponent to escape our prime if we don't move.
4) Timing - how many moves can we make before having to break our prime.
5) Safety - how likely is it for you to be hit by oponent.

We will supplement this with rollouts to determine which is the best move for a given strategy.

Next we will add a minmax search.

Next we will add alpha beta pruning.

Next we will add bad move pruning based on chosen strategy.


*/
using namespace std;

namespace BackgammonNS
{
    unsigned short Analyzer::get_best_move_index(const PositionType& position, MoveList& move_list, unsigned char player, bool display)
    {
        const int num_scores = 3;
        auto best_score = -1000.0f;
        auto best_ndx = 0;
        float scores[num_scores];

        for (auto ndx = 0u; ndx < move_list.move_list_ndx_size; ndx++)
        {
            auto move_set = move_list.move_list[move_list.move_list_ndx[ndx]];
            Backgammon::render(move_set.result_position, player);
            cout << MoveList::get_move_desc(move_set, player) << endl;
            float score = analyze(move_set.result_position, player);
        }
        return best_ndx;
    }



    void Analyzer::scan_position(const PositionType& position, AnalyzerResult& result)
    {
        result.clear();

        auto [player_0_bar, player_1_bar] = Backgammon::get_bar_info(position);
        result.pip_count[0] = player_0_bar * 25;
        result.pip_count[1] = player_1_bar * 25;

        unsigned int player_mask[2] = { 0b000000000000000000000001, 0b100000000000000000000000 };

        for (auto slot = 0u; slot < 24; slot++)
        {
            auto [slot_player, num_checkers] = Backgammon::get_slot_info(position, slot);
         
            result.pip_count[slot_player] += slot_player == 0 ? (24 - slot) * num_checkers : (slot + 1) * num_checkers;
            if (slot_player == 0 && slot > 12) result.in_the_zone[0] += num_checkers;
            if (slot_player == 1 && slot < 11) result.in_the_zone[1] += num_checkers;

            if (num_checkers >= 2) result.blocked_points[slot_player] |= player_mask[slot_player];
            if (num_checkers == 1) result.blots[slot_player] |= player_mask[slot_player];
            if (num_checkers > 3) result.mountains[slot_player] |= player_mask[slot_player];
            if (num_checkers == 3) result.triples[slot_player] |= player_mask[slot_player];
            
            player_mask[0] <<= 1;
            player_mask[1] >>= 1;
        }
    }

    float Analyzer::analyze(const PositionType& position, unsigned char player)
    {
        AnalyzerResult result;
        scan_position(position, result);
        result.render();

        auto pip_lead = player == 0 ? (float)result.pip_count[1] - (float)result.pip_count[0] : (float)result.pip_count[0] - (float)result.pip_count[1];
        auto score = (float)pip_lead / 100.0f;
        
        return score / 2.0f;
    }

    void AnalyzerResult::render()
    {
        cout << "Pip Count:      " << setw(4) << pip_count[0] << " " << setw(4) << pip_count[1] << endl;
        cout << "In the Zone:    " << setw(4) << in_the_zone[0] << " " << setw(4) << in_the_zone[1] << endl;

        cout << "Blocked:        ";
        print_mask_desc(blocked_points[0]);
        cout << "   ";
        print_mask_desc(blocked_points[1]);
        cout << endl;

        cout << "Blots:          ";
        print_mask_desc(blots[0]);
        cout << "   ";
        print_mask_desc(blots[1]);
        cout << endl;

        cout << "Mountains:      ";
        print_mask_desc(mountains[0]);
        cout << "   ";
        print_mask_desc(mountains[1]);
        cout << endl;

        cout << "Triples:        ";
        print_mask_desc(triples[0]);
        cout << "   ";
        print_mask_desc(triples[1]);
        cout << endl;
    }

    void AnalyzerResult::print_mask_desc(unsigned int mask)
    {
        cout << bitset<6>(mask >> 18) << " ";
        cout << bitset<6>(mask >> 12) << " ";
        cout << bitset<6>(mask >> 6) << " ";
        cout << bitset<6>(mask) << " ";
    }

    void AnalyzerResult::clear()
    {
        for (auto x = 0u; x < 2; x++)
        {
            pip_count[x] = 0;
            in_the_zone[x] = 0;
            blocked_points[x] = 0;
            blots[x] = 0;
            mountains[x] = 0;
            triples[x] = 0;
        }
    }

}
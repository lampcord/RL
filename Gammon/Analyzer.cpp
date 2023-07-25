#include <iostream>
#include <iomanip>
#include <bitset>
#include "analyzer.h"

/*
The AI will be heuristic and use the following structure.

At the top end, we attempt to chose the best strategy of these 4:
1) Priming
Primary goal is to build a perfect prime.
Need at least one oponent checker back.
Purity is important.
Timing is important.
Efficiency is important.
Lead is not important.

2) Blitzing
Need at least one oponent checker back.
Primary goal is to shut out oponent.
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

Breakdown of 4 possible conditions:
(You / Oponent)
Priming / Priming
Split back checkers for high anchor.
Try and make a prime.
Make points in order.

Priming / Blitzing
Never split your back anchors.
Low anchors are fine.
Slot.

Blitzing / Priming
Attack if possible.
Escape back checkers if attack is not possible.
Do Not Slot!

Blitzing / Blitzing
Attack if possilbe.
Anchor anywhere you can.
Don't give up your anchor!

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

4 basic strategies:
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

    /*
    Te 12 rules:
    [ ] Break the mountain.
    [ ] Keep at least 3 checkers on the mid-point.
    [ ] To double hit is tiger play (weak tiger / strong tiger)
    [ ] Attacking with 8 checkers is weak.
    [ ] Attacking with 10 checkers is strong.
    [ ] Split against the stripped 8 point.
    [ ] Split against a prime.
    [ ] Never split facing a blitzing structure.
    [ ] Hit and split.
    */
    float Analyzer::analyze(const PositionType& position, unsigned char player)
    {
        AnalyzerResult result;
        scan_position(position, result);

        auto pip_lead = player == 0 ? (float)result.pip_count[1] - (float)result.pip_count[0] : (float)result.pip_count[0] - (float)result.pip_count[1];
        auto score = (float)pip_lead / 100.0f;
        
        //[] The most important point is the 5 point.
        //[] Make an outfield point.
        //[] Fight for a good point.
        const float raw_value_for_points[11] = { 0.1f, 0.1f, 0.3f, 0.8f, 0.9f, 1.0f, 0.7f, 0.6f, 0.3f, 0.2f, 0.2f };
        unsigned int mask = 0b100000000000000000000000;
        
        for (auto x = 0; x < 11; x++)
        {
            if ((mask & result.blocked_points[0]) != 0) result.raw_mask_value[0] += raw_value_for_points[x];
            if ((mask & result.blocked_points[1]) != 0) result.raw_mask_value[1] += raw_value_for_points[x];
            if ((mask & result.blots[0]) != 0) result.raw_mask_value[0] += raw_value_for_points[x] / 3.0f;
            if ((mask & result.blots[1]) != 0) result.raw_mask_value[1] += raw_value_for_points[x] / 3.0f;
            mask >>= 1;
        }


        result.render();

        return score / 2.0f;
    }

    void AnalyzerResult::render()
    {
        cout << "Pip Count:      " << setw(4) << pip_count[0] << " " << setw(4) << pip_count[1] << endl;
        cout << "In the Zone:    " << setw(4) << in_the_zone[0] << " " << setw(4) << in_the_zone[1] << endl;
        cout << "Raw Mask Value: " << setw(4) << raw_mask_value[0] << " " << setw(4) << raw_mask_value[1] << endl;

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
            raw_mask_value[x] = 0.0f;
            blocked_points[x] = 0;
            blots[x] = 0;
            mountains[x] = 0;
            triples[x] = 0;
        }
    }

}
#include <iostream>
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
    tuple<unsigned int, unsigned int> Analyzer::get_pip_count(const PositionType& position)
    {
        unsigned int player_total[2] = { 0, 0 };

        auto [player_0_bar, player_1_bar] = Backgammon::get_bar_info(position);
        player_total[0] += player_0_bar * 25;
        player_total[1] += player_1_bar * 25;

        for (auto slot = 0u; slot < 24; slot++)
        {
            auto [slot_player, num_checkers] = Backgammon::get_slot_info(position, slot);
            if (num_checkers == 0) continue;
            player_total[slot_player] += slot_player == 0 ? (24 - slot) * num_checkers : (slot + 1) * num_checkers;
        }
        return tuple<unsigned int, unsigned int>(player_total[0], player_total[1]);
    }

    float Analyzer::analyze(const PositionType& position)
    {
        auto [player_0_pip_count, player_1_pip_count] = get_pip_count(position);
        cout << "Player 0 pip: " << player_0_pip_count << " Player 1 pip: " << player_1_pip_count << endl;
        return 0.0f;
    }

}
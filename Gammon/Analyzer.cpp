#include <iostream>
#include <iomanip>
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
    void Analyzer::scan_position(const PositionType& position, AnalyzerResult& result)
    {
        result.clear();

        auto [player_0_bar, player_1_bar] = Backgammon::get_bar_info(position);
        result.pip_count[0] = player_0_bar * 25;
        result.pip_count[1] = player_1_bar * 25;

        for (auto slot = 0u; slot < 24; slot++)
        {
            auto [slot_player, num_checkers] = Backgammon::get_slot_info(position, slot);
            if (num_checkers == 0) continue;
         
            // pip count
            result.pip_count[slot_player] += slot_player == 0 ? (24 - slot) * num_checkers : (slot + 1) * num_checkers;

            // board strength (number of blocks in your home board)
            if (slot >= 18 && slot < 24 && slot_player == 0 && num_checkers > 1) result.board_strength[0]++;
            if (slot >= 0 && slot < 6 && slot_player == 1 && num_checkers > 1) result.board_strength[1]++;

        }
    }

    float Analyzer::analyze(const PositionType& position, unsigned char player)
    {
        AnalyzerResult result;
        scan_position(position, result);

        auto pip_lead = player == 0 ? (float)result.pip_count[1] - (float)result.pip_count[0] : (float)result.pip_count[0] - (float)result.pip_count[1];
        auto score = (float)pip_lead / 100.0f;
        
        auto player_0_board_score = (float)(result.board_strength[0] * result.board_strength[0]) / 36.0f;
        auto player_1_board_score = (float)(result.board_strength[1] * result.board_strength[1]) / 36.0f;
        score += player == 0 ? player_0_board_score - player_1_board_score : player_1_board_score - player_0_board_score;

        return score / 2.0f;
    }

    void AnalyzerResult::render()
    {
        cout << "Pip Count:      " << setw(4) << pip_count[0] << " " << setw(4) << pip_count[1] << endl;
        cout << "Board Strength: " << setw(4) << board_strength[0] << " " << setw(4) << board_strength[1] << endl;
    }

    void AnalyzerResult::clear()
    {
        for (auto x = 0u; x < 2; x++)
        {
            pip_count[0] = 0;
            board_strength[0] = 0;
        }
    }

}
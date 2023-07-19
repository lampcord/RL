#include <iostream>
#include "Analyzer.h"

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
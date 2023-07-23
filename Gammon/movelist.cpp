#include "movelist.h"
#include <optional>
#include <iostream>
#include <iomanip>
#include <bitset>

using namespace std;

namespace BackgammonNS
{
    void MoveList::dump_moves(const unsigned char& player)
    {
        auto duplicates = 0;
        auto total_valid = 0;
        vector<tuple<string, PositionStruct>> rolls;
        for (auto x = 0u; x < move_list_size; x++)
        {
            bool valid = (max_sub_moves > 0 && move_list[x].moves[max_sub_moves - 1] != 0);
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
                rolls.push_back({ roll_desc, move_list[x].result_position });
                Backgammon::render(move_list[x].result_position, 1 - player);
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
            cout << setw(40) << get<0>(s);
            cout << " " << bitset<64>(get<1>(s).position[0]);
            cout << " " << bitset<64>(get<1>(s).position[1]);
            cout << endl;
        }
        cout << "Total Moves Generated: " << move_list_size << endl;
        cout << "Total Duplicates: " << duplicates << endl;
        cout << "Total Valid: " << total_valid << endl;

        rolls.clear();
        for (auto x = 0u; x < move_list_ndx_size; x++)
        {
            string roll_desc = "";
            for (auto y = 0; y < 4; y++)
            {
                if (move_list[move_list_ndx[x]].moves[y] == 0) continue;
                auto die = move_list[move_list_ndx[x]].moves[y] & 0b111;
                auto slot = move_list[move_list_ndx[x]].moves[y] >> 3;
                if (slot == (bar_indicator >> 3)) cout << "Die " << (int)die << " From Bar " << endl;
                roll_desc += to_string(slot);
                roll_desc += " to ";
                roll_desc += to_string(player == 0 ? slot + die : slot - die);
                roll_desc += ", ";
            }
            rolls.push_back({ roll_desc, move_list[move_list_ndx[x]].result_position });
        }
        for (auto s : rolls)
        {
            cout << setw(40) << get<0>(s);
            cout << " " << bitset<64>(get<1>(s).position[0]);
            cout << " " << bitset<64>(get<1>(s).position[1]);
            cout << endl;
        }

    }

    void MoveList::build_index()
    {
        move_list_ndx_size = 0;

        auto ndx = 0u;
        while (ndx >= 0 && ndx < move_list_size && max_sub_moves > 0)
        {
            if (move_list[ndx].moves[max_sub_moves - 1] != 0)
            {
                move_list_ndx[move_list_ndx_size++] = ndx;
            }
            ndx++;
        }
    }

    string MoveList::get_move_desc(MoveStruct& move_set, unsigned char player)
    {
        string description;

        for (auto y = 0u; y < 4; y++)
        {
            auto move = move_set.moves[y];
            if (move == 0) break;
            auto slot = (move & 0b11111000) >> 3;
            auto display_slot = player == 0 ? 24 - slot : slot + 1;
            auto die = (move & 0b111);
            auto slot_desc = slot == (bar_indicator >> 3) ? "bar" : to_string(display_slot);
            description += "Moved a ";
            description += to_string(die);
            description += " from ";
            description += slot_desc;
            description += ", ";
        }

        return description;
    }
}
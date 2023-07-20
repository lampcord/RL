#include "movelist.h"
#include <optional>
#include <iostream>
#include <iomanip>
#include <bitset>

using namespace std;

namespace BackgammonNS
{
    optional<MoveStruct> MoveList::get_legal_move(unsigned int& ndx)
    {
        auto result = optional<MoveStruct>();

        while (ndx >= 0 && ndx < move_list_size && max_sub_moves > 0)
        {
            // only return moves with maximum number of submoves
            if (move_list[ndx].moves[max_sub_moves - 1] != 0)
            {
                result = move_list[ndx++];
                break;
            }
            ndx++;
        }

        return result;
    }

    unsigned int MoveList::get_number_of_moves()
    {
        unsigned int num_moves = 0;

        for (auto ndx = 0u; ndx < move_list_size && max_sub_moves > 0; ndx++)
        {
            if (move_list[ndx].moves[max_sub_moves - 1] != 0)
            {
                num_moves++;
            }
        }

        return num_moves;
    }

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
    }

}
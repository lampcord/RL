#include <iostream>
#include <iomanip>
#include <bitset>
#include <array>
#include <string>
#include <map>
#include <fstream>
#include "analyzer.h"
#include "PerfTimer.h"

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

In addition there are two types of structures:
1) Prime
2) Blitz

These obviously feed into the above strategies. These can be detected by static analysis of the initial position and used to prioritize different tactics:

Breakdown of 4 possible conditions:
(You / Oponent)
Priming / Priming
Split back checkers for high anchor.
    Number of blots in oponents home board
    Number of blocks in oponents home board
    Location of high anchor.
Try and make a prime.
    Raw block score
    Raw slot score
    Raw checkers in range of slot
Make points in order.
    Raw block score
    Purity
Implied
    Number of oponents blots in home board
    Number of oponents blocks in home board
    Location of high oponents anchor.

Priming / Blitzing
Never split your back anchors.
    Number of blots in oponents home board
    Number of blocks in oponents home board
Low anchors are fine.
Slot.
    Purity.
    Raw block score
    Raw slot score
    Raw checkers in range of slot
Implied
    Oponents on bar
    Number of oponents blots in home board
    Number of oponents blocks in home board
    Location of high oponents anchor.

Blitzing / Priming
Attack if possible.
    Oponents on bar
    Blocks in your home board.
    Number of oponents blots in home board
    Number of oponents blocks in home board
    Location of high oponents anchor.
Escape back checkers if attack is not possible.
    Number of checkers in oponents home board
Do Not Slot!
    Raw slot score

Blitzing / Blitzing
Attack if possilbe.
    Oponents on bar
    Blocks in your home board.
    Number of oponents blots in home board
    Number of oponents blocks in home board
    Location of high oponents anchor.
Anchor anywhere you can.
Don't give up your anchor!
    Number of blots in oponents home board
    Number of blocks in oponents home board

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
    static MoveList hit_move_list;

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
        return string();
    }
    unsigned short Analyzer::get_best_move_index(const PositionStruct& position, MoveList& move_list, unsigned char player, bool verbose)
    {
        const int num_scores = 3;
        auto best_score = -1000.0f;
        auto best_ndx = 0;
        float scores[num_scores] = {};
        AnalyzerScan scan;
        scan_position(position, scan);
        auto [player_0_structure, player_1_structure] = get_board_structure(scan, verbose);

        for (auto ndx = 0u; ndx < move_list.move_list_ndx_size; ndx++)
        {
            auto move_set = move_list.move_list[move_list.move_list_ndx[ndx]];

            scan_position(move_set.result_position, scan);
            scan.number_of_hits = get_number_of_rolls_that_hit(move_set.result_position, 1 - player, hit_move_list, false);
            float score = analyze(scan , player, player_0_structure, player_1_structure);
            if (verbose) {
                cout << MoveList::get_move_desc(move_set, player) << " " << score << endl;
                scan.render();
            }
            if (score > best_score)
            {
                best_score = score;
                best_ndx = ndx;
            }
        }
        return best_ndx;
    }

    std::tuple<BoardStructure, BoardStructure> Analyzer::get_board_structure(const AnalyzerScan& scan, bool verbose)
    {
        float total_impurity_pct[2] = { 0.0f, 0.0f };
        float total_first_pct[2] = { 0.0f, 0.0f };
        float total_in_the_zone_pct[2] = { 0.0f, 0.0f };
        float total_lead_pct[2] = { 0.0f, 0.0f };
        float total_blitz_pct[2] = { 0.0f, 0.0f };

        for (auto player = 0; player < 2; player++)
        {
            if (scan.impurity[player] == 0)
            {
                total_impurity_pct[player] += 0.0f;
            }
            else if (scan.impurity[player] == 1)
            {
                total_impurity_pct[player] += 0.333f;
            }
            else if (scan.impurity[player] == 2)
            {
                total_impurity_pct[player] += 0.667f;
            }
            else if (scan.impurity[player] >= 3)
            {
                total_impurity_pct[player] += 1.0f;
            }

            if (scan.first[player] <= 2)
            {
                total_first_pct[player] += 1.0f;
            }
            else
            {
                total_first_pct[player] += 0.0f;
            }

            if (scan.in_the_zone[player] <= 8)
            {
                total_in_the_zone_pct[player] += 0.285714f;
            }
            else if (scan.in_the_zone[player] == 9)
            {
                total_in_the_zone_pct[player] += 0.4f;
            }
            else if (scan.in_the_zone[player] == 10)
            {
                total_in_the_zone_pct[player] += 0.642857f;
            }
            else if (scan.in_the_zone[player] >= 11)
            {
                total_in_the_zone_pct[player] += 1.0f;
            }

            auto lead = scan.pip_count[1 - player] - scan.pip_count[player];
            if (lead >= 12)
            {
                total_lead_pct[player] += 1.0f;
            }
            else if (lead <= -12)
            {
                total_lead_pct[player] += 0.0f;
            }
            else
            {
                total_lead_pct[player] += 0.5f;
            }

            total_blitz_pct[player] = (total_impurity_pct[player] + total_first_pct[player] + total_in_the_zone_pct[player] + total_lead_pct[player]) / 4.0f;
        }
        if (verbose)
        {
            cout << "Impurity PCT    " << setw(12) << total_impurity_pct[0] << " " << setw(12) << total_impurity_pct[1] << endl;
            cout << "First PCT       " << setw(12) << total_first_pct[0] << " " << setw(12) << total_first_pct[1] << endl;
            cout << "In The Zone PCT " << setw(12) << total_in_the_zone_pct[0] << " " << setw(12) << total_in_the_zone_pct[1] << endl;
            cout << "Lead PCT        " << setw(12) << total_lead_pct[0] << " " << setw(12) << total_lead_pct[1] << endl;
            cout << "Blitz PCT       " << setw(12) << total_blitz_pct[0] << " " << setw(12) << total_blitz_pct[1] << endl;
        }

        BoardStructure board_structure_0 = total_blitz_pct[0] > 0.5f ? BoardStructure::blitz : BoardStructure::prime;
        BoardStructure board_structure_1 = total_blitz_pct[1] > 0.5f ? BoardStructure::blitz : BoardStructure::prime;
        
        return {board_structure_0, board_structure_1};
    }



    void Analyzer::scan_position(const PositionStruct& position, AnalyzerScan& scan)
    {
        scan.clear();

        auto [player_0_bar, player_1_bar] = Backgammon::get_bar_info(position);
        scan.pip_count[0] = player_0_bar * 25;
        scan.pip_count[1] = player_1_bar * 25;

        unsigned int player_mask[2] = { 0b000000000000000000000001, 0b100000000000000000000000 };

        for (auto slot = 0u; slot < 24; slot++)
        {
            auto [slot_player, num_checkers] = Backgammon::get_slot_info(position, slot);
         
            scan.pip_count[slot_player] += slot_player == 0 ? (24 - slot) * num_checkers : (slot + 1) * num_checkers;
            if (slot_player == 0 && slot > 12) scan.in_the_zone[0] += num_checkers;
            if (slot_player == 1 && slot < 11) scan.in_the_zone[1] += num_checkers;

            if (num_checkers >= 2) scan.blocked_points_mask[slot_player] |= player_mask[slot_player];
            if (num_checkers == 1) scan.blots_mask[slot_player] |= player_mask[slot_player];
            if (num_checkers > 3) scan.mountains_mask[slot_player] |= player_mask[slot_player];
            if (num_checkers == 3) scan.triples_mask[slot_player] |= player_mask[slot_player];
            
            player_mask[0] <<= 1;
            player_mask[1] >>= 1;
        }

        const float raw_value_for_points[11] = { 0.1f, 0.1f, 0.3f, 0.8f, 0.9f, 1.0f, 0.7f, 0.6f, 0.3f, 0.2f, 0.2f };
        unsigned int mask = 0b100000000000000000000000;

        for (auto x = 0; x < 11; x++)
        {
            if ((mask & scan.blocked_points_mask[0]) != 0) scan.raw_mask_value[0] += raw_value_for_points[x];
            if ((mask & scan.blocked_points_mask[1]) != 0) scan.raw_mask_value[1] += raw_value_for_points[x];
            if ((mask & scan.blots_mask[0]) != 0) scan.raw_mask_value[0] += raw_value_for_points[x] / 3.0f;
            if ((mask & scan.blots_mask[1]) != 0) scan.raw_mask_value[1] += raw_value_for_points[x] / 3.0f;
            mask >>= 1;
        }

        mask = 0b100000000000000000000000;
        for (auto ndx = 0; ndx < 11; ndx++)
        {
            for (auto player = 0; player < 2; player++)
            {
                if ((scan.mountains_mask[player] & mask) != 0) scan.mountains[player]++;
                if ((scan.blocked_points_mask[player] & mask) != 0)
                {
                    scan.structure[player]++;
                    if (scan.first[player] < 0) scan.first[player] = ndx;
                    scan.last[player] = ndx;
                }
            }
            mask >>= 1;
        }
        scan.waste[0] = scan.in_the_zone[0] - scan.structure[0] * 2;
        scan.waste[1] = scan.in_the_zone[1] - scan.structure[1] * 2;
        scan.impurity[0] = scan.last[0] + 1 - scan.first[0] - scan.structure[0];
        scan.impurity[1] = scan.last[1] + 1 - scan.first[1] - scan.structure[1];

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
    float Analyzer::analyze(AnalyzerScan& scan, unsigned char player, const BoardStructure& player_0_structure, const BoardStructure& player_1_structure)
    {
        auto pip_lead = player == 0 ? (float)scan.pip_count[1] - (float)scan.pip_count[0] : (float)scan.pip_count[0] - (float)scan.pip_count[1];
        auto score = (float)pip_lead / 100.0f;
        score += (float)scan.raw_mask_value[player];

        score -= (float)scan.number_of_hits / 36.0f;

        return score / 2.0f;
    }

    bool Analyzer::test_board_structure()
    {
        map<int, vector<char>> chart_structure;
        map<int, vector<char>> chart_impurity;
        map<int, vector<char>> chart_waste;
        map<int, vector<char>> chart_first;
        map<int, vector<char>> chart_in_the_zone;
        map<int, vector<char>> chart_lead;
        map<int, vector<char>> chart_mountains;

        auto ndx = 0;
        for (auto &s : blitz_prime_test_data)
        {
            cout << setw(3) << ndx ++ << ") " << s << endl;
            PositionStruct position;
            Backgammon::position_from_string(s, position);
            Backgammon::render(position, 0);
            auto player_0_test_struct = s[79];
            auto player_1_test_struct = s[81];
            AnalyzerScan scan;
            scan_position(position, scan);
            auto [player_0_structure, player_1_structure] = get_board_structure(scan);

            chart_structure[scan.structure[0]].push_back(player_0_test_struct);
            chart_waste[scan.waste[0]].push_back(player_0_test_struct);
            chart_impurity[scan.impurity[0]].push_back(player_0_test_struct);
            chart_first[scan.first[0]].push_back(player_0_test_struct);
            chart_in_the_zone[scan.in_the_zone[0]].push_back(player_0_test_struct);
            chart_mountains[scan.mountains[0]].push_back(player_0_test_struct);
            chart_lead[scan.pip_count[1] - scan.pip_count[0]].push_back(player_0_test_struct);
            
            chart_structure[scan.structure[1]].push_back(player_1_test_struct);
            chart_waste[scan.waste[1]].push_back(player_1_test_struct);
            chart_impurity[scan.impurity[1]].push_back(player_1_test_struct);
            chart_first[scan.first[1]].push_back(player_1_test_struct);
            chart_in_the_zone[scan.in_the_zone[1]].push_back(player_1_test_struct);
            chart_mountains[scan.mountains[1]].push_back(player_1_test_struct);
            chart_lead[scan.pip_count[0] - scan.pip_count[1]].push_back(player_1_test_struct);

            scan.render();
            cout << player_0_test_struct << " " << player_1_test_struct << endl;

        }
        dump_chart("Structure", chart_structure);
        dump_chart("Impurity", chart_impurity);
        dump_chart("Waste", chart_waste);
        dump_chart("First", chart_first);
        dump_chart("In The Zone", chart_in_the_zone);
        dump_chart("Lead", chart_lead);
        dump_chart("Mountains", chart_mountains);

        /*
        if impurity <= 0: P
        if impurity >= 3: B
        */
        return false;
    }

    unsigned short Analyzer::get_number_of_rolls_that_hit(const PositionStruct& position, unsigned char player, MoveList& move_list, bool verbose)
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

    bool Analyzer::test_number_of_rolls_that_hit(std::string filename, MoveList& move_list)
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
            auto number_of_hits = get_number_of_rolls_that_hit(rec.position, rec.player, move_list, false);
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
        
        return result;
    }

    void Analyzer::dump_chart(string desc, std::map<int, std::vector<char>>& chart_structure)
    {
        cout << desc << endl;
        for (auto &p : chart_structure)
        {
            float total_b = 0.0f;
            float total_p = 0.0f;

            cout << p.first << " => ";
            for (auto v : p.second) {
                if (v == 'B') total_b++;
                if (v == 'P') total_p++;
                cout << v;
            }
            cout << " %B " << total_b/ (total_b + total_p);
            cout << endl;
        }
    }

    void AnalyzerScan::render()
    {
        cout << "Pip Count:      " << setw(4) << pip_count[0] << " " << setw(4) << pip_count[1] << endl;
        cout << "In the Zone:    " << setw(4) << in_the_zone[0] << " " << setw(4) << in_the_zone[1] << endl;
        cout << "Raw Mask Value: " << setw(4) << raw_mask_value[0] << " " << setw(4) << raw_mask_value[1] << endl;
        cout << "Structure:      " << setw(4) << structure[0] << " " << setw(4) << structure[1] << endl;
        cout << "Impurity:       " << setw(4) << impurity[0] << " " << setw(4) << impurity[1] << endl;
        cout << "Waste:          " << setw(4) << waste[0] << " " << setw(4) << waste[1] << endl;
        cout << "First:          " << setw(4) << first[0] << " " << setw(4) << first[1] << endl;
        cout << "Last:           " << setw(4) << last[0] << " " << setw(4) << last[1] << endl;
        cout << "Mountains:      " << setw(4) << mountains[0] << " " << setw(4) << mountains[1] << endl;
        cout << "Number of Hits  " << setw(4) << number_of_hits << endl;
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

        cout << "Mountains Mask:      ";
        print_mask_desc(mountains_mask[0]);
        cout << "   ";
        print_mask_desc(mountains_mask[1]);
        cout << endl;

        cout << "Triples Mask:        ";
        print_mask_desc(triples_mask[0]);
        cout << "   ";
        print_mask_desc(triples_mask[1]);
        cout << endl;
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
            pip_count[x] = 0;
            in_the_zone[x] = 0;
            raw_mask_value[x] = 0.0f;
            structure[x] = 0;
            impurity[x] = 0;
            waste[x] = 0;
            first[x] = -1;
            last[x] = 0;
            mountains[x] = 0;
            blocked_points_mask[x] = 0;
            blots_mask[x] = 0;
            mountains_mask[x] = 0;
            triples_mask[x] = 0;
        }
    }

}
#include "pch.h"
#include "C4.h"
#include "squirrel3.h"
#include <iostream>
#include <random>
#include <iomanip>
//#include <map>
#include <unordered_map>
#include <fstream>
#include <filesystem>
#include <algorithm>

using namespace std;

namespace C4
{
    struct record_tuple {
        float visits;
        float wins;
    };
    static unsigned int hits = 0;
    static unsigned int misses = 0;

    const unsigned int no_memory = 0;
    const unsigned int score_mode = 1;
    const unsigned int learn_mode = 2;
    static unsigned int play_mode = no_memory;

    static unordered_map<unsigned long long, record_tuple> recall_memory_learn;
    static unordered_map<unsigned long long, record_tuple> recall_memory_saturated;
    static unordered_map<unsigned long long, float> recall_memory_score;
    static unsigned int max_leafs;
    static unsigned int max_rollouts;
    static string recall_filename = "recallmemory.bin";

    const char player_1_symbol = 'O';
    const char player_2_symbol = 'X';
    const char blank_symbol = '.';

    const int num_cols = 7;
    const int num_rows = 6;
    const int bits_in_length = 3;
    const int win_length = 4;

    const int max_win_sets = 13;
    const int win_check_row_size = (win_length - 1) * max_win_sets;
    const int win_check_table_size = num_cols * num_rows * win_check_row_size;

    static int win_check_table[win_check_table_size];
    static bool win_check_table_filled = false;
    static uint32_t last_seed = 0;

    const int direction_size = (win_length - 1) * 2;

    const int vert_co[direction_size] = { 0, 0, 0, 0, 0, 0 };
    const int vert_row[direction_size] = { -3, -2, -1, 1, 2, 3 };
    const int horiz_co[direction_size] = { -3, -2, -1, 1, 2, 3 };
    const int horiz_row[direction_size] = { 0, 0, 0, 0, 0, 0 };
    const int diag1_co[direction_size] = { -3, -2, -1, 1, 2, 3 };
    const int diag1_row[direction_size] = { -3, -2, -1, 1, 2, 3 };
    const int diag2_co[direction_size] = { 3, 2, 1, -1, -2, -3 };
    const int diag2_row[direction_size] = { -3, -2, -1, 1, 2, 3 };


    enum class GameResult
    {
        player_1_wins = 0,
        player_2_wins = 1,
        draw = 2,
        not_completed = 3
    };

    void render(char(&array_pos)[num_cols * num_rows]);
    bool is_win(unsigned long long player, C4::GameResult prune_result);

    unsigned long long make_key(unsigned long long position, unsigned long long turn)
    {
        unsigned long long key = position;
        key *= 2;
        key += turn;
        return key;
    }

    void crack_key(unsigned long long& position, unsigned long long& turn, unsigned long long key)
    {
        turn = key & 0x1;
        position = key / 2;
    }

    string get_filename(string extension)
    {
        auto filename = recall_filename;
        string to_replace = ".bin";
        size_t pos = filename.find(to_replace);
        if (pos != string::npos)
        {
            filename.replace(pos, to_replace.length(), extension);
        }
        return filename;
    }

    void load_score()
    {
        auto filename_score = get_filename("_score.bin");

        filesystem::path filePath(filename_score);

        if (filesystem::exists(filePath)) {
            cout << "Loading " << filename_score << endl;
        }
        else {
            cout << "Unable to find " << filename_score << " aborting load." << endl;
            return;
        }

        ifstream inputfile(filename_score);
        unsigned long long position;
        float score;
        while (inputfile >> position >> score) {
            recall_memory_score[position] = score;
        }
        inputfile.close();
    }

    void load_learn()
    {
        auto filename_learn = get_filename("_learn.bin");

        filesystem::path filePath(filename_learn);

        if (filesystem::exists(filePath)) {
            cout << "Loading " << filename_learn << endl;
        }
        else {
            cout << "Unable to find " << filename_learn << " aborting load." << endl;
            return;
        }

        ifstream inputfile(filename_learn);
        unsigned long long position;
        float visits;
        float wins;
        while (inputfile >> position >> visits >> wins) {
            record_tuple rc;
            rc.visits = visits;
            rc.wins = wins;
            recall_memory_learn[position] = rc;
        }
        inputfile.close();

        //for (auto pair : recall_memory_learn)
        //{
        //    unsigned long long position;
        //    unsigned long long turn;
        //    crack_key(position, turn, pair.first);
        //    unsigned long long op_turn = 1 - turn;
        //    auto key = make_key(position, op_turn);
        //    if (recall_memory_learn.count(key) > 0)
        //    {
        //        cout << pair.first << ", " << key << " " << pair.second.wins << " " << pair.second.visits << " " << recall_memory_learn[key].wins << " " << recall_memory_learn[key].visits << endl;
        //    }
        //}
    }

    void save_saturated()
    {
        auto filename_learn = get_filename("_saturated.bin");
        ofstream outputFile(filename_learn);
        for (const auto& pair : recall_memory_saturated) {
            outputFile << pair.first << ' ' << pair.second.visits << ' ' << pair.second.wins << '\n';
        }
        outputFile.close();
    }

    void save_score()
    {
        auto filename_learn = get_filename("_score.bin");
        ofstream outputFile(filename_learn);
        for (const auto& pair : recall_memory_score) {
            outputFile << pair.first << ' ' << pair.second << '\n';
        }
        outputFile.close();
    }

    void save_learn()
    {
        auto filename_learn = get_filename("_learn.bin");
        ofstream outputFile(filename_learn);
        for (const auto& pair : recall_memory_learn) {
            outputFile << pair.first << ' ' << pair.second.visits << ' ' << pair.second.wins << '\n';
        }
        outputFile.close();

        unordered_map<unsigned long long, record_tuple> test_map;
        ifstream inputfile(filename_learn);
        unsigned long long key;
        float visits;
        float wins;
        while (inputfile >> key >> visits >> wins) {
            record_tuple rc;
            rc.visits = visits;
            rc.wins = wins;
            test_map[key] = rc;
        }
        inputfile.close();

        bool passed = true;
        for (const auto& pair : recall_memory_learn) {
            if (test_map.count(pair.first) == 0)
            {
                cout << "Missing key " << pair.first << endl;
                passed = false;
                break;
            }
            auto test_rec = test_map[pair.first];
            if (test_rec.visits != pair.second.visits || test_rec.wins != pair.second.wins)
            {
                cout << "value mismatch " << endl;
                passed = false;
                break;
            }
        }
        cout << " Result: " << passed << endl;

    }

    void set_parameters(char* filename, unsigned int leafs, unsigned int rollouts, unsigned int play_mode_flag)
    {
        recall_filename = filename;
        max_leafs = leafs;
        max_rollouts = rollouts;

        play_mode = play_mode_flag;
        if (play_mode == score_mode)
        {
            load_score();
        }
        else if (play_mode == learn_mode)
        {
            load_learn();
        }
    }

    void dump_win_check_table()
    {
        for (auto col = 0; col < (int)num_cols; col++)
        {
            for (auto row = 0; row < (int)num_rows; row++)
            {
                auto ndx = col * num_rows + row;
                cout << setw(3) << ndx << " | ";
                for (auto win_check_set = 0u; win_check_set < max_win_sets; win_check_set++)
                {
                    for (auto win_check_item = 0u; win_check_item < (win_length - 1); win_check_item++)
                    {
                        auto win_check_ndx = ndx * win_check_row_size + win_check_set * (win_length - 1) + win_check_item;
                        cout << setw(3) << win_check_table[win_check_ndx] << " ";
                    }
                    cout << "| ";
                }
                cout << endl;
            }
        }

        char array_pos[num_cols * num_rows];
        for (auto col = 0; col < (int)num_cols; col++)
        {
            for (auto row = 0; row < (int)num_rows; row++)
            {
                auto test_ndx = col * num_rows + row;

                for (auto win_check_set = 0u; win_check_set < max_win_sets; win_check_set++)
                {
                    for (auto ndx = 0u; ndx < num_cols * num_rows; ndx++) array_pos[ndx] = blank_symbol;
                    array_pos[test_ndx] = player_2_symbol;

                    bool valid = true;
                    for (auto win_check_item = 0; win_check_item < (win_length - 1); win_check_item++)
                    {
                        auto win_check_ndx = test_ndx * win_check_row_size + win_check_set * (win_length - 1) + win_check_item;
                        auto target_ndx = win_check_table[win_check_ndx];
                        if (target_ndx < 0)
                        {
                            valid = false;
                            break;
                        }
                        array_pos[target_ndx] = player_1_symbol;
                    }

                    if (!valid) break;
                    render(array_pos);
                }
            }
        }
    }

    int add_win_set(int col, int row, const int(&col_table)[direction_size], const int(&row_table)[direction_size], int win_check_set)
    {
        int num_win_check_sets_added = 0;
        int test_set[win_length - 1];

        for (auto start_dir_ndx = 0u; start_dir_ndx < (direction_size - (win_length - 1)) + 1; start_dir_ndx++)
        {
            bool all_valid = true;
            for (auto test_dir_ndx = 0u; test_dir_ndx < (win_length - 1); test_dir_ndx++)
            {
                int test_col = col + col_table[start_dir_ndx + test_dir_ndx];
                int test_row = row + row_table[start_dir_ndx + test_dir_ndx];
                bool valid = (test_col >= 0 && test_col < num_cols && test_row >= 0 && test_row < num_rows);
                //cout << "(" << test_col << ", " << test_row << ") " << (valid ? "+" : "-");
                if (!valid)
                {
                    all_valid = false;
                    break;
                }
                auto win_ndx = test_col * num_rows + test_row;
                //cout << win_ndx << " ";
                test_set[test_dir_ndx] = win_ndx;
            }
            if (all_valid)
            {
                auto ndx = col * num_rows + row;

                for (auto test_dir_ndx = 0u; test_dir_ndx < (win_length - 1); test_dir_ndx++)
                {
                    auto win_check_ndx = ndx * win_check_row_size + (win_check_set + num_win_check_sets_added) * (win_length - 1) + test_dir_ndx;
                    win_check_table[win_check_ndx] = test_set[test_dir_ndx];
                }
                num_win_check_sets_added++;
                //cout << " VALID ";
            }
            //cout << endl;
        }


        return num_win_check_sets_added;
    }
    void initialize_win_check_table()
    {
        for (auto x = 0u; x < win_check_table_size; x++) win_check_table[x] = -1;

        for (auto col = 0; col < (int)num_cols; col++)
        {
            for (auto row = 0; row < (int)num_rows; row++)
            {
                auto ndx = col * num_rows + row;
                auto win_check_set = 0;
                win_check_set += add_win_set(col, row, vert_co, vert_row, win_check_set);
                win_check_set += add_win_set(col, row, horiz_co, horiz_row, win_check_set);
                win_check_set += add_win_set(col, row, diag1_co, diag1_row, win_check_set);
                win_check_set += add_win_set(col, row, diag2_co, diag2_row, win_check_set);
            }
        }

        //dump_win_check_table();
    }

    void get_array_pos_from_binary(char(&array_pos)[num_cols * num_rows], unsigned long long position)
    {
        const int num_bits = num_cols * num_rows + num_cols * bits_in_length;
        char bits[num_bits];

        for (auto ndx = 0; ndx < num_bits; ndx++)
        {
            bits[num_bits - ndx - 1] = position % 2;
            position /= 2;
        }

        //for (auto ndx = 0; ndx < num_bits; ndx++)
        //{
        //    cout << (int)bits[ndx] << " ";
        //}
        //cout << endl;

        unsigned int used[num_cols];
        for (auto col = 0u; col < num_cols; col++)
        {
            auto ndx = num_cols * num_rows + bits_in_length * col;
            auto blanks = 0;
            for (auto b = 0u; b < bits_in_length; b++)
            {
                blanks *= 2;
                blanks += (int)bits[ndx + b];
                //cout << (int)bits[ndx + b] << " ";
            }
            used[col] = num_rows - blanks;
            //cout << blanks << endl;
        }

        for (auto ndx = 0u; ndx < num_cols * num_rows; ndx++)
        {
            auto col = ndx / num_rows;
            auto row = ndx % num_rows;
            if (row >= used[col])
            {
                array_pos[ndx] = blank_symbol;
                continue;
            }
            array_pos[ndx] = bits[ndx] == 1 ? player_2_symbol : player_1_symbol;
        }
    }

    unsigned int get_legal_moves(char(&array_pos)[num_cols * num_rows], unsigned int(&legal_moves)[num_cols])
    {
        auto row = num_rows - 1;
        auto move_ndx = 0u;
        for (auto col = 0u; col < num_cols; col++)
        {
            auto ndx = col * num_rows + row;
            if (array_pos[ndx] == blank_symbol)
            {
                legal_moves[move_ndx++] = col;
            }
        }
        return move_ndx;
    }

    void render(char(&array_pos)[num_cols * num_rows])
    {
        unsigned int legal_moves[num_cols];
        auto num_legal_moves = get_legal_moves(array_pos, legal_moves);

        cout << "+---+---+---+---+---+---+---+" << endl;
        for (auto row = 0u; row < num_rows; row++)
        {
            cout << "| ";
            auto display_row = num_rows - row - 1;
            for (auto col = 0u; col < num_cols; col++)
            {
                auto ndx = col * num_rows + display_row;
                cout << array_pos[ndx] << " | ";
            }
            cout << endl;
            cout << "+---+---+---+---+---+---+---+" << endl;
        }
        cout << "Moves: ";
        for (auto move = 0u; move < num_legal_moves; move++)
        {
            cout << legal_moves[move] << " ";
        }
        cout << endl;
    }

    void render_binary_position(unsigned long long position)
    {
        char array_pos[num_cols * num_rows];

        get_array_pos_from_binary(array_pos, position);
        render(array_pos);
    }

    bool check_for_win(int test_ndx, char(&array_pos)[num_cols * num_rows])
    {
        bool result = false;

        auto test_symbol = array_pos[test_ndx];

        for (auto win_check_set = 0u; win_check_set < max_win_sets; win_check_set++)
        {
            bool valid = true;
            for (auto win_check_item = 0; win_check_item < (win_length - 1); win_check_item++)
            {
                auto win_check_ndx = test_ndx * win_check_row_size + win_check_set * (win_length - 1) + win_check_item;
                auto target_ndx = win_check_table[win_check_ndx];
                if (target_ndx < 0 || array_pos[target_ndx] != test_symbol)
                {
                    valid = false;
                    break;
                }
            }

            if (valid)
            {
                result = true;
                break;
            }
        }

        return result;
    }

    GameResult move(char(&array_pos)[num_cols * num_rows], unsigned long long player, unsigned int move)
    {
        GameResult result = GameResult::not_completed;

        auto ndx = move * num_rows;
        for (auto row = 0u; row < num_rows; row++)
        {
            if (array_pos[ndx] == blank_symbol)
            {
                array_pos[ndx] = player == 0 ? player_1_symbol : player_2_symbol;
                if (check_for_win(ndx, array_pos))
                {
                    result = player == 0 ? GameResult::player_1_wins : GameResult::player_2_wins;
                }
                break;
            }
            ndx++;
        }

        return result;
    }

    float minimax(char(&array_pos)[num_cols * num_rows], int test_move, int player, int maximizing_player, int max_depth) {
        char rollout_board[num_cols * num_rows];
        memcpy(rollout_board, array_pos, sizeof(rollout_board));
        if (test_move >= 0)
        {
            auto result = move(rollout_board, player, test_move);
            if (result == GameResult::player_1_wins || result == GameResult::player_2_wins)
            {
                return is_win(maximizing_player, result) ? 1.0f : 0.0f;
            }
        }

        unsigned int legal_moves[num_cols];
        auto num_moves = get_legal_moves(rollout_board, legal_moves);
        if (max_depth == 0 || num_moves == 0) {
            return 0.5f;
        }

        if (player == maximizing_player) {

            float bestValue = -1000000.0;
            for (auto i = 0u; i < num_moves; ++i) {
                float value = minimax(rollout_board, legal_moves[i], 1 - player, maximizing_player, max_depth - 1);
                bestValue = bestValue > value ? bestValue : value;
            }
            return bestValue;
        }
        else {

            float bestValue = 1000000.0;
            for (auto i = 0u; i < num_moves; ++i) {
                float value = minimax(rollout_board, legal_moves[i], 1 - player, maximizing_player, max_depth - 1);
                bestValue = bestValue < value ? bestValue : value;
            }
            return bestValue;
        }
    }
    
    void test_min_max()
    {

        if (!win_check_table_filled)
        {
            initialize_win_check_table();
        }
        win_check_table_filled = true;

        vector<unsigned long long> positions = {
            1797558,
            1797046,
            8796094818742,
            8796094814646,
            72066390132709814,
            72066390132709806,
            72066665010616686,
            72066665010616622,
            72071063057127214,
            72071063057127213,
            72073262080382253,
            72073262080381741,
            108102059099312941,
            108102059099312940,
            126116457608762156,
            126116457608729388,
            126679407562146604,
            126679407562146603,
            126679407570535210,
            126679407570534698,
            126960882547241258,
            126960882547241257,
            126960951266717929
        };

        unsigned int player = 0;
        unsigned int maximizing_player = 0;
        for (auto position : positions)
        {
            char array_pos[num_cols * num_rows];

            get_array_pos_from_binary(array_pos, position);
            render(array_pos);

            unsigned int legal_moves[num_cols];
            auto num_moves = get_legal_moves(array_pos, legal_moves);
            for (auto x = 0u; x < num_moves; x++)
            {
                auto test_move = legal_moves[x];
                cout << test_move << " " << minimax(array_pos, test_move, player, maximizing_player, 4) << endl;
            }
            player = 1 - player;
        }
    }

    GameResult min_max_prune(char(&array_pos)[num_cols * num_rows], unsigned long long rollout_player, unsigned int &num_moves, unsigned int(&legal_moves)[num_cols])
    {
        GameResult result = GameResult::not_completed;

        return result;
    }

    float calc_rollout(unsigned long long position, unsigned long long player, unsigned long long num_rollouts)
    {
        float wins = 0.0f;
        float visits = 0.0f;
        auto key = make_key(position, player);
        if (play_mode == score_mode)
        {
            auto it = recall_memory_score.find(key);
            if (it != recall_memory_score.end()) {
                hits++;
                return it->second;
            }
            misses++;
        }

        if (last_seed == 0)
        {
            cout << "New Seed" << endl;
            last_seed = (uint32_t)time(NULL);
        }
        Squirrel3 rng(last_seed);

        if (!win_check_table_filled)
        {
            initialize_win_check_table();
        }
        win_check_table_filled = true;

        bool leaf_exists = false;
        if (play_mode == learn_mode && recall_memory_learn.count(key) > 0)
        {
            auto record = recall_memory_learn[key];
            wins = record.wins;
            visits = record.visits;
            leaf_exists = true;
        }
        //cout << "Result: " << wins << " Rollouts: " << visits << endl;

        char array_pos[num_cols * num_rows];
        char rollout_board[num_cols * num_rows];

        get_array_pos_from_binary(array_pos, position);

        for (auto x = 0u; x < num_rollouts; x++)
        {
            auto rollout_player = player;
            memcpy(rollout_board, array_pos, sizeof(rollout_board));
            while (true)
            {
                unsigned int legal_moves[num_cols];
                auto num_moves = get_legal_moves(rollout_board, legal_moves);
                if (num_moves <= 0)
                {
                    wins += 0.5f;
                    visits++;
                    break;
                }
            
                // check for forced wins / losses
                //auto prune_result = min_max_prune(rollout_board, rollout_player, num_moves, legal_moves);
                //if (prune_result != GameResult::not_completed)
                //{
                //    if (is_win(player, prune_result))
                //    {
                //        wins += 1.0f;
                //    }
                //    visits++;
                //    break;
                //}

                auto move_result = move(rollout_board, rollout_player, legal_moves[rng() % num_moves]);
 
                //render(rollout_board);

                if (move_result != GameResult::not_completed)
                {
                    //cout << "Player " << (int)game_result << " WINS!!" << endl;
                    if (is_win(player, move_result))
                    {
                        wins += 1.0f;
                    }
                    visits++;
                    break;
                }
                rollout_player = 1 - rollout_player;
            }

            //render(rollout_board);
        }
        last_seed = rng();

        if (play_mode == learn_mode && visits <= max_rollouts && (recall_memory_learn.size() < max_leafs || leaf_exists))
        {
            record_tuple record;
            record.wins = wins;
            record.visits = visits;
            recall_memory_learn[key] = record;
        }

        return wins / visits;
    }

    bool is_win(unsigned long long player, C4::GameResult result)
    {
        return (player == 0 && result == GameResult::player_1_wins) ||
            (player == 1 && result == GameResult::player_2_wins);
    }

    void start_new_game()
    {
        cout << " Mem " << recall_memory_learn.size() << " filename " << recall_filename << " leafs ";
        cout << max_leafs << " rollouts " << max_rollouts << " play mode " << play_mode << " hits " << hits << " misses " << misses << endl;
        hits = 0;
        misses = 0;
        test_min_max();
    }

    void finalize()
    {
        cout << "Finalizing recall memory..." << endl;
        auto count = 0u;
        auto total = recall_memory_learn.size();
        for (auto record : recall_memory_learn)
        {
            count++;
            int remaining_turns = (int) max_rollouts - (int)  record.second.visits;
            if (remaining_turns < 0) continue;

            unsigned long long position;
            unsigned long long turn;
            crack_key(position, turn, record.first);
            calc_rollout(position, turn, remaining_turns);
            if (count % 1000 == 0)
            {
                cout << count << "/" << total << endl;
            }
        }
        cout << count << "/" << total << endl;
        for (auto record : recall_memory_learn)
        {
            record_tuple rts;
            rts.visits = record.second.visits;
            rts.wins = record.second.wins;
            recall_memory_saturated[record.first] = rts;
            recall_memory_score[record.first] = (float)rts.wins / (float)rts.visits;
        }

        save_saturated();
        save_score();
    }

}
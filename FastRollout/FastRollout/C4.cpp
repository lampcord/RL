#include "pch.h"
#include "C4.h"
#include "squirrel3.h"
#include <iostream>
#include <random>
#include <iomanip>

using namespace std;

namespace C4
{
    const char player_1_symbol = 'X';
    const char player_2_symbol = 'O';
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
                bool valid = (test_col >= 0 && test_col < num_cols&& test_row >= 0 && test_row < num_rows);
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

    void get_array_pos_from_binary(char(&array_pos)[num_cols * num_rows], unsigned long long position, unsigned long long player)
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

        auto active_symbol = player == 0 ? player_1_symbol : player_2_symbol;
        auto passive_symbol = player == 0 ? player_2_symbol : player_1_symbol;
        for (auto ndx = 0u; ndx < num_cols * num_rows; ndx++)
        {
            auto col = ndx / num_rows;
            auto row = ndx % num_rows;
            if (row >= used[col])
            {
                array_pos[ndx] = blank_symbol;
                continue;
            }
            array_pos[ndx] = bits[ndx] == 1 ? active_symbol : passive_symbol;
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

    void render_binary_position(unsigned long long position, unsigned long long player)
    {
        char array_pos[num_cols * num_rows];

        get_array_pos_from_binary(array_pos, position, player);
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

    float calc_rollout(unsigned long long position, unsigned long long player, unsigned long long num_rollouts)
    {
        if (last_seed == 0)
        {
            cout << "New Seed" << endl;
            last_seed = time(NULL);
        }
        Squirrel3 rng(last_seed);

        if (!win_check_table_filled)
        {
            initialize_win_check_table();
        }
        win_check_table_filled = true;

        float result = 0.0f;

        char array_pos[num_cols * num_rows];
        char rollout_board[num_cols * num_rows];

        get_array_pos_from_binary(array_pos, position, 1 - player);

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
                    result += 0.5f;
                    break;
                }
                auto game_result = move(rollout_board, rollout_player, legal_moves[rng() % num_moves]);
 
                //render(rollout_board);

                if (game_result != GameResult::not_completed)
                {
                    //cout << "Player " << (int)game_result << " WINS!!" << endl;
                    if ((player == 0 && game_result == GameResult::player_1_wins) ||
                        (player == 1 && game_result == GameResult::player_2_wins))
                    {
                        result += 1.0f;
                    }
                    break;
                }
                rollout_player = 1 - rollout_player;
            }

            //render(rollout_board);
        }
        last_seed = rng();

        return result;
    }

}
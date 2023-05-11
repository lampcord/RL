#include "pch.h"
#include "C4.h"
#include "squirrel3.h"
#include <iostream>
#include <random>

using namespace std;

namespace C4
{
    const int num_cols = 7;
    const int num_rows = 6;
    const int bits_in_length = 3;
    const char player_1_symbol = 'X';
    const char player_2_symbol = 'O';
    const char blank_symbol = '.';

    enum class GameResult
    {
        player_1_wins = 0,
        player_2_wins = 1,
        draw = 2,
        not_completed = 3
    };

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

    GameResult move(char(&array_pos)[num_cols * num_rows], unsigned long long player, unsigned int move)
    {
        GameResult result = GameResult::not_completed;

        auto ndx = move * num_rows;
        for (auto row = 0u; row < num_rows; row++)
        {
            if (array_pos[ndx] == blank_symbol)
            {
                array_pos[ndx] = player == 0 ? player_1_symbol : player_2_symbol;
                break;
            }
            ndx++;
        }

        return result;
    }

    float calc_rollout(unsigned long long position, unsigned long long player, unsigned long long num_rollouts)
    {

        Squirrel3 rng(42);

        float result = 0.0f;

        char array_pos[num_cols * num_rows];
        char rollout_board[num_cols * num_rows];

        get_array_pos_from_binary(array_pos, position, player);

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
                    break;
                }

                move(rollout_board, rollout_player, legal_moves[rng() % num_moves]);
                //render(rollout_board);
                rollout_player = 1 - rollout_player;
            }
            result += 1.0f;

            //render(rollout_board);
        }

        return result;
    }

}
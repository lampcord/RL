#include "TicTacToe.h"
#include <map>
#include <set>
#include <iostream>

/*

Position is represented as follows in a 16 bit unsigned integer

.......XXXXXXXXX.......OOOOOOOOO

Move is represented by a number instead of a mask to keep under 256 bits

*/

using namespace std;

namespace TicTacToeNS
{
	const unsigned int win_table[] =
	{
		0b111000000,
		0b000111000,
		0b000000111,
		0b100100100,
		0b010010010,
		0b001001001,
		0b100010001,
		0b001010100
	};
	const char user_keys[] = { 'q','w','e','a','s','d','z','x','c' };
	map<char, unsigned short> key_to_move =
	{
		{'q', 0b100000000},
		{'w', 0b010000000},
		{'e', 0b001000000},
		{'a', 0b000100000},
		{'s', 0b000010000},
		{'d', 0b000001000},
		{'z', 0b000000100},
		{'x', 0b000000010},
		{'c', 0b000000001},
	};

	void TicTacToe::move(const PositionType& position, const unsigned char player, const MoveType move, MoveResult<PositionType>& move_result)
	{
		move_result.position = position;
		move_result.position.position[player] |= move;
		move_result.next_players_turn = 1 - player;
		move_result.result = GameResult::keep_playing;
		
		auto win_compare = move_result.position.position[player];

		for (auto win_entry : win_table)
		{
			if ((win_entry & win_compare) == win_entry)
			{
				move_result.result = player == 0 ? GameResult::player_0_win : GameResult::player_1_win;
				break;
			}
		}
	}

	void TicTacToe::get_initial_position(PositionType& position)
	{
		position.position[0] = 0b0;
		position.position[1] = 0b0;
	}
	void TicTacToe::get_legal_moves(const PositionType& position, const unsigned char player, MoveType& legal_moves)
	{
		legal_moves = position.position[0] | position.position[1];
		legal_moves = ~legal_moves;
		legal_moves &= 0b111111111;
	}

	void TicTacToe::render(const PositionType& position)
	{
		unsigned short win_result = 0b0;
		for (auto player = 0u; player < 2; player++)
		{
			auto win_compare = position.position[player];

			for (auto win_entry : win_table)
			{
				if ((win_entry & win_compare) == win_entry)
				{
					win_result = win_entry;
					break;
				}
			}
			if (win_result != 0b0) break;
		}

		unsigned short mask = 0b100000000;
		for (auto x = 0u; x < 9u; x++)
		{
			if (x % 3 == 0) cout << endl << "+---+---+---+" << endl << '|';
			auto c = '.';
			if (position.position[0] & mask)
			{
				c = '0';
			}
			else if (position.position[1] & mask)
			{
				c = '1';
			}
			if (mask & win_result)
			{
				cout << '(' << c << ")|";
			}
			else
			{
				cout << ' ' << c << " |";
			}
			mask = mask >> 1;
		}
		cout << endl << "+---+---+---+" << endl;
	}
	MoveType TicTacToe::prompt_user(const PositionType& position, const unsigned char player)
	{
		unsigned short mask = 0b100000000;
		set<char> valid_moves;

		for (auto x = 0u; x < 9u; x++)
		{
			if (x % 3 == 0) cout << endl << "+---+---+---+" << endl << '|';
			char c = user_keys[x];
			if (position.position[0] & mask)
			{
				c = '.';
			}
			else if (position.position[1] & mask)
			{
				c = '.';
			}
			else
			{
				valid_moves.insert(c);
			}
			cout << ' ' << c << " |";
			mask = mask >> 1;
		}
		cout << endl << "+---+---+---+" << endl;

		char move_choice = '.';
		while (valid_moves.size() > 0)
		{
			cout << "Enter move: (";
			for (auto c : valid_moves) cout << c << ", ";
			cout << ")";
			cout << endl;
			cin >> move_choice;
			if (key_to_move.count(move_choice) > 0 && valid_moves.count(move_choice))
			{
				return key_to_move[move_choice];
			}
		}

		return 0;
	}
}
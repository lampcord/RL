#include "TicTacToe.h"
#include <iostream>

/*

Position is represented as follows in a 16 bit unsigned integer

.......XXXXXXXXX.......OOOOOOOOO

Move is represented by a number instead of a mask to keep under 256 bits

*/


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
		unsigned short mask = 0b100000000;
		for (auto x = 0u; x < 9u; x++)
		{
			if (x % 3 == 0) std::cout << std::endl;
			auto c = '.';
			if (position.position[0] & mask)
			{
				c = '0';
			}
			else if (position.position[1] & mask)
			{
				c = '1';
			}
			std::cout << c;
			mask = mask >> 1;
		}
		std::cout << std::endl;
	}
}
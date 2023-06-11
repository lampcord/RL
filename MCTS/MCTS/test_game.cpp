#include "test_game.h"
#include <iostream>

using namespace std;

/*
Represents the game of 2 in a row.

4 slots:

| 0 | 1 | 2 | 3 |

Two players take turns playing into any open slot.
First player to get two in a row wins.

Game is represented as a 8 bit unsigned int as follows

AAAABBBB

Where AAAA is P0's position.
	  BBBB is P1's position.

Legal moves are returned as a mask:
XXXX3210


*/

namespace TestGameNS
{

	const unsigned int win_table[] =
	{
		0b1100,
		0b0110,
		0b0011
	};

	void TestGame::move(const PositionType& position, unsigned int player, MoveType move, MoveResult<MoveType>& move_result)
	{
		unsigned int move_mask = player == 0 ? move << 4 : move;

		move_result.position = position | move_mask;
		move_result.next_players_turn = 1 - player;
		move_result.result = GameResult::keep_playing;

		unsigned int win_compare = player == 0 ? move_result.position >> 4 : move_result.position;
		
		for (auto win_entry : win_table)
		{
			if ((win_entry & win_compare) == win_entry)
			{
				move_result.result = player == 0 ? GameResult::player_0_win : GameResult::player_1_win;
				break;
			}
		}
	}

	void TestGame::get_initial_position(PositionType& position)
	{
		position = 0b00000000;
	}

	void TestGame::get_legal_moves(const PositionType& position, const unsigned int player, MoveType& legal_moves)
	{
		unsigned int player1_pos = position >> 4;
		unsigned int player2_pos = position & 0b00001111;
		unsigned int blocked = player1_pos | player2_pos;
		legal_moves = ~blocked & 0b00001111;
	}

	void TestGame::render(const PositionType& position)
	{
		char display[] = "....\0";

		unsigned int move_mask = 0b10000000;
		for (auto x = 0u; x < 8u; x++)
		{
			if ((move_mask & position) == move_mask)
			{
				auto ndx = (x % 4);
				display[ndx] = x < 4 ? '0' : '1';
			}
			move_mask >>= 1;
		}
		cout << display;
	}

}

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

void TestGame::move(const unsigned char& position, unsigned int turn, int move, MoveResult<unsigned char>& move_result)
{
}

void TestGame::get_initial_position(unsigned char& position)
{
	position = 0b00000000;
}

void TestGame::get_legal_moves(const unsigned char& position, const unsigned int turn, unsigned char& legal_moves)
{
	unsigned int player1_pos = position >> 4;
	unsigned int player2_pos = position & 0b00001111;
	unsigned int blocked = player1_pos | player2_pos;
	legal_moves = ~blocked & 0b00001111;
}

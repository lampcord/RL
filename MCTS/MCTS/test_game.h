#pragma once
#include "game_rules.h"

class TestGame
{
public:
	TestGame() {};
	~TestGame() {};

	static void move(const unsigned char &position, unsigned int turn, int move, MoveResult<unsigned char> & move_result);
	static void get_initial_position(unsigned char& position);
	static void get_legal_moves(const unsigned char& position, const unsigned int turn, unsigned char& legal_moves);
};


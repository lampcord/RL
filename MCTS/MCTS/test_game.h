#pragma once
#include "game_rules.h"

using namespace GameRulesNS;

namespace TestGameNS
{

	typedef unsigned char PositionType;
	typedef unsigned char MoveType;

	class TestGame
	{
	public:
		TestGame() {};
		~TestGame() {};

		static void move(const PositionType& position, unsigned int player, unsigned int move, MoveResult<PositionType>& move_result);
		static void get_initial_position(PositionType& position);
		static void get_legal_moves(const PositionType& position, const unsigned int player, MoveType& legal_moves);

		static void render(const PositionType& position);
	};

}

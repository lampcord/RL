#pragma once
#include "game_rules.h"

using namespace GameRulesNS;


namespace TicTacToeNS
{
	typedef unsigned int PositionType;
	typedef unsigned short MoveType;
	const unsigned int NumChildren = 9u;

	class TicTacToe
	{
		TicTacToe() {};
		~TicTacToe() {};
		
		static void move(const PositionType& position, unsigned int player, unsigned int move, MoveResult<PositionType>& move_result);
		static void get_initial_position(PositionType& position);
		static void get_legal_moves(const PositionType& position, const unsigned int player, MoveType& legal_moves);

		static void render(const PositionType& position);
	};
}


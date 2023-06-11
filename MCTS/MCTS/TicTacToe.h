#pragma once
#include "game_rules.h"

using namespace GameRulesNS;


namespace TicTacToeNS
{
	struct PositionStruct {
		unsigned short position[2];
	};
	typedef PositionStruct PositionType;
	typedef unsigned short MoveType;

	class TicTacToe
	{
	public:
		TicTacToe() {};
		~TicTacToe() {};
		
		static void move(const PositionType& position, const unsigned char player, const MoveType move, MoveResult<PositionType>& move_result);
		static void get_initial_position(PositionType& position);
		static void get_legal_moves(const PositionType& position, const unsigned char player, MoveType& legal_moves);

		static void render(const PositionType& position);
	};
}


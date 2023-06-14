#pragma once
#include "game_rules.h"

using namespace GameRulesNS;

namespace Connect4NS
{
	struct PositionStruct {
		unsigned long long position[2];

		bool operator==(const PositionStruct& other) const {
			return position[0] == other.position[0] && position[1] == other.position[1];
		}
	};
	typedef PositionStruct PositionType;
	typedef unsigned char MoveType;

	class Connect4
	{
	public:


		static void move(const PositionType& position, const unsigned char player, const MoveType move, MoveResult<PositionType>& move_result);
		static void get_initial_position(PositionType& position);
		static void get_legal_moves(const PositionType& position, const unsigned char player, MoveType& legal_moves);

		static void render(const PositionType& position);
		static MoveType prompt_user(const PositionType& position, const unsigned char player);
		static void build_win_table_set();
	};

}


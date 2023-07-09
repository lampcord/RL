#pragma once
#include "game_rules.h"

using namespace GameRulesNS;

namespace BackgammonNS
{
	struct PositionStruct {
		unsigned long long position[2];

		bool operator==(const PositionStruct& other) const {
			return position[0] == other.position[0] && position[1] == other.position[1];
		}
	};
	struct MoveStruct
	{
		unsigned int moves;
		PositionStruct result_position;
	};
	typedef PositionStruct PositionType;
	typedef unsigned int MoveType;

	class Backgammon
	{
	private:
		static void render_bar_section(const BackgammonNS::PositionType& position);
		static void render_board_section(const BackgammonNS::PositionType& position, bool top);

	public:
		static void move(const PositionType& position, const unsigned char player, const MoveType move, MoveResult<PositionType>& move_result);
		static void get_initial_position(PositionType& position);
		static void get_legal_moves(const PositionType& position, const unsigned char player, const unsigned int roll);
		static void render(const PositionType& position);
		static MoveType prompt_user(const PositionType& position, const unsigned char player);
	};
}
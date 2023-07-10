#pragma once
#include "game_rules.h"
#include <functional>
#include <unordered_map>

using namespace GameRulesNS;

namespace BackgammonNS
{
	struct PositionStruct {
		unsigned long long position[2];

		bool operator==(const PositionStruct& other) const {
			return position[0] == other.position[0] && position[1] == other.position[1];
		}
	};

	struct PositionStructHash
	{
		size_t operator()(const PositionStruct& position) const
		{
			std::hash<uint64_t> hasher;
			size_t h1 = hasher(position.position[0]);
			size_t h2 = hasher(position.position[1]);

			return h1 ^ (h2 << 1);
		}
	};

	struct MoveStruct
	{
		PositionStruct result_position;
		unsigned char moves[4];
		void clear()
		{
			for (auto x = 0; x < 4; x++) moves[x] = 0;
			result_position.position[0] = 0;
			result_position.position[1] = 0;
		}
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
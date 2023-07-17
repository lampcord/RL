#pragma once
//#include "game_rules.h"
#include <functional>
#include <unordered_map>
#include <string>
#include <optional>

//using namespace GameRulesNS;

namespace BackgammonNS
{
	enum class castoff_availability {
		unavailable,
		pending,
		available
	};
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

	const unsigned int max_move_list = 2048;
	struct MoveList
	{
		std::unordered_map<PositionStruct, unsigned char, PositionStructHash> duplicate_positions;
		MoveStruct move_list[max_move_list];
		unsigned int move_list_size = 0;
		unsigned char max_sub_moves = 0;

		MoveList() {};
		~MoveList() {};
		void initialize(const PositionType& position) 
		{
			move_list[0].clear();
			move_list[0].result_position = position;
			move_list_size = 1;
			duplicate_positions.clear();
			max_sub_moves = 0;
		};
		void dump_moves(const unsigned char& player);
		std::optional<MoveStruct> get_legal_move(unsigned int& ndx);
	};
	class Backgammon
	{
	private:
		static void render_bar_section(const BackgammonNS::PositionType& position);
		static void render_board_section(const BackgammonNS::PositionType& position, bool top, unsigned char casted_off);

	public:
		static void position_from_string(const std::string str_pos, BackgammonNS::PositionType& position);
		//static void move(const PositionType& position, const unsigned char player, const MoveType move, MoveResult<PositionType>& move_result);
		static void get_initial_position(PositionType& position);
		static void generate_legal_moves(const PositionType& position, const unsigned char player, const unsigned int roll, MoveList & move_list);
		static void render(const PositionType& position);
		static MoveType prompt_user(const PositionType& position, const unsigned char player);
		static void run_position_tests(const std::string filename, bool verbose);
	};
}
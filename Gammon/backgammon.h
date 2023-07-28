#pragma once
#include <functional>
#include <string>
#include <optional>

namespace BackgammonNS
{
	const unsigned char bar_indicator = 0b11111000;

	typedef std::tuple<unsigned char, unsigned char> slot_info;
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
	//typedef PositionStruct PositionType;
	typedef unsigned int MoveType;

	struct MoveList;

	class Backgammon
	{
	private:
		static void render_bar_section(const BackgammonNS::PositionType& position, unsigned char player);
		static void render_board_section(const BackgammonNS::PositionType& position, bool top, unsigned char casted_off);
		static bool gen_moves_for_1_die(const unsigned int pos_ndx, const unsigned int& blocked, const unsigned char player, const unsigned int die, unsigned int move_ndx, castoff_availability can_castoff, MoveList& move_list, bool no_duplicates);

	public:
		static slot_info get_bar_info(const PositionType& position);
		static slot_info get_slot_info(const PositionType& position, unsigned char slot);
		static void update_slot(PositionType& position, unsigned char player, unsigned char slot, bool increment, MoveList& move_list);

		static void position_from_string(const std::string str_pos, BackgammonNS::PositionType& position);
		static std::string string_from_position(BackgammonNS::PositionType& position);
		static void get_initial_position(PositionType& position);
		static void generate_legal_moves(const PositionType& position, const unsigned char player, const unsigned int roll, MoveList & move_list, bool no_duplicates);
		static void render_roll(const unsigned char roll);
		static void render(const PositionType& position, unsigned char player);
		static void run_position_tests(const std::string filename, bool verbose, MoveList& move_list, int max_positions = -1);
		static int get_winner(const PositionType& position);
	};

}
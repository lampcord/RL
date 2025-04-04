#pragma once
#include <unordered_map>
#include <stdexcept>
#include "backgammon.h"
#include "flat_hash_map-master/bytell_hash_map.hpp"
#include <vector>

namespace BackgammonNS
{
	const unsigned int max_move_list = 4096;

	struct MoveList
	{
		ska::bytell_hash_map<PositionStruct, unsigned char, PositionStructHash> duplicate_positions;
		MoveStruct move_list[max_move_list] = {};
		unsigned int move_list_size = 0;

		unsigned short move_list_ndx[max_move_list] = {};
		unsigned int move_list_ndx_size = 0;

		unsigned char max_sub_moves = 0;

		MoveList() {};
		~MoveList() {};
		void initialize(const PositionStruct& position)
		{
			move_list[0].clear();
			move_list[0].result_position = position;
			move_list_size = 1;
			duplicate_positions.clear();
			max_sub_moves = 0;
			move_list_ndx_size = 0;
		};
		std::vector<unsigned char> get_all_single_moves(PositionStruct& position, std::vector<unsigned char>& moves_so_far);
		PositionStruct get_position_for_partial_move(std::vector<unsigned char>& moves_so_far);
		void dump_moves(const unsigned char& player);
		void build_index();
		static std::string get_move_desc(MoveStruct& move_set, unsigned char player);
	};

}
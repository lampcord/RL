#pragma once
#include "backgammon.h"

namespace BackgammonNS
{
	const unsigned int max_move_list = 4092;
	struct MoveList
	{
		std::unordered_map<PositionStruct, unsigned char, PositionStructHash> duplicate_positions;
		MoveStruct move_list[max_move_list] = {};
		unsigned int move_list_size = 0;

		unsigned short move_list_ndx[max_move_list] = {};
		unsigned int move_list_ndx_size = 0;

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
			move_list_ndx_size = 0;
		};

		void dump_moves(const unsigned char& player);
		std::optional<MoveStruct> get_legal_move(unsigned int& ndx);
		unsigned int get_number_of_moves();
	};

}
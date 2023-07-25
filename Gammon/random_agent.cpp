#include "random_agent.h"

namespace RandomAgentNS
{
	void RandomAgent::get_move(BackgammonNS::PositionStruct& position, unsigned char player, unsigned int roll, std::unique_ptr<BackgammonNS::MoveList>& move_list, Squirrel3& rng)
	{
		BackgammonNS::Backgammon::generate_legal_moves(position, player, roll, *move_list, true);
		if (move_list->move_list_ndx_size > 0)
		{
			auto move_set = move_list->move_list[move_list->move_list_ndx[rng() % move_list->move_list_ndx_size]];
			position = move_set.result_position;
		}
	}
}

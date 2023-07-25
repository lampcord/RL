#pragma once
#include "backgammon.h"
#include "squirrel3.h"
#include "movelist.h"
#include <memory>

namespace RandomAgentNS
{
	class RandomAgent
	{
	public:
		static void get_move(BackgammonNS::PositionStruct& position, unsigned char player, unsigned int roll, std::unique_ptr<BackgammonNS::MoveList>& move_list, Squirrel3& rng);
	};
}
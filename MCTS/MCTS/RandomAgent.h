#pragma once
#include "game_rules.h"
#include "squirrel3.h"

using namespace GameRulesNS;
namespace RandomAgentNS
{

	template<typename TGameRules, typename TPosition, typename TMoveType>
	class RandomAgent
	{
	public:
		RandomAgent() {
			rng = new Squirrel3(42);
		};
		~RandomAgent() {
			if (rng != nullptr)
			{
				delete rng;
				rng = nullptr;
			}
		};

		bool choose_move(TPosition position, unsigned int player, TMoveType& move);
	private:
		Squirrel3* rng = nullptr;
	};


	template<typename TGameRules, typename TPosition, typename TMoveType>
	inline bool RandomAgent<TGameRules, TPosition, TMoveType>::choose_move(TPosition position, unsigned int player, TMoveType& move)
	{
		TMoveType legal_moves;
		TGameRules::get_legal_moves(position, player, legal_moves);
		auto num_moves = get_num_moves(legal_moves);
		if (num_moves == 0)	return false;

		auto move_num = (*rng)() % num_moves;
		move = get_nth_move(legal_moves, move_num);
		return true;
	}
}

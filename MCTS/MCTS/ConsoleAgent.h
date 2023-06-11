#pragma once
#pragma once
#include "game_rules.h"

using namespace GameRulesNS;
using namespace std;

namespace ConsoleAgentNS
{

	template<typename TGameRules, typename TPosition, typename TMoveType>
	class ConsoleAgent
	{
	public:
		ConsoleAgent() {
		};
		~ConsoleAgent() {};

		bool choose_move(TPosition position, unsigned int player, TMoveType& move);
	};


	template<typename TGameRules, typename TPosition, typename TMoveType>
	inline bool ConsoleAgent<TGameRules, TPosition, TMoveType>::choose_move(TPosition position, unsigned int player, TMoveType& move)
	{
		move = TGameRules::prompt_user(position, player);
		return true;
	}
}

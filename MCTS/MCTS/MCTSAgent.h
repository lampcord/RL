#pragma once
#include <utility>
#include <concepts>
#include "game_rules.h"

using namespace std;
using namespace GameRulesNS;

/*
TGameRules: static class that provides all functionality needed to simulate game
move(position, player, move) -> position, player, result
get_legal_moves(position, player) -> [move]
get_initial_position() -> position


*/

//template <typename T, typename TPosition>
//concept CGameRules = requires(T c, TPosition position, int player, int move)
//{
//	{ c.move(position, player, move) } -> same_as<void>;
//};
namespace MCTSAgentNS
{

	template <typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	class MCTSAgent
	{
	public:
		MCTSAgent() {};
		~MCTSAgent() {};
		bool choose_move(TPosition position, unsigned int player, TMoveType& move);

	private:
		TNodeStorage node_storage;

		TNodeID select(TNodeID node);
		TNodeID expand(TNodeID node);
		pair<float, int> rollout(TNodeID node);
		void back_propopgate(TNodeID node, pair<float, int> rollout_result);
	};

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline bool MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::choose_move(TPosition position, unsigned int player, TMoveType& move)
	{
		auto root_node = node_storage.initialize(position, player);
		MoveResult<TPosition> move_result;

		TGameRules::move(0, 0, 0, move_result);

		auto node = select(root_node);

		//node = expand(node);

		//auto rollout_result = rollout(node);

		//back_propogate(node, rollout_result.firstValue, rollout_result);

		return true;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::select(TNodeID node)
	{
		return TNodeID();
	}

}

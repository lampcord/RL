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

		TNodeID select(TNodeID node_id);
		TNodeID expand(TNodeID node_id);
		pair<float, int> rollout(TNodeID node_id);
		void back_propopgate(TNodeID node_id, pair<float, int> rollout_result);
		TNodeID best_child(TNodeID node_id);
	};

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline bool MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::choose_move(TPosition position, unsigned int player, TMoveType& move)
	{
		auto root_node_id = node_storage.initialize(position, player);
		auto node = node_storage.get_node(root_node_id);
		if (node == nullptr) return false;

		for (auto x = 0u; x < 10; x++)
		{

			auto node_id = select(root_node_id);

			node_id = expand(node_id);

			//auto rollout_result = rollout(node);

			//back_propogate(node, rollout_result.firstValue, rollout_result);

			cout << "---------------------------" << endl;
			node_storage.dump();
		}

		return false;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::select(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->next_child_index == 0) return node_id;
		if (node->remaining_moves_mask != 0) return node_id;

		auto best_child_id = best_child(node_id);
		return select(best_child_id);
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::expand(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->remaining_moves_mask == 0)
		{
			TGameRules::get_legal_moves(node->position, node->player_to_move, node->remaining_moves_mask);
		}
		if (node->remaining_moves_mask == 0) return node_id;

		auto move = get_nth_move(node->remaining_moves_mask, 0);
		MoveResult<TPosition> move_result;
		TGameRules::move(node->position, node->player_to_move, move, move_result);
		node->remaining_moves_mask &= ~move;
		auto child_node_id = node_storage.create_child_node(node_id, move_result.position, move_result.next_players_turn, move);

		return child_node_id;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::best_child(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->next_child_index == 0) return node_id;

		return node->children[node->next_child_index - 1];
	}

}

#pragma once
#include <utility>
#include <concepts>
#include "game_rules.h"
#include "squirrel3.h"
#include <limits>

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
	struct RolloutResult
	{
		float score;
		unsigned int player;
	};

	template <typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	class MCTSAgent
	{
	public:
		MCTSAgent(float c = 1.41f) {
			rng = make_unique<Squirrel3>(42);
			_c = c;
		};
		~MCTSAgent() {};

		bool choose_move(TPosition position, unsigned int player, TMoveType& move);

	private:
		TNodeStorage node_storage;
		unique_ptr<Squirrel3> rng = nullptr;
		float _c = 1.41f;

		TNodeID select(TNodeID node_id);
		TNodeID expand(TNodeID node_id);
		void rollout(TNodeID node_id, RolloutResult& rollout_result);
		void back_propogate(TNodeID node_id, const RolloutResult& rollout_result);
		TNodeID best_child(TNodeID node_id);
		TNodeID most_visited(TNodeID node_id);
		float ucb(TNodeID node_id, float c);
	};

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline bool MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::choose_move(TPosition position, unsigned int player, TMoveType& move)
	{
		auto root_node_id = node_storage.initialize(position, player);
		auto node = node_storage.get_node(root_node_id);
		if (node == nullptr) return false;

		for (auto x = 0u; x < 10000; x++)
		{
			//cout << "---------------------------" << endl;

			auto node_id = select(root_node_id);

			node_id = expand(node_id);

			RolloutResult rollout_result;
			rollout(node_id, rollout_result);
			//cout << "Result: " << (int)rollout_result.player << " Score: " << rollout_result.score << endl;

			back_propogate(node_id, rollout_result);

		}
		//node_storage.dump();
		//node_storage.validate();
		//auto node_id = 0;
		//node = node_storage.get_node(node_id);
		//while (node != nullptr)
		//{
		//	cout << node_id << " ";
		//	TGameRules::render(node->position);
		//	node->dump();
		//	cout << " ";
		//	node_id++;
		//	node = node_storage.get_node(node_id);
		//	cout << endl;
		//}
		auto best_node_id = most_visited(root_node_id);
		auto best_node = node_storage.get_node(best_node_id);
		if (best_node == nullptr) return false;

		move = best_node->move_to_reach_position;

		return true;
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
		if (node->result != GameResult::keep_playing) return node_id;
		if (node->remaining_moves_mask == 0)
		{
			TGameRules::get_legal_moves(node->position, node->player_to_move, node->remaining_moves_mask);
		}
		if (node->remaining_moves_mask == 0) return node_id;

		auto move = get_nth_move(node->remaining_moves_mask, 0);
		MoveResult<TPosition> move_result;
		TGameRules::move(node->position, node->player_to_move, move, move_result);
		node->remaining_moves_mask &= ~move;
		auto child_node_id = node_storage.create_child_node(node_id, move_result.position, move_result.next_players_turn, move, move_result.result);

		return child_node_id;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline void MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::rollout(TNodeID node_id, RolloutResult& rollout_result)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return;
		auto parent = node_storage.get_node(node->parent_id);
		if (parent == nullptr) return;

		auto position = node->position;
		auto player_to_move = node->player_to_move;
		auto player_of_record = parent->player_to_move;
		auto result = node->result;

		//TGameRules::render(position);
		while (result == GameResult::keep_playing)
		{
			TMoveType legal_moves;
			TGameRules::get_legal_moves(position, player_to_move, legal_moves);
			auto num_moves = get_num_moves(legal_moves);
			if (num_moves == 0)
			{
				result = GameResult::tie;
				break;
			}

			auto move_num = (*rng)() % num_moves;
			auto move = get_nth_move(legal_moves, move_num);

			MoveResult<TPosition> move_result;
			TGameRules::move(position, player_to_move, move, move_result);

			player_of_record = player_to_move;
			player_to_move = move_result.next_players_turn;
			position = move_result.position;
			result = move_result.result;
			//TGameRules::render(position);
		}

		if (result == GameResult::tie)
		{
			rollout_result.score = 0.5f;
		}
		else
		{
			if ((result == GameResult::player_0_win && player_of_record == 0) ||
				(result == GameResult::player_1_win && player_of_record == 1))
			{
				rollout_result.score = 1.0f;
			}
			else
			{
				rollout_result.score = 0.0f;
			}
		}
		rollout_result.player = player_of_record;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline void MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::back_propogate(TNodeID node_id, const RolloutResult& rollout_result)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return;
		node->num_visits += 1.0f;
		auto parent = node_storage.get_node(node->parent_id);
		if (parent == nullptr) return;

		auto score = parent->player_to_move == rollout_result.player ? rollout_result.score : 1.0f - rollout_result.score;
		node->num_wins += score;

		back_propogate(node->parent_id, rollout_result);
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::best_child(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->next_child_index == 0) return node_id;

		auto best_score = ucb(node->children[0], _c);
		auto best_child_id = node->children[0];
		for (auto child_ndx = 1; child_ndx < node->next_child_index; child_ndx++)
		{
			auto score = ucb(node->children[child_ndx], _c);
			if (score > best_score)
			{
				best_score = score;
				best_child_id = node->children[child_ndx];
			}
		}
		return best_child_id;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::most_visited(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->next_child_index == 0) return node_id;

		auto best_score = 0;
		auto best_child_id = -1;
		for (auto child_ndx = 0; child_ndx < node->next_child_index; child_ndx++)
		{
			auto child_id = node->children[child_ndx];
			auto child = node_storage.get_node(child_id);
			if (child == nullptr) continue;

			auto score = child->num_visits;
			if (child_ndx == 0 || score > best_score)
			{
				best_score = score;
				best_child_id = node->children[child_ndx];
			}

		}
		return best_child_id;
	}

	/*
	exploration = c * math.sqrt(math.log(self.parent.num_visits) / self.num_visits)
	exploitation = self.num_wins / self.num_visits
	*/
	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline float MCTSAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::ucb(TNodeID node_id, float c)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return 0.0f;

		auto parent = node_storage.get_node(node->parent_id);
		if (parent == nullptr) return 0.0f;

		if (node->num_visits == 0.0f) return numeric_limits<float>::infinity();

		auto exploration = c * sqrt(log(parent->num_visits) / node->num_visits);
		auto exploitation = node->num_wins / node->num_visits;

		return exploration + exploitation;
	}

}

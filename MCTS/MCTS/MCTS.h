#pragma once
#include <utility>

using namespace std;
/*
TGameRules: static class that provides all functionality needed to simulate game
move(position, turn, move) -> position, turn, result
get_legal_moves(position, turn) -> [move]
get_initial_position() -> position


*/


template <typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition>
class MCTS
{
public:
	MCTS(TGameRules game_rules, TNodeStorage node_storage) 
	{
		this->game_rules = game_rules;
		this->node_storage = node_storage;
	};
	~MCTS() {};
	int find_move(TPosition position, unsigned int turn);

private:
	TGameRules game_rules;
	TNodeStorage node_storage;

	TNodeID select(TNodeID node);
	TNodeID expand(TNodeID node);
	pair<float, int> rollout(TNodeID node);
	void back_propopgate(TNodeID node, pair<float, int> rollout_result);
};

template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition>
inline int MCTS<TGameRules, TNodeStorage, TNodeID, TPosition>::find_move(TPosition position, unsigned int turn)
{
	auto root_node = node_storage.initialize(position, turn);

	auto node = select(root_node);

	node = expand(node);

	auto rollout_result = rollout(node);

	back_propogate(node, rollout_result.firstValue, rollout_result);

	return 0;
}

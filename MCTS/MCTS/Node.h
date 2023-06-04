#pragma once
#include <array>
#include <algorithm>
#include <iostream>
#include <iomanip>

/*
TNodeID: type of node id used to access nodes

TNodeStorage: container that creates and manages nodes
get_root_id() -> root_node_id
create_child_node(node_id, position, player) -> child_node
get_node(node_id) -> node
is_null(node_id) -> bool

*/

using namespace std;

template <typename TNodeID, typename TPosition, typename TMoveType, unsigned int TNumChildren>
struct Node
{
	Node() : children{} {};
	void initialize(TPosition position, int player_to_move, int move, TNodeID parent, TNodeID null_id);
	void dump();

	float num_visits = 0.0f;
	float num_wins = 0.0f;

	TPosition position;
	int player_to_move = 0;
	TMoveType move_to_reach_position = 0;
	
	TNodeID parent;
	TMoveType remaining_moves_mask = 0;
	array<TNodeID, TNumChildren> children;
	int next_child_index = 0;
};

template <typename TPosition, typename TMoveType, unsigned int TMaxNode, unsigned int TNumChildren>
class NodeContainerArray
{
public:
	NodeContainerArray() {};
	~NodeContainerArray() {};
	void dump();

	int initialize(TPosition& position, int player_to_move);
	int get_root_id() { return root_id; }
	int create_child_node(int parent_id, TPosition& position, int player_to_move, int move);
	Node<int, TPosition, TMoveType, TNumChildren> * get_node(int node_id);
	bool is_null(int node_id) { return node_id == null_id; }
	int get_null() { return null_id; }

private:
	unsigned int num_elements;
	const int null_id = -1;
	const int root_id = 0;
	array<Node<int, TPosition, TMoveType, TNumChildren>, TMaxNode> nodes;
};


template<typename TPosition, typename TMoveType, unsigned int TMaxNode, unsigned int TNumChildren>
inline void NodeContainerArray<TPosition, TMoveType, TMaxNode, TNumChildren>::dump()
{
	for (auto x = 0u; x < num_elements; x++)
	{
		cout << setw(3) << x << ") ";
		nodes[x].dump();
		cout << endl;
	}
}

template<typename TPosition, typename TMoveType, unsigned int TMaxNode, unsigned int TNumChildren>
inline int NodeContainerArray<TPosition, TMoveType, TMaxNode, TNumChildren>::initialize(TPosition& position, int player_to_move)
{
	num_elements = root_id;
	nodes[num_elements].initialize(position, player_to_move, -1, null_id, null_id);
	num_elements++;
	return root_id;
}

template<typename TPosition, typename TMoveType, unsigned int TMaxNode, unsigned int TNumChildren>
inline int NodeContainerArray<TPosition, TMoveType, TMaxNode, TNumChildren>::create_child_node(int parent_id, TPosition& position, int player_to_move, int move)
{
	if (num_elements >= nodes.size()) return null_id;
	if (parent_id < 0 || parent_id >= (int)num_elements) return null_id;

	auto parent_node = &nodes[parent_id];
	if (parent_node->next_child_index >= parent_node->children.size()) return null_id;

	int next_node_id = num_elements++;

	parent_node->children[parent_node->next_child_index++] = next_node_id;
	
	nodes[next_node_id].initialize(position, player_to_move, move, parent_id, null_id);
	return next_node_id;
}

template<typename TPosition, typename TMoveType, unsigned int TMaxNode, unsigned int TNumChildren>
inline Node<int, TPosition, TMoveType, TNumChildren>* NodeContainerArray<TPosition, TMoveType, TMaxNode, TNumChildren>::get_node(int node_id)
{
	if (node_id >= 0 && node_id < num_elements) return &(nodes[node_id]);

	return nullptr;
}

template<typename TNodeID, typename TPosition, typename TMoveType, unsigned int TNumChildren>
inline void Node<TNodeID, TPosition, TMoveType, TNumChildren>::initialize(TPosition position, int player_to_move, int move, TNodeID parent, TNodeID null_id)
{
	this->position = position;
	this->parent = parent;
	this->player_to_move = player_to_move;
	this->move_to_reach_position = move;

	num_visits = 0.0f;
	num_wins = 0.0f;
	fill(children.begin(), children.end(), null_id);
	next_child_index = 0;
}

template<typename TNodeID, typename TPosition, typename TMoveType, unsigned int TNumChildren>
inline void Node<TNodeID, TPosition, TMoveType, TNumChildren>::dump()
{
	cout << setw(3) << parent << " [ ";
	for (auto x = 0; x < next_child_index; x++) cout << children[x] << " ";
	cout << "]";
}


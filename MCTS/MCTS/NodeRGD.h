#pragma once
#include <array>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include <bitset>
#include <assert.h>
#include "game_rules.h"

/*
TNodeID: type of node id used to access nodes

TNodeStorage: container that creates and manages nodes
get_root_id() -> root_node_id
create_child_node(node_id, position, player) -> child_node
get_node(node_id) -> node
is_null(node_id) -> bool

*/

using namespace std;
using namespace GameRulesNS;

namespace NodeRGDNS
{
	/*
	Instead of having an array of nodes, we could store only the position of the first node and then calculate the position of each of the next nodes as an offset from there.
	???? Would that waste a lot of space????.
	*/
	template <typename TNodeID, typename TPosition, typename TMoveType>
	struct NodeRGD
	{
		NodeRGD() {};
		void initialize(TPosition position, int player_to_move, int move, GameResult result, TNodeID parent_id, TNodeID null_id);
		void dump();
		void show_size();
		TNodeID get_child_id(unsigned int child_ndx);

		float num_visits = 0.0f;
		float num_wins = 0.0f;
		TNodeID parent_id = TNodeID();

		TNodeID first_child_id = TNodeID();
		TPosition position;
		TMoveType move_to_reach_position = 0;
		TMoveType remaining_moves_mask = 0;

		GameResult result = GameResult::keep_playing;
		unsigned char player_to_move = 0;
		unsigned char num_children = 0;
	};

	template<typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID NodeRGD<TNodeID, TPosition, TMoveType>::get_child_id(unsigned int child_ndx)
	{
		//if (child_ndx >= num_children) return -1;

		return first_child_id + child_ndx;
	}

	template<typename TNodeID, typename TPosition, typename TMoveType>
	inline void NodeRGD<TNodeID, TPosition, TMoveType>::show_size()
	{
		cout << "Node Size: " << sizeof(*this) << endl;
		cout << "num_visits: " << sizeof(num_visits) << endl;
		cout << "num_wins: " << sizeof(num_wins) << endl;
		cout << "parent_id: " << sizeof(parent_id) << endl;

		cout << "first_child_id: " << sizeof(first_child_id) << endl;
		cout << "position: " << sizeof(position) << endl;
		cout << "move_to_reach_position: " << sizeof(move_to_reach_position) << endl;
		cout << "remaining_moves_mask: " << sizeof(remaining_moves_mask) << endl;
		cout << "result: " << sizeof(result) << endl;
		cout << "player_to_move: " << sizeof(player_to_move) << endl;
		cout << "num_children: " << sizeof(num_children) << endl;
	}

	template <typename TPosition, typename TMoveType, unsigned int TMaxNode>
	class NodeContainerArrayRGD
	{
	public:
		NodeContainerArrayRGD() {
			nodes = make_unique<array<NodeRGD<int, TPosition, TMoveType>, TMaxNode>>();
		};
		~NodeContainerArrayRGD() {};
		void dump();

		int initialize(TPosition& position, int player_to_move);
		int get_root_id() { return root_id; }
		bool reserve_child_nodes(int parent_id, unsigned int num_nodes);
		int create_child_node(int parent_id, TPosition& position, int player_to_move, int move, GameResult result);
		NodeRGD<int, TPosition, TMoveType>* get_node(int node_id);
		bool is_null(int node_id) { return node_id == null_id; }
		int get_null() { return null_id; }
		unsigned int get_num_elements() { return num_elements; }
		bool validate();
	private:
		unsigned int num_elements;
		const int null_id = -1;
		const int root_id = 0;
		unique_ptr<array<NodeRGD<int, TPosition, TMoveType>, TMaxNode>> nodes;
	};


	template<typename TPosition, typename TMoveType, unsigned int TMaxNode>
	inline void NodeContainerArrayRGD<TPosition, TMoveType, TMaxNode>::dump()
	{
		for (auto x = 0u; x < num_elements; x++)
		{
			cout << setw(3) << x << ") ";
			(*nodes)[x].dump();
			cout << endl;
		}
	}

	template<typename TPosition, typename TMoveType, unsigned int TMaxNode>
	inline int NodeContainerArrayRGD<TPosition, TMoveType, TMaxNode>::initialize(TPosition& position, int player_to_move)
	{
		num_elements = root_id;
		(*nodes)[num_elements].initialize(position, player_to_move, -1, GameResult::keep_playing, null_id, null_id);
		num_elements++;

		return root_id;
	}

	template<typename TPosition, typename TMoveType, unsigned int TMaxNode>
	inline bool NodeContainerArrayRGD<TPosition, TMoveType, TMaxNode>::reserve_child_nodes(int parent_id, unsigned int num_nodes)
	{
		if (num_elements + num_nodes >= nodes->size()) return false;
		if (parent_id < 0 || parent_id >= (int)num_elements) return false;

		auto parent_node = &(*nodes)[parent_id];
		if (parent_node->num_children > 0) return false;

		int next_node_id = num_elements;
		num_elements += num_nodes;

		parent_node->first_child_id = next_node_id;

		return true;
	}

	template<typename TPosition, typename TMoveType, unsigned int TMaxNode>
	inline int NodeContainerArrayRGD<TPosition, TMoveType, TMaxNode>::create_child_node(int parent_id, TPosition& position, int player_to_move, int move, GameResult result)
	{
		if (parent_id < 0 || parent_id >= (int)num_elements) return null_id;

		auto parent_node = &(*nodes)[parent_id];

		int child_id = parent_node->get_child_id(parent_node->num_children);

		(*nodes)[child_id].initialize(position, player_to_move, move, result, parent_id, null_id);

		// This MUST be done last, otherwise a thread may try to access an uninitialized child.
		parent_node->num_children++;
		return child_id;
	}

	template<typename TPosition, typename TMoveType, unsigned int TMaxNode>
	inline NodeRGD<int, TPosition, TMoveType>* NodeContainerArrayRGD<TPosition, TMoveType, TMaxNode>::get_node(int node_id)
	{
		if (node_id >= 0 && node_id < (int)num_elements) return &((*nodes)[node_id]);

		return nullptr;
	}

	template<typename TNodeID, typename TPosition, typename TMoveType>
	inline void NodeRGD<TNodeID, TPosition, TMoveType>::initialize(TPosition position, int player_to_move, int move, GameResult result, TNodeID parent_id, TNodeID null_id)
	{
		// These never change after being initialized from create_child_node.
		this->position = position;
		this->parent_id = parent_id;
		this->player_to_move = player_to_move;
		this->move_to_reach_position = move;
		this->result = result;

		// These are constantly updated and may need to be atomic.
		num_visits = 0.0f;
		num_wins = 0.0f;
		first_child_id = null_id;
		num_children = 0;
		remaining_moves_mask = 0;
	}

	template<typename TNodeID, typename TPosition, typename TMoveType>
	inline void NodeRGD<TNodeID, TPosition, TMoveType>::dump()
	{
		cout << setw(3) << parent_id << " ";
		cout << bitset<sizeof(TMoveType) * 8>(remaining_moves_mask) << " ";
		cout << bitset<sizeof(TMoveType) * 8>(move_to_reach_position);
		cout << " [ ";
		for (auto x = 0; x < num_children; x++) cout << get_child_id(x) << " ";
		cout << "] ";
		cout << num_wins << "/" << num_visits << " ";
	}

	template<typename TPosition, typename TMoveType, unsigned int TMaxNode>
	inline bool NodeContainerArrayRGD<TPosition, TMoveType, TMaxNode>::validate()
	{
		// all of a node's children should have their parent be the node
		auto nodes_checked = 0;
		for (auto node_id = 0u; node_id < num_elements; node_id++)
		{
			auto node = (*nodes)[node_id];
			for (auto child_ndx = 0; child_ndx < node.num_children; child_ndx++)
			{
				auto child_id = node.get_child_id(child_ndx);
				auto child_node = get_node(child_id);
				if (child_node == nullptr)
				{
					cout << "VALIDATE FAILED (Valid Child) Node ID: " << node_id << " Child ID: " << child_id << endl;
					return false;
				}
				if (child_node->parent_id != node_id)
				{
					cout << "VALIDATE FAILED (Parent of Child) Node ID: " << node_id << " Child ID: " << child_id << endl;
					return false;
				}
			}
			nodes_checked++;
		}
		cout << "Validate Children PASSED " << nodes_checked << endl;

		// all nodes should have a parent who has them as a child
		nodes_checked = 0;
		auto unused_nodes = 0u;
		for (auto node_id = 0u; node_id < num_elements; node_id++)
		{
			auto node = (*nodes)[node_id];
			if (node.num_visits == 0)
			{
				unused_nodes++;
				continue;
			}
			auto parent = get_node(node.parent_id);
			if (parent == nullptr) continue;

			bool found_parents_child = false;
			for (auto child_ndx = 0; child_ndx < parent->num_children; child_ndx++)
			{
				auto child_id = parent->get_child_id(child_ndx);
				if (child_id == node_id)
				{
					found_parents_child = true;
					break;
				}
			}
			if (!found_parents_child)
			{
				cout << "VALIDATE FAILED (Child of Parent) Node ID: " << node_id << endl;
				return false;
			}
			nodes_checked++;
		}
		cout << "Validate Parents PASSED " << nodes_checked << " unused: " << unused_nodes << endl;

		// the sum of a node's children's visits == node 
		nodes_checked = 0;
		for (auto node_id = 0u; node_id < num_elements; node_id++)
		{
			auto node = (*nodes)[node_id];
			if (node.num_children == 0) continue;

			auto child_visits = 0.0f;
			auto node_visits = node.parent_id == null_id ? node.num_visits : node.num_visits - 1;

			for (auto child_ndx = 0; child_ndx < node.num_children; child_ndx++)
			{
				auto child_id = node.get_child_id(child_ndx);
				auto child_node = get_node(child_id);
				if (child_node == nullptr)
				{
					cout << "VALIDATE FAILED (Valid Child) Node ID: " << node_id << " Child ID: " << child_id << endl;
					return false;
				}
				child_visits += child_node->num_visits;
			}
			if (node_visits != child_visits)
			{
				cout << "VALIDATE FAILED (Visits) Node ID: " << node_id << " Visits " << node_visits << " Child visits " << child_visits << endl;
				return false;
			}
			nodes_checked++;
		}
		cout << "Validate Visits PASSED " << nodes_checked << endl;

		// the sum of a node's children's wins == wins with same parent move + (1 - wins with different child's parent's move)
		nodes_checked = 0;
		for (auto node_id = 0u; node_id < num_elements; node_id++)
		{
			auto node = (*nodes)[node_id];
			if (node.num_children == 0) continue;

			auto child_wins = 0.0f;
			if (node.parent_id == null_id) continue;

			auto parent = get_node(node.parent_id);
			auto flip_results = node.player_to_move != parent->player_to_move;

			for (auto child_ndx = 0; child_ndx < node.num_children; child_ndx++)
			{
				auto child_id = node.get_child_id(child_ndx);
				auto child_node = get_node(child_id);
				if (child_node == nullptr)
				{
					cout << "VALIDATE FAILED (Valid Child) Node ID: " << node_id << " Child ID: " << child_id << endl;
					return false;
				}
				child_wins += flip_results ? (child_node->num_visits - child_node->num_wins) : child_node->num_wins;
			}

			if (node.num_wins < child_wins || node.num_wins > child_wins + 1.0f)
			{
				cout << "VALIDATE FAILED (Wins) Node ID: " << node_id << " Wins " << node.num_wins << " Child Wins " << child_wins << endl;
				return false;
			}
			nodes_checked++;
		}
		cout << "Validate Wins PASSED " << nodes_checked << endl;

		// Check what pct of nodes have some but not all children.
		nodes_checked = 0;
		auto some_children = 0;
		for (auto node_id = 0u; node_id < num_elements; node_id++)
		{
			auto node = (*nodes)[node_id];
			if (node.num_children > 0 && node.remaining_moves_mask != 0)
			{
				some_children++;
			}
			nodes_checked++;
		}
		cout << "Total Nodes: " << nodes_checked << " Some Children " << some_children << endl;

		return false;
	}
}
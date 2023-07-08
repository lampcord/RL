#pragma once
#include <utility>
#include <concepts>
#include <limits>
#include <unordered_map>
#include <map>
#include "game_rules.h"
#include "squirrel3.h"
#include "PerfTimer.h"
#include "concurrent_queue_cv.h"
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
namespace MCTSRGDAgentNS
{
	static map<float, float> numerator_cache;
	
	struct RolloutResult
	{
		float score;
		unsigned int player;
	};
	
	template <typename TNodeID>
	struct rollout_queue_package
	{
		TNodeID node_id;
		RolloutResult rollout_result;
	};

	template <typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	class MCTSRGDAgent
	{
	public:
		MCTSRGDAgent(unsigned long long max_time = 10000000, 
			uint32_t seed = 42,
			unsigned int select_threads = 4u,
			unsigned int expand_threads = 1u,
			unsigned int rollout_threads = 5u,
			unsigned int back_propogate_threads = 4u,
			float c = 1.41f) {
			rng = make_unique<Squirrel3>(seed);
			timer = make_unique<PerfTimer>(false, false, true);
			_c = c;
			this->max_time = max_time;

			for (auto x = 0u; x < select_threads; x++)	worker_threads.emplace_back(&MCTSRGDAgent::select_thread, this);
			for (auto x = 0u; x < expand_threads; x++)	worker_threads.emplace_back(&MCTSRGDAgent::expand_thread, this);
			for (auto x = 0u; x < rollout_threads; x++)	worker_threads.emplace_back(&MCTSRGDAgent::rollout_thread, this);
			for (auto x = 0u; x < back_propogate_threads; x++ )	worker_threads.emplace_back(&MCTSRGDAgent::back_propogate_thread, this);
			cout << "Total Threads: " << worker_threads.size() << endl;
		};
		~MCTSRGDAgent() {
			cout << "Discarded Select:         " << select_queue.release_all() << endl;
			cout << "Discarded Expand:         " << expand_queue.release_all() << endl;
			cout << "Discarded Rollout:        " << rollout_queue.release_all() << endl;
			cout << "Discarded Back Propogate: " << back_propogate_queue.release_all() << endl;
			for (auto& t : worker_threads) t.join();
		};

		bool choose_move(TPosition position, unsigned int player, TMoveType& move);
		void get_root_choice_map(unordered_map<TMoveType, float>& choice_map);
		unsigned long long get_num_back_propogates() { return num_back_propogates; }
		void clear_back_propogates() { num_back_propogates = 0u; }
		void add_select_thread()
		{
			worker_threads.emplace_back(&MCTSRGDAgent::select_thread, this);
			cout << "Total Threads: " << worker_threads.size() << endl;
		}
		void add_rollout_thread()
		{
			worker_threads.emplace_back(&MCTSRGDAgent::rollout_thread, this);
			cout << "Total Threads: " << worker_threads.size() << endl;
		}
		void add_back_propogate_thread()
		{
			worker_threads.emplace_back(&MCTSRGDAgent::back_propogate_thread, this);
			cout << "Total Threads: " << worker_threads.size() << endl;
		}
	private:
		TNodeStorage node_storage;
		unique_ptr<Squirrel3> rng = nullptr;
		unique_ptr<PerfTimer> timer = nullptr;
		float _c = 1.41f;
		unsigned long long max_time = 0u;
		unsigned long long num_back_propogates = 0u;

		TNodeID select(TNodeID node_id);
		TNodeID expand(TNodeID node_id);
		void rollout(TNodeID node_id, RolloutResult& rollout_result);
		void back_propogate(TNodeID node_id, const RolloutResult& rollout_result);
		TNodeID best_child(TNodeID node_id);
		TNodeID best_child_fast(TNodeID node_id);
		TNodeID most_visited(TNodeID node_id);
		float ucb(TNodeID node_id, float c);

		vector<thread> worker_threads;

		void select_thread();
		void expand_thread();
		void rollout_thread();
		void back_propogate_thread();

		cq::concurrent_queue<TNodeID>select_queue;
		cq::concurrent_queue<TNodeID>expand_queue;
		cq::concurrent_queue<rollout_queue_package<TNodeID>>rollout_queue;
		cq::concurrent_queue<rollout_queue_package<TNodeID>>back_propogate_queue;
	};

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline bool MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::choose_move(TPosition position, unsigned int player, TMoveType& move)
	{
		TMoveType legal_moves;
		TGameRules::get_legal_moves(position, player, legal_moves);
		auto num_moves = get_num_moves(legal_moves);
		if (num_moves == 0) return false;

		auto root_node_id = node_storage.initialize(position, player);
		auto node = node_storage.get_node(root_node_id);
		if (node == nullptr) return false;

		select_queue.enable_push();
		rollout_queue.enable_push();
		rollout_queue.enable_push();
		back_propogate_queue.enable_push();

		for (auto x = 0; x < 64; x ++) select_queue.push(root_node_id);

		this_thread::sleep_for(chrono::microseconds(max_time));

		back_propogate_queue.disable_push();
		rollout_queue.disable_push();
		rollout_queue.disable_push();
		select_queue.disable_push();

		//timer->start();
		//auto x = 0u;
		//for (x = 0u; x < 5000000; x++)
		//{
		//	//cout << "---------------------------" << endl;

		//	auto node_id = select(root_node_id);

		//	node_id = expand(node_id);

		//	RolloutResult rollout_result;
		//	rollout(node_id, rollout_result);
		//	//cout << "Result: " << (int)rollout_result.player << " Score: " << rollout_result.score << endl;

		//	back_propogate(node_id, rollout_result);

		//	if (timer->GetElapsedThreadTime() > max_time) break;
		//}
		//cout << "Time: " << (float)timer->GetElapsedThreadTime() / 10000000.0 << " Loops: " << x << " Nodes: " << node_storage.get_num_elements() << endl;
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
		//cout << "EV:" << best_node->num_wins / best_node->num_visits << endl;
		unordered_map<TMoveType, float> choice_map;
		get_root_choice_map(choice_map);
		//for (auto pair : choice_map)
		//{
		//	cout << bitset<sizeof(TMoveType) * 8>(pair.first) << " " << pair.second << endl;
		//}
		return true;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline void MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::get_root_choice_map(unordered_map<TMoveType, float>& choice_map)
	{
		auto root_node = node_storage.get_node(node_storage.get_root_id());
		if (root_node == nullptr) return;

		for (auto child_ndx = 0; child_ndx < root_node->num_children.load(memory_order_acquire); child_ndx++)
		{
			auto child_id = root_node->get_child_id(child_ndx);
			auto child = node_storage.get_node(child_id);
			if (child == nullptr) continue;

			if (choice_map.count(child->move_to_reach_position) == 0) choice_map[child->move_to_reach_position] = 0.0f;
			choice_map[child->move_to_reach_position] += child->num_visits.load(memory_order_acquire) / root_node->num_visits.load(memory_order_acquire);
		}
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::select(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->num_children == 0) return node_id;
		if (node->remaining_moves_mask != 0) return node_id;

		auto best_child_id = best_child_fast(node_id);

		return select(best_child_id);
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::expand(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->result != GameResult::keep_playing) return node_id;
		if (node->remaining_moves_mask == 0 && node->num_children == 0)
		{
			TMoveType remaining_moves_mask;
			TGameRules::get_legal_moves(node->position, node->player_to_move, remaining_moves_mask);
			node->remaining_moves_mask.store(remaining_moves_mask, memory_order_release);
			auto num_children = get_num_moves(node->remaining_moves_mask.load(memory_order_acquire));
			if (num_children > 0)
			{
				auto expanded = node_storage.reserve_child_nodes(node_id, num_children);
				if (!expanded)
				{
					node->remaining_moves_mask.store(0u, memory_order_release);
					return node_id;
				}
			}
		}
		if (node->remaining_moves_mask == 0) return node_id;

		auto move = get_first_move(node->remaining_moves_mask.load(memory_order_acquire));
		MoveResult<TPosition> move_result;
		TGameRules::move(node->position, node->player_to_move, move, move_result);
		node->remaining_moves_mask &= ~move;
		auto child_node_id = node_storage.create_child_node(node_id, move_result.position, move_result.next_players_turn, move, move_result.result);

		return child_node_id;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline void MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::rollout(TNodeID node_id, RolloutResult& rollout_result)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return;
		auto parent = node_storage.get_node(node->parent_id);
		if (parent == nullptr) return;

		auto position = node->position;
		auto player_to_move = node->player_to_move;
		auto player_of_record = parent->player_to_move;
		auto result = node->result;

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
	inline void MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::back_propogate(TNodeID node_id, const RolloutResult& rollout_result)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return;

		auto parent = node_storage.get_node(node->parent_id);
		if (parent == nullptr)
		{
			// must update visits even if we have no parent because that would mean we are the root node.
			node->num_visits += 1.0f;
			num_back_propogates++;
			return;
		}
		auto score = parent->player_to_move == rollout_result.player ? rollout_result.score : 1.0f - rollout_result.score;
		node->num_wins += score;

		// need to do this last because it is a trigger to best_child_fast
		node->num_visits += 1.0f;

		back_propogate(node->parent_id, rollout_result);
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::best_child(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->num_children == 0) return node_id;

		auto best_score = ucb(node->get_child_id(0), _c);
		auto best_child_id = node->get_child_id(0);
		for (auto child_ndx = 1; child_ndx < node->num_children.load(memory_order_acquire); child_ndx++)
		{
			auto score = ucb(node->get_child_id(child_ndx), _c);
			if (score == numeric_limits<float>::infinity())
			{
				best_child_id = node->get_child_id(child_ndx);
				break;
			}

			if (score > best_score)
			{
				best_score = score;
				best_child_id = node->get_child_id(child_ndx);
			}
		}
		return best_child_id;
	}

	/*
	Some optimization ideas.
	1) We only need to calculate c * sqrt(log(parent_visits)) once.
	2) We can cache sqrt(num_visits) (invalidate on change by setting to -1)
	We go from N * log + N * sqrt => 1 * log + 2 * sqrt (N == number of children)
	7 log + 7 sqrt => 1 * log + 2 * sqrt => ~4.7 times faster.
	Average run time went down from appx 32%.
	Expect better when we have more moves.
	*/
	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::best_child_fast(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->num_children == 0) return node_id;

		auto exploration_numerator = _c * sqrt(log(node->num_visits.load(memory_order_acquire)));

		auto best_score = -numeric_limits<float>::infinity();
		auto best_child_id = node->get_child_id(0);
		for (auto child_ndx = 0; child_ndx < node->num_children.load(memory_order_acquire); child_ndx++)
		{
			auto score = numeric_limits<float>::infinity();
			auto child_id = node->get_child_id(child_ndx);
			auto child = node_storage.get_node(child_id);

			if (child->num_visits == 0.0f)
			{
				best_child_id = child_id;
				break;
			}

			auto exploration = exploration_numerator / sqrt(child->num_visits.load(memory_order_acquire));
			auto exploitation = child->num_wins.load(memory_order_acquire) / child->num_visits.load(memory_order_acquire);

			score = exploration + exploitation;
			if (score > best_score)
			{
				best_score = score;
				best_child_id = child_id;
			}
		}
		return best_child_id;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline TNodeID MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::most_visited(TNodeID node_id)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return node_id;
		if (node->num_children == 0) return node_id;

		auto best_score = 0.0f;
		auto best_child_id = -1;
		for (auto child_ndx = 0; child_ndx < node->num_children.load(memory_order_acquire); child_ndx++)
		{
			auto child_id = node->get_child_id(child_ndx);
			auto child = node_storage.get_node(child_id);
			if (child == nullptr) continue;

			// check for instant win to avoid MCTS habit of 'delayed gratification'
			if (child->result != GameResult::keep_playing)
			{
				if (child->result == GameResult::player_0_win && node->player_to_move == 0 ||
					child->result == GameResult::player_1_win && node->player_to_move == 1)
				{
					best_child_id = child_id;
					break;
				}
			}

			auto score = child->num_visits.load(memory_order_acquire);
			if (child_ndx == 0 || score > best_score)
			{
				best_score = score;
				best_child_id = node->get_child_id(child_ndx);
			}

		}
		return best_child_id;
	}

	/*
	exploration = c * math.sqrt(math.log(self.parent.num_visits) / self.num_visits)
	exploitation = self.num_wins / self.num_visits
	*/
	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline float MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::ucb(TNodeID node_id, float c)
	{
		auto node = node_storage.get_node(node_id);
		if (node == nullptr) return 0.0f;

		auto parent = node_storage.get_node(node->parent_id);
		if (parent == nullptr) return 0.0f;

		if (node->num_visits == 0.0f) return numeric_limits<float>::infinity();

		auto exploration = c * sqrt(log(parent->num_visits.load(memory_order_acquire)) / node->num_visits.load(memory_order_acquire));
		auto exploitation = node->num_wins.load(memory_order_acquire) / node->num_visits.load(memory_order_acquire);

		return exploration + exploitation;
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline void MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::select_thread()
	{
		TNodeID id;
		while (select_queue.pop(id))
		{
			TNodeID new_id = select(id);
			expand_queue.push(new_id);
		}
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline void MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::expand_thread()
	{
		TNodeID id;
		while (expand_queue.pop(id))
		{
			TNodeID new_id = expand(id);
			rollout_queue_package<TNodeID> package;
			package.node_id = new_id;
			rollout_queue.push(package);
		}
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline void MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::rollout_thread()
	{
		rollout_queue_package<TNodeID> package;
		while (rollout_queue.pop(package))
		{
			rollout(package.node_id, package.rollout_result);
			back_propogate_queue.push(package);
		}
	}

	template<typename TGameRules, typename TNodeStorage, typename TNodeID, typename TPosition, typename TMoveType>
	inline void MCTSRGDAgent<TGameRules, TNodeStorage, TNodeID, TPosition, TMoveType>::back_propogate_thread()
	{
		rollout_queue_package<TNodeID> package;
		while (back_propogate_queue.pop(package))
		{
			back_propogate(package.node_id, package.rollout_result);
			select_queue.push(node_storage.get_root_id());
		}
	}

}

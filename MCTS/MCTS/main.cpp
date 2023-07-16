#include <iostream>
#include <time.h>
#include <chrono>
#include <thread>
#include <array>
#include <bitset>
#include <map>
#include "PerfTimer.h"

#include "test_game.h"
#include "TicTacToe.h"
#include "Connect4.h"
#include "backgammon.h"

#include "Node.h"
#include "NodeRGD.h"
#include "MCTSAgent.h"
#include "MCTSRGDAgent.h"
#include "RandomAgent.h"
#include "ConsoleAgent.h"

using namespace NodeNS;
using namespace NodeRGDNS;

template <typename TPositionType, typename TMoveType, typename TGameRules, typename TAgent0Type, typename TAgent1Type>
unsigned int play_games(TAgent0Type& agent_0, TAgent1Type& agent_1, unsigned int games = 1, bool show = true)
{
	TPositionType position;
	unsigned int player = 0;
	MoveResult<TPositionType> move_result;
	map<string, unsigned int> results{
		{ "Player 0", 0u },
		{ "Player 1", 0u },
		{ "Tie", 0u }
	};
	unsigned int total_moves = 0u;

	for (auto x = 0u; x < games; x++)
	{
		player = x % 2;
		if (show) cout << "----------" << endl;
		if (!show)
		{
			if (x % 100 == 0)
			{
				cout << " " << x << "/" << games;
				cout << "(" << results["Player 0"] << ", " << results["Player 1"] << ", " << results["Tie"] << ")" << endl;
			}
			cout << '.';
		}
		TGameRules::get_initial_position(position);
		if (show) TGameRules::render(position);

		while (true)
		{
			TMoveType move = 0;
			if (player == 0)
			{
				unordered_map<TMoveType, float> choice_map;
				choice_map.clear();
				if (!agent_0.choose_move(position, player, move))
				{
					results["Tie"]++;
					if (show) cout << " Tie." << endl;
					break;
				}
			}
			else
			{
				if (!agent_1.choose_move(position, player, move))
				{
					results["Tie"]++;
					if (show) cout << " Tie." << endl;
					break;
				}
			}
			total_moves++;

			TGameRules::move(position, player, move, move_result);
			if (show) cout << " Move: " << bitset <sizeof(TMoveType) * 8>(move) << endl;

			position = move_result.position;
			player = move_result.next_players_turn;
			if (show) TGameRules::render(position);

			if (move_result.result == GameResult::player_0_win || move_result.result == GameResult::player_1_win)
			{
				if (move_result.result == GameResult::player_0_win)
				{
					results["Player 0"]++;
				}
				else
				{
					results["Player 1"]++;
				}
				if (show) cout << " " << (move_result.result == GameResult::player_0_win ? "Player 0" : "Player 1") << " wins!" << endl;
				break;
			}
		}
	}
	cout << endl;
	for (auto pair : results)
	{
		cout << pair.first << ": " << pair.second << endl;
	}
	return total_moves;
}

//using namespace TestGameNS;
//using namespace TicTacToeNS;
using namespace Connect4NS;

int main()
{
	BackgammonNS::MoveList move_list;
	BackgammonNS::Backgammon::run_position_tests("C:\\GitHub\\RL\\MCTS\\MCTS\\test_games.txt");
	return 0;

	BackgammonNS::PositionType bgposition;
	BackgammonNS::Backgammon::get_initial_position(bgposition);
	//BackgammonNS::Backgammon::position_from_string("W02  0  0  0  0B05  0B03  0  0  0W05B05  0  0  0W03  0W05  0  0  0  0B02  0  0", bgposition);
	//BackgammonNS::Backgammon::position_from_string(  "B02B02B02B02B02B04B01  0  0  0  0  0  0  0  0  0  0W01W04W02W02W02W02W02  0  0", bgposition);
	//BackgammonNS::Backgammon::position_from_string("  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0", bgposition);
	BackgammonNS::Backgammon::position_from_string("B06B03  0  0  0B01B01  0  0B01  0  0  0B01  0  0  0  0  0  0B01  0W01B01  0  0", bgposition);
	//bgposition.position[0] = 0b0000100101001000001100010000110010100101000110001000000000000011;
	//bgposition.position[1] = 0b0000100010000000000100010000110001001010000010001000010001100000;

	for (auto roll = 0; roll < 1; roll++)
	{
		BackgammonNS::Backgammon::render(bgposition);
		BackgammonNS::Backgammon::generate_legal_moves(bgposition, 0, 4, move_list);
		move_list.dump_moves(1);
		//unsigned int ndx = 0;
		//while (true)
		//{
		//	auto move = move_list.get_legal_move(ndx);
		//	if (!move) break;
		//	cout << bitset<64>(move.value().result_position.position[0]) << " ";
		//	cout << bitset<64>(move.value().result_position.position[1]) << " " << endl;
		//}
		//BackgammonNS::Backgammon::render(bgposition);
		//BackgammonNS::Backgammon::get_legal_moves(bgposition, 1, roll);
	}
	return 0;

	const unsigned thread_count = std::thread::hardware_concurrency();
	cout << thread_count << endl;

	//auto node = Node<int, Connect4NS::PositionType, Connect4NS::MoveType>();
	//node.show_size();

	typedef  NodeContainerArrayRGD<PositionType, MoveType, 10000000> node_container_RGD;
	typedef MCTSRGDAgentNS::MCTSRGDAgent<Connect4, node_container_RGD, int, PositionType, MoveType> MCTSRGDAgentType;
	MCTSRGDAgentType mcts_rgd_agent(100000, 42, 1, 1, 1, 1);

	typedef  NodeContainerArray<PositionType, MoveType, 10000000> node_container;
	typedef MCTSAgentNS::MCTSAgent<Connect4, node_container, int, PositionType, MoveType> MCTSAgentType;
	MCTSAgentType mcts_agent(100000);

	typedef RandomAgentNS::RandomAgent<Connect4, PositionType, MoveType> RandomAgentType;
	auto seed = (uint32_t)time(NULL);
	cout << "Seed: " << seed << endl;
	RandomAgentType random_agent(seed);

	typedef ConsoleAgentNS::ConsoleAgent<Connect4, PositionType, MoveType> ConsoleAgentType;
	ConsoleAgentType console_agent;

	PerfTimer pf(true, true, true);
	pf.start();
	//auto moves = play_games<PositionType, MoveType, Connect4, MCTSRGDAgentType, ConsoleAgentType>(mcts_rgd_agent, console_agent, 10, true);
	//auto moves = play_games<PositionType, MoveType, Connect4, ConsoleAgentType, MCTSRGDAgentType>(console_agent, mcts_rgd_agent, 10, true);
	auto moves = play_games<PositionType, MoveType, Connect4, MCTSAgentType, MCTSRGDAgentType>(mcts_agent, mcts_rgd_agent, 10, false);
		//mcts_rgd_agent.clear_back_propogates();
	//auto moves = play_games<PositionType, MoveType, Connect4, MCTSAgentType, MCTSRGDAgentType>(mcts_agent, mcts_rgd_agent, 10, false);
	cout << "Total Moves:   " << moves << endl;
	cout << "BPS (MCTS):    " << mcts_agent.get_num_back_propogates() << endl;
	cout << "BPS (MCTSRGD): " << mcts_rgd_agent.get_num_back_propogates() << endl;
	cout << "Cycles / move: " << (float)mcts_rgd_agent.get_num_back_propogates() / (float)moves << endl;
	//mcts_rgd_agent.add_select_thread();
	//mcts_rgd_agent.add_rollout_thread();
	//mcts_rgd_agent.add_back_propogate_thread();
//auto moves = play_games<PositionType, MoveType, Connect4, MCTSRGDAgentType, MCTSRGDAgentType>(mcts_rgd_agent, mcts_rgd_agent, 10, true);
	pf.stop();
	pf.print();

}


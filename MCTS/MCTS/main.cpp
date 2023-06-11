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
#include "Node.h"
#include "MCTSAgent.h"
#include "RandomAgent.h"
#include "ConsoleAgent.h"

template <typename TPositionType, typename TMoveType, typename TGameRules, typename TAgent0Type, typename TAgent1Type>
void play_games(TAgent0Type& agent_0, TAgent1Type& agent_1, unsigned int games = 1, bool show=true)
{
	TPositionType position;
	unsigned int player = 0;
	MoveResult<TPositionType> move_result;
	map<string, unsigned int> results{
		{ "Player 0", 0u },
		{ "Player 1", 0u },
		{ "Tie", 0u }
	};

	for (auto x = 0u; x < games; x++)
	{
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

			TGameRules::move(position, player, move, move_result);
			if (show) cout << " Move: " << bitset <sizeof(TMoveType) * 8> (move) << endl;

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
}

//using namespace TestGameNS;
using namespace TicTacToeNS;

int main()
{
	//auto node = Node<int, TicTacToeNS::PositionType, TicTacToeNS::MoveType>();
	//node.show_size();

	typedef  NodeContainerArray<PositionType, MoveType, 1000000> node_container;
	typedef MCTSAgentNS::MCTSAgent<TicTacToe, node_container, int, PositionType, MoveType> MCTSAgentType;
	MCTSAgentType mcts_agent;

	typedef RandomAgentNS::RandomAgent<TicTacToe, PositionType, MoveType> RandomAgentType;
	auto seed = (uint32_t)time(NULL);
	seed = 1686510551;
	cout << "Seed: " << seed << endl;
	RandomAgentType random_agent(seed);

	typedef ConsoleAgentNS::ConsoleAgent<TicTacToe, PositionType, MoveType> ConsoleAgentType;
	ConsoleAgentType console_agent;
	
	PerfTimer pf(true, true, true);
	pf.start();
	play_games<PositionType, MoveType, TicTacToe, MCTSAgentType, MCTSAgentType>(mcts_agent, mcts_agent, 1, true);
	pf.stop();
	pf.print();
}


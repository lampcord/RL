#include <iostream>
#include <time.h>
#include <chrono>
#include <thread>
#include <array>
#include <bitset>
#include "PerfTimer.h"
#include "Node.h"
#include "test_game.h"
#include "MCTSAgent.h"
#include "RandomAgent.h"
#include "TicTacToe.h"

template <typename TPositionType, typename TMoveType, typename TGameRules, typename TAgentType>
void play_games(TAgentType& agent)
{
	TPositionType position;
	unsigned int player = 0;
	MoveResult<TPositionType> move_result;

	for (auto x = 0u; x < 1; x++)
	{
		cout << "----------" << endl;
		TGameRules::get_initial_position(position);
		TGameRules::render(position);

		while (true)
		{
			TMoveType move = 0;
			if (!agent.choose_move(position, player, move))
			{
				cout << " Tie." << endl;
				break;
			}
			TGameRules::move(position, player, move, move_result);
			cout << " Move: " << bitset <sizeof(TMoveType) * 8> (move) << endl;

			position = move_result.position;
			player = move_result.next_players_turn;
			TGameRules::render(position);

			if (move_result.result == GameResult::player_0_win || move_result.result == GameResult::player_1_win)
			{
				cout << " " << (move_result.result == GameResult::player_0_win ? "Player 0" : "Player 1") << " wins!" << endl;
				break;
			}
		}
	}
}

using namespace TestGameNS;
//using namespace RandomAgentNS;
//using namespace MCTSAgentNS;

int main()
{
	auto node = Node<int, TicTacToeNS::PositionType, TicTacToeNS::MoveType, 9u>();
	node.show_size();

	typedef  NodeContainerArray<PositionType, MoveType, 1000000, NumChildren> node_container;
	typedef MCTSAgentNS::MCTSAgent<TestGame, node_container, int, PositionType, MoveType> MCTSAgentType;
	MCTSAgentType Agent;

	//typedef RandomAgentNS::RandomAgent<TestGame, PositionType, MoveType> RandomAgentType;
	//RandomAgentType Agent;
	
	PerfTimer pf(true, true, true);
	pf.start();
	//play_games<PositionType, MoveType, TestGame, MCTSAgent<TestGame, node_container, int, PositionType, MoveType>>(Agent);
	play_games<PositionType, MoveType, TestGame, MCTSAgentType>(Agent);
	pf.stop();
	pf.print();
}


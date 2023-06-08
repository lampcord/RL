#include <iostream>
#include <time.h>
#include <chrono>
#include <thread>
#include <array>
#include "PerfTimer.h"
#include "Node.h"
#include "test_game.h"
#include "MCTSAgent.h"
#include "RandomAgent.h"

using namespace TestGameNS;
//using namespace RandomAgentNS;
using namespace MCTSAgentNS;

int main()
{
	PositionType position;
	unsigned int player = 0;
	MoveResult<PositionType> move_result;

	typedef  NodeContainerArray<PositionType, MoveType, 1000000, 4> node_container;
	MCTSAgent<TestGame, node_container, int, PositionType, MoveType>Agent;

	//RandomAgent<TestGame, PositionType, MoveType>Agent;

	PerfTimer pf(true, true, true);
	pf.start();
	for (auto x = 0u; x < 1; x++)
	{
		cout << "----------" << endl;
		TestGame::get_initial_position(position);
		TestGame::render(position);

		while (true)
		{
			MoveType move;
			if (!Agent.choose_move(position, player, move))
			{
				cout << "Tie." << endl;
				break;
			}
			TestGame::move(position, player, move, move_result);

			position = move_result.position;
			player = move_result.next_players_turn;
			TestGame::render(position);

			if (move_result.result == GameResult::player_0_win || move_result.result == GameResult::player_1_win)
			{
				cout << (move_result.result == GameResult::player_0_win ? "Player 0" : "Player 1") << " wins!" << endl;
				break;
			}
		}
	}
	pf.stop();
	pf.print();
	
}


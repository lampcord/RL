#include <iostream>
#include <time.h>
#include "PerfTimer.h"
#include "Node.h"
#include "test_game.h"
#include "MCTS.h"
#include <chrono>
#include <thread>
#include <array>
#include "squirrel3.h"

using namespace TestGameNS;

int main()
{
	Squirrel3 rng(42);

	//typedef  NodeContainerArray<PositionType, 100, 4> node_container;
	//MCTS<TestGame, node_container, int, MoveType>mcts;
	//mcts.find_move(position, player);

	PositionType position;
	MoveType legal_moves;
	unsigned int player = 0;
	MoveResult<PositionType> move_result;

	for (auto x = 0u; x < 10; x++)
	{
		cout << "----------" << endl;
		TestGame::get_initial_position(position);
		TestGame::render(position);

		TestGame::get_legal_moves(position, player, legal_moves);
		auto num_moves = get_num_moves<MoveType>(legal_moves);
		while (num_moves > 0)
		{
			auto move = get_nth_move<MoveType>(legal_moves, rng() % num_moves);
			TestGame::move(position, player, move, move_result);

			position = move_result.position;
			player = move_result.next_players_turn;
			TestGame::render(position);

			if (move_result.result == GameResult::player_0_win || move_result.result == GameResult::player_1_win)
			{
				cout << (move_result.result == GameResult::player_0_win ? "Player 0" : "Player 1") << " wins!" << endl;
				break;
			}

			TestGame::get_legal_moves(position, player, legal_moves);
			num_moves = get_num_moves<MoveType>(legal_moves);
		}
	}
	
}


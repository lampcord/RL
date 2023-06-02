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

int main()
{
	typedef  NodeContainerArray<unsigned char, 100, 4> node_container;

	MCTS<TestGame, node_container, int, unsigned char>mcts;

	unsigned char position;
	unsigned char legal_moves;
	unsigned int turn = 0;

	TestGame::get_initial_position(position);
	TestGame::get_legal_moves(position, turn, legal_moves);
	auto num_moves = get_num_moves<unsigned char>(legal_moves);
	for (auto x = 0u; x < num_moves; x++)
	{
		auto move = get_nth_move(legal_moves, x);
		cout << (unsigned int)move << endl;
	}

	mcts.find_move(position, turn);
}


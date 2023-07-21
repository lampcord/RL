#include <iostream>
#include "backgammon.h"
#include "analyzer.h"
#include "movelist.h"
#include "squirrel3.h"

using namespace BackgammonNS;
using namespace std;

int main()
{
	Squirrel3 rng(42);
	std::unique_ptr<MoveList> move_list = std::make_unique<MoveList>();
	Backgammon::run_position_tests("C:\\GitHub\\RL\\test_games.txt", false, *move_list);
	return 0;

	unsigned char player = 0;
	PositionStruct position;
	Backgammon::get_initial_position(position);
	Backgammon::render(position, 0);
	auto roll = rng() % 36;
	roll = 2;
	Backgammon::generate_legal_moves(position, player, roll, *move_list, true);
	//auto num_moves = move_list->get_number_of_moves();
	move_list->dump_moves(0);
	//if (num_moves > 0)
	//{
	//	auto move = move_list->get_legal_move(rng() % num_moves);
	//}
	//Backgammon::render(position, 1);
	//Analyzer::analyze(position);
	//delete move_list;
}


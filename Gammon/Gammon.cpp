#include <iostream>
#include "backgammon.h"

using namespace BackgammonNS;

int main()
{
	MoveList move_list;
	PositionStruct position;
	Backgammon::get_initial_position(position);
	Backgammon::position_from_string("@02  0  0  0  0B05  0B04  0  0  0W03B04  0  0  0W02W01W03B01  0W02  0W02  0  1", position);
	Backgammon::render(position);
	Analyzer::analyze(position);

	//Backgammon::run_position_tests("C:\\GitHub\\RL\\test_games.txt", false);
}


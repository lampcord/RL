#include <iostream>
#include "backgammon.h"

int main()
{
	BackgammonNS::MoveList move_list;
	BackgammonNS::Backgammon::run_position_tests("C:\\GitHub\\RL\\test_games.txt", false);
}


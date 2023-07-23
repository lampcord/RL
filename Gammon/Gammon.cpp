#include <iostream>
#include <iomanip>
#include "backgammon.h"
#include "analyzer.h"
#include "movelist.h"
#include "squirrel3.h"
#include "Gammon.h"
#include "PerfTimer.h"

using namespace BackgammonNS;
using namespace std;

int main()
{
	cout << "===================================================================================================================================" << endl;
	cout << "===================================================================================================================================" << endl;
	cout << "=                                                                                                                                 =" << endl;
	cout << "=                                                                                                                                 =" << endl;
	cout << "=                                                                                                                                 =" << endl;
	cout << "===================================================================================================================================" << endl;
	cout << "===================================================================================================================================" << endl;
	std::unique_ptr<MoveList> move_list = std::make_unique<MoveList>();
	std::unique_ptr<MoveList> rollout_move_list = std::make_unique<MoveList>();
	
	//Backgammon::run_position_tests("C:\\GitHub\\RL\\test_games.txt", false, *move_list);
	//return 0;

	auto num_games = 10000u;
	unsigned char player = 1;
	Squirrel3 rng(42);
	PositionStruct position;
	Backgammon::get_initial_position(position);

	auto roll = 14;
	Backgammon::render(position, player);
	Backgammon::generate_legal_moves(position, player, roll, *move_list, true);
	Analyzer::get_best_move_index(position, *move_list, player, true);
	return 0;

	for (auto ndx = 0u; ndx < move_list->move_list_ndx_size; ndx++)
	{
		auto move_set = move_list->move_list[move_list->move_list_ndx[ndx]];
		print_move_set(move_set, player);
		
		auto score = Analyzer::analyze(move_set.result_position, player);

		auto rollout_score = rollout(move_set.result_position, 1 - player, rollout_move_list, num_games, rng, false);
		
		auto average_rollout_score = rollout_score / num_games;
		
		auto average_score = (-average_rollout_score + score) / 2.0f;

		cout << "Score " << setw(6) << score << " Average rollout score " << setw(6) << average_rollout_score << " Average score " << setw(6) << average_score << endl;
	}
}

float rollout(PositionStruct &position, unsigned char player, std::unique_ptr<BackgammonNS::MoveList>& move_list, unsigned int num_games, Squirrel3& rng, bool display)
{
	auto total_moves = 0u;
	//PerfTimer pf(true, true, true);

	//pf.start();
	float total_score = 0.0f;
	const auto max_moves = 20u;
	for (auto game_num = 0u; game_num < num_games; game_num++)
	{
		auto rollout_player = player;
		auto rollout_position = position;
		int winner = 0;
		auto moves_this_round = 0u;

		while (winner == 0 && moves_this_round < max_moves)
		{
			auto roll = rng() % 36;
			if (display)
			{
				Backgammon::render(rollout_position, rollout_player);
				auto die1 = roll % 6 + 1;
				auto die2 = roll / 6 + 1;
				cout << "Roll: " << (int)die1 << ", " << (int)die2 << endl;
			}
			Backgammon::generate_legal_moves(rollout_position, rollout_player, roll, *move_list, true);
			if (move_list->move_list_ndx_size > 0)
			{
				auto move_ndx = rng() % move_list->move_list_ndx_size;
				auto move_set = move_list->move_list[move_list->move_list_ndx[move_ndx]];
				rollout_position = move_set.result_position;
				if (display)
				{
					print_move_set(move_set, rollout_player);
				}
			}
			moves_this_round += 1;
			rollout_player = 1 - rollout_player;
			winner = Backgammon::get_winner(rollout_position);
			total_moves++;
		}
		if (winner == 0)
		{
			total_score += Analyzer::analyze(rollout_position, player);
		}
		else
		{
			total_score += player == 0 ? winner : -winner;
		}

		if (display)
		{
			Backgammon::render(rollout_position, rollout_player);
			cout << "Winner: " << winner << endl;
		}
	}
	//pf.stop();
	//pf.print();
	//cout << "Total moves: " << total_moves << " " << (float)total_moves * 10000000.0f / (float) pf.GetElapsedThreadTime() << endl;
	//cout << pf.GetElapsedThreadTime() << endl;

	return total_score;
}

void print_move_set(BackgammonNS::MoveStruct& move_set, unsigned char rollout_player)
{
	cout << MoveList::get_move_desc(move_set, rollout_player) << endl;
}


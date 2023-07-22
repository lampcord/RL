#include <iostream>
#include <bitset>
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
	
	//Backgammon::run_position_tests("C:\\GitHub\\RL\\test_games.txt", false, *move_list);
	//return 0;

	auto num_games = 20000u;
	Squirrel3 rng(42);


	play_random_games(rng, move_list, num_games, false);
}

void play_random_games(Squirrel3& rng, std::unique_ptr<BackgammonNS::MoveList>& move_list, unsigned int & num_games, bool display)
{
	PositionStruct position;
	unsigned char player = 0;
	auto total_moves = 0u;
	PerfTimer pf(true, true, true);

	pf.start();
	for (auto game_num = 0u; game_num < num_games; game_num++)
	{
		Backgammon::get_initial_position(position);
		int winner = 0;

		while (winner == 0)
		{
			auto roll = rng() % 36;
			if (display)
			{
				Backgammon::render(position, player);
				auto die1 = roll % 6 + 1;
				auto die2 = roll / 6 + 1;
				cout << "Roll: " << (int)die1 << ", " << (int)die2 << endl;
			}
			Backgammon::generate_legal_moves(position, player, roll, *move_list, true);
			if (move_list->move_list_ndx_size > 0)
			{
				auto move_ndx = rng() % move_list->move_list_ndx_size;
				auto move_set = move_list->move_list[move_list->move_list_ndx[move_ndx]];
				position = move_set.result_position;
				if (display)
				{
					for (auto y = 0u; y < 4; y++)
					{
						auto move = move_set.moves[y];
						if (move == 0) break;
						auto slot = (move & 0b11111000) >> 3;
						auto display_slot = player == 0 ? 24 - slot : slot + 1;
						auto die = (move & 0b111);
						auto slot_desc = slot == (bar_indicator >> 3) ? "bar" : to_string(display_slot);
						cout << "Moved a " << die << " from " << slot_desc << endl;
					}
				}
			}
			player = 1 - player;
			winner = Backgammon::get_winner(position);
			total_moves++;
		}

		if (display)
		{
			Backgammon::render(position, player);
			cout << "Winner: " << winner << endl;
		}
	}
	pf.stop();
	pf.print();
	cout << "Total moves: " << total_moves << " " << (float)total_moves * 10000000.0f / (float) pf.GetElapsedThreadTime() << endl;
	cout << pf.GetElapsedThreadTime() << endl;
}


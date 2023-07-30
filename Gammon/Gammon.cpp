#include <iostream>
#include <iomanip>
#include "backgammon.h"
#include "analyzer.h"
#include "movelist.h"
#include "squirrel3.h"
#include "Gammon.h"
#include "PerfTimer.h"
#include "console_agent.h"
#include "random_agent.h"
#include "analyzer_agent.h"

using namespace BackgammonNS;
using namespace std;
static MoveList hit_move_list;

template<typename TAgentType0, typename TAgentType1>
inline void play_games(BackgammonNS::PositionStruct& position, unsigned char player, std::unique_ptr<BackgammonNS::MoveList>& move_list, Squirrel3& rng, TAgentType0& agent_0, TAgentType1& agent_1, bool verbose=true)
{
	auto winner = 0;
	while (winner == 0)
	{
		auto roll = rng() % 36;
		//roll = 0;
		if (verbose)
		{
			BackgammonNS::Backgammon::render(position, player);
			Analyzer::get_number_of_hits(position, player, hit_move_list);
			auto die1 = roll % 6 + 1;
			auto die2 = roll / 6 + 1;
			std::cout << "Roll: " << (int)die1 << ", " << (int)die2 << std::endl;
		}
		//auto num_rolls = Analyzer::get_number_of_rolls_that_hit(position, player, hit_move_list, false);
		//cout << Backgammon::string_from_position(position) << setw(3) << (int)player << setw(3) << num_rolls << endl;

		if (player == 0)
		{
			agent_0.get_move(position, player, roll, move_list, rng, verbose);
		}
		else
		{
			agent_1.get_move(position, player, roll, move_list, rng, verbose);
		}

		winner = BackgammonNS::Backgammon::get_winner(position);
		player = 1 - player;
	}
	if (verbose)
	{
		BackgammonNS::Backgammon::render(position, player);
		Analyzer::get_number_of_hits(position, player, hit_move_list);
	}
	//auto num_rolls = Analyzer::get_number_of_rolls_that_hit(position, player, hit_move_list, false);
	//cout << Backgammon::string_from_position(position) << setw(3) << (int)player << setw(3) << num_rolls << endl;

}

int main()
{
	cout << "=============================================================================================================================================" << endl;
	cout << "=============================================================================================================================================" << endl;
	cout << "=                                                                                                                                           =" << endl;
	cout << "=     >=>>=>          >>           >=>    >=>   >=>      >===>          >>       >=>       >=> >=>       >=>     >===>      >==>    >=>     =" << endl;
	cout << "=     >>   >=>       >>=>       >=>   >=> >=>  >=>     >>    >=>       >>=>      >> >=>   >>=> >> >=>   >>=>   >=>    >=>   >> >=>  >=>     =" << endl;
	cout << "=     >>    >=>     >> >=>     >=>        >=> >=>     >=>             >> >=>     >=> >=> > >=> >=> >=> > >=> >=>        >=> >=> >=> >=>     =" << endl;
	cout << "=     >==>>=>      >=>  >=>    >=>        >>=>>       >=>            >=>  >=>    >=>  >=>  >=> >=>  >=>  >=> >=>        >=> >=>  >=>>=>     =" << endl;
	cout << "=     >>    >=>   >=====>>=>   >=>        >=>  >=>    >=>   >===>   >=====>>=>   >=>   >>  >=> >=>   >>  >=> >=>        >=> >=>   > >=>     =" << endl;
	cout << "=     >>     >>  >=>      >=>   >=>   >=> >=>   >=>    >=>    >>   >=>      >=>  >=>       >=> >=>       >=>   >=>     >=>  >=>    >>=>     =" << endl;
	cout << "=     >===>>=>  >=>        >=>    >===>   >=>     >=>   >====>    >=>        >=> >=>       >=> >=>       >=>     >===>      >=>     >=>     =" << endl;
	cout << "=                                                                                                                                           =" << endl;
	cout << "=============================================================================================================================================" << endl;
	cout << "=============================================================================================================================================" << endl;
	//Analyzer::test_board_structure();
	//return 0;

	std::unique_ptr<MoveList> move_list = std::make_unique<MoveList>();
	std::unique_ptr<MoveList> rollout_move_list = std::make_unique<MoveList>();
	
	Analyzer::test_number_of_hits("C:\\GitHub\\RL\\test_hits.txt" , *move_list);
	return 0;

	//Backgammon::run_position_tests("C:\\GitHub\\RL\\test_games.txt", false, *move_list);
	//return 0;

	auto num_games = 10000u;
	unsigned char player = 0;
	Squirrel3 rng(42);
	PositionStruct position;
	Backgammon::get_initial_position(position);

	ConsoleAgentNS::ConsoleAgent console_agent;
	RandomAgentNS::RandomAgent random_agent;
	AnalyzerAgentNS::AnalyzerAgent analyzer_agent;

	//play_games<ConsoleAgentNS::ConsoleAgent, RandomAgentNS::RandomAgent>(position, player, move_list, rng, console_agent, random_agent);
	//play_games<RandomAgentNS::RandomAgent, RandomAgentNS::RandomAgent>(position, player, move_list, rng, random_agent, random_agent);
	play_games<ConsoleAgentNS::ConsoleAgent, AnalyzerAgentNS::AnalyzerAgent>(position, player, move_list, rng, console_agent, analyzer_agent, true);
	//for (auto x = 0; x < 1000; x++) {
	//	Backgammon::get_initial_position(position);
	//	play_games<AnalyzerAgentNS::AnalyzerAgent, AnalyzerAgentNS::AnalyzerAgent>(position, player, move_list, rng, analyzer_agent, analyzer_agent, false);
	//}
	//play_games<RandomAgentNS::RandomAgent, AnalyzerAgentNS::AnalyzerAgent>(position, player, move_list, rng, random_agent, analyzer_agent);
	return 0;

	auto roll = 0;
	Backgammon::render(position, player);
	Backgammon::generate_legal_moves(position, player, roll, *move_list, true);
	Analyzer::get_best_move_index(position, *move_list, player, true);
	return 0;

}


float rollout(const PositionStruct &position, unsigned char player, std::unique_ptr<BackgammonNS::MoveList>& move_list, unsigned int num_games, Squirrel3& rng, bool display)
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
			AnalyzerScan scan;
			Analyzer::scan_position(rollout_position, scan);
			total_score += Analyzer::analyze(scan, player, BoardStructure::unclear, BoardStructure::unclear);
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


#include <iostream>
#include "console_agent.h"
#include "analyzer.h"

namespace ConsoleAgentNS
{
	using namespace BackgammonNS;
	using namespace std;

	void ConsoleAgentNS::ConsoleAgent::get_move(BackgammonNS::PositionStruct& position, unsigned char player, unsigned int roll, unique_ptr<BackgammonNS::MoveList>& move_list, Squirrel3& rng, bool verbose)
	{
		BackgammonNS::Backgammon::generate_legal_moves(position, player, roll, *move_list, false);
		PositionStruct display_position = position;
		std::vector<unsigned char> moves_so_far;
		while (true)
		{
			auto moves = move_list->get_all_single_moves(position, moves_so_far);
			if (moves.size() == 0) break;
			char move_char = 'a';
			for (auto move : moves)
			{
				cout << move_char++ << ") ";
				display_move(move, player);
			}
			unsigned char choice;
			cin >> choice;
			int move_ndx = choice - 'a';
			if (move_ndx >= 0 && move_ndx < moves.size())
			{
				cout << "Your move: ";
				auto move = moves[move_ndx];
				display_move(move, player);
				moves_so_far.push_back(move);
				display_position = move_list->get_position_for_partial_move(moves_so_far);
				Backgammon::render(display_position, player);
			}
			else
			{
				cout << "Invalid move." << endl;
			}
		}
		position = display_position;
	}
	void ConsoleAgent::display_move(const unsigned char& move, unsigned char player)
	{
		auto die = move & 0b111;
		auto slot = (move >> 3);
		auto adjusted_slot = player == 0 ? 24 - slot : slot + 1;
		if (slot == (bar_indicator >> 3)) cout << "Die " << (int)die << " From Bar " << endl;
		else cout << "Die " << (int)die << " From " << (int)adjusted_slot << endl;
	}
}

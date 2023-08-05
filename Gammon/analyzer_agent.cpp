#include "analyzer_agent.h"
#include "analyzer.h"

using namespace BackgammonNS;
using namespace std;;

namespace AnalyzerAgentNS
{
	void AnalyzerAgent::get_move(PositionStruct& position, unsigned char player, unsigned int roll, unique_ptr<MoveList>& move_list, Squirrel3& rng, bool verbose)
	{
		TStructVec struct_v;

		Backgammon::generate_legal_moves(position, player, roll, *move_list, true);
		auto best_ndx = Analyzer::get_best_move_index(position, *move_list, player, struct_v, verbose);
		if (best_ndx >= 0)
		{
			auto best_move_set = move_list->move_list[move_list->move_list_ndx[best_ndx]];
			if (verbose) cout << "Best Move: " << MoveList::get_move_desc(best_move_set, player) << endl;
			position = best_move_set.result_position;
		}
		else
		{
			if (verbose) cout << "No Moves." << endl;
		}
	}
}
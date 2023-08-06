#include "analyzer_agent.h"
#include "analyzer.h"

using namespace BackgammonNS;
using namespace std;

namespace AnalyzerAgentNS
{
	static bool struct_v_loaded = false;

	void AnalyzerAgent::get_move(PositionStruct& position, unsigned char player, unsigned int roll, std::unique_ptr<BackgammonNS::AnalyzerState>& state, bool verbose)
	{
		Backgammon::generate_legal_moves(position, player, roll, state->move_list, true);
		auto best_ndx = Analyzer::get_best_move_index(position, *state, player, verbose);
		if (best_ndx >= 0)
		{
			auto best_move_set = state->move_list.move_list[state->move_list.move_list_ndx[best_ndx]];
			if (verbose) cout << "Best Move: " << MoveList::get_move_desc(best_move_set, player) << endl;
			position = best_move_set.result_position;
		}
		else
		{
			if (verbose) cout << "No Moves." << endl;
		}
	}
}
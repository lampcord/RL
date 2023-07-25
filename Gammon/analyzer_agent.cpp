#include "analyzer_agent.h"
#include "analyzer.h"

using namespace BackgammonNS;
using namespace std;;

namespace AnalyzerAgentNS
{
	void AnalyzerAgent::get_move(PositionStruct& position, unsigned char player, unsigned int roll, unique_ptr<MoveList>& move_list, Squirrel3& rng)
	{
		Backgammon::generate_legal_moves(position, player, roll, *move_list, true);
		auto best_ndx = Analyzer::get_best_move_index(position, *move_list, player, true);
		position = move_list->move_list[move_list->move_list_ndx[best_ndx]].result_position;
	}
}
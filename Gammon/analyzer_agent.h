#pragma once
#include "backgammon.h"
#include "squirrel3.h"
#include "movelist.h"
#include "analyzer.h"
#include <memory>

namespace AnalyzerAgentNS
{
	class AnalyzerAgent
	{
	public:
		static void get_move(BackgammonNS::PositionStruct& position, unsigned char player, unsigned int roll, std::unique_ptr<BackgammonNS::AnalyzerState>& state, bool verbose=true);
	};
}
#pragma once
#include "backgammon.h"
#include "squirrel3.h"
#include "movelist.h"
#include "analyzer.h"
#include <memory>

namespace ConsoleAgentNS
{
	class ConsoleAgent
	{
		static void display_move(const unsigned char& move, unsigned char player);
	public:
		static void get_move(BackgammonNS::PositionStruct& position, unsigned char player, unsigned int roll, std::unique_ptr<BackgammonNS::AnalyzerState>& state, bool verbose);
	};
}
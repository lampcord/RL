#pragma once
#include "backgammon.h"

namespace BackgammonNS
{
	struct AnalyzerResult
	{
		unsigned short pip_count[2] = { 0,0 };
		unsigned short board_strength[2] = { 0,0 };
		void render();
		void clear();
	};
	class Analyzer
	{
	private:
	public:
		static void scan_position(const PositionType& position, AnalyzerResult& result);
		static float analyze(const PositionType& position, unsigned char player);
	};
}

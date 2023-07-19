#pragma once
#include "backgammon.h"

namespace BackgammonNS
{
	class Analyzer
	{
	private:
	public:
		static std::tuple<unsigned int, unsigned int> get_pip_count(const PositionType& position);
		static float analyze(const PositionType& position);
	};
}

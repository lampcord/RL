#pragma once
#include "backgammon.h"
#include "movelist.h"

/*
Te 12 rules:
[ ] The most important point is the 5 point.
[ ] Make an outfield point.
[ ] Fight for a good point.
[ ] Break the mountain.
[ ] Keep at least 3 checkers on the mid-point.
[ ] To double hit is tiger play (weak tiger / strong tiger)
[ ] Attacking with 8 checkers is weak.
[ ] Attacking with 10 checkers is strong.
[ ] Split against the stripped 8 point.
[ ] Split against a prime.
[ ] Never split facing a blitzing structure.
[ ] Hit and split.
*/
namespace BackgammonNS
{
	struct AnalyzerResult
	{
		unsigned short pip_count[2] = { 0,0 };
		unsigned short in_the_zone[2] = { 0,0 };
		unsigned int blocked_points[2] = { 0,0 };
		unsigned int blots[2] = { 0,0 };
		unsigned int mountains[2] = { 0,0 };
		unsigned int triples[2] = { 0,0 };
		void render();
		void print_mask_desc(unsigned int mask);
		void clear();
	};
	class Analyzer
	{
	private:
	public:
		static unsigned short get_best_move_index(const PositionType& position, MoveList& move_list, unsigned char player, bool display);

		static void scan_position(const PositionType& position, AnalyzerResult& result);
		static float analyze(const PositionType& position, unsigned char player);
	};
}

#pragma once
#include <tuple>
#include <string>
#include "backgammon.h"
#include "movelist.h"

namespace BackgammonNS
{
	enum class Strategy {
		priming,
		blitzing,
		racing,
		contact
	};
	enum class Structure {
		unclear,
		prime,
		blitz
	};
	struct AnalyzerResult
	{
		unsigned short pip_count[2] = { 0,0 };
		unsigned short in_the_zone[2] = { 0,0 };
		float raw_mask_value[2] = { 0,0 };
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
		static std::string get_structure_desc(const Structure& structure);
		static unsigned short get_best_move_index(const PositionType& position, MoveList& move_list, unsigned char player, bool display);
		static std::tuple<Structure, Structure> get_structure(const PositionType& position, const AnalyzerResult& result);
		static void scan_position(const PositionType& position, AnalyzerResult& result);
		static float analyze(const PositionType& position, unsigned char player);
	};
}

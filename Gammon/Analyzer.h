#pragma once
#include <tuple>
#include <string>
#include <map>
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
	enum class BoardStructure {
		unclear,
		prime,
		blitz
	};
	struct AnalyzerScan
	{
		unsigned short pip_count[2] = { 0,0 };
		unsigned short in_the_zone[2] = { 0,0 };
		unsigned int structure[2] = { 0,0 };
		unsigned int impurity[2] = { 0,0 };
		unsigned int waste[2] = { 0, 0 };
		int first[2] = { -1, -1 };
		unsigned int last[2] = { 0, 0 };
		unsigned int mountains[2] = { 0, 0 };

		float raw_mask_value[2] = { 0,0 };
		unsigned int blocked_points_mask[2] = { 0,0 };
		unsigned int blots_mask[2] = { 0,0 };
		unsigned int mountains_mask[2] = { 0,0 };
		unsigned int triples_mask[2] = { 0,0 };
		void render();
		void print_mask_desc(unsigned int mask);
		void clear();
	};
	class Analyzer
	{
	private:
	public:
		static void dump_chart(std::string desc, std::map<int, std::vector<char>>& chart_structure);
		static std::string get_board_structure_desc(const BoardStructure& structure);
		static std::tuple<BoardStructure, BoardStructure> get_board_structure(const AnalyzerScan& scan);
		static bool test_board_structure();

		
		static unsigned short get_best_move_index(const PositionType& position, MoveList& move_list, unsigned char player, bool display);
		static void scan_position(const PositionType& position, AnalyzerScan& scan);
		static float analyze(AnalyzerScan& scan, unsigned char player, const BoardStructure& player_0_structure, const BoardStructure& player_1_structure);
	};
}

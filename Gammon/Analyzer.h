#pragma once
#include <tuple>
#include <string>
#include <map>
#include "backgammon.h"
#include "movelist.h"
#include "evaluation_vector.h"

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
	/*
	[X] Blocks in your home board
    [X] Location of high anchor
    [X] Location of high blot
    [X] Number of blocks in home board
    [X] Number of blots in home board
    [X] Checkers on bar
    [X] Purity
    [X] Raw block score
    [X] Raw checkers in range of slot
    [X] Raw slot score
	*/
	const unsigned int AC_pip_count = 0;
	const unsigned int AC_total_in_the_zone = 1;
	const unsigned int AC_anchors_in_opp_board = 2;
	const unsigned int AC_blots_in_opp_board = 3;
	const unsigned int AC_checkers_on_bar = 4;
	const unsigned int AC_location_of_high_anchor = 5;
	const unsigned int AC_location_of_high_blot = 6;
	const unsigned int AC_blocks_in_home_board = 7;
	const unsigned int AC_blots_in_home_board = 8;
	const unsigned int AC_structure = 9;
	const unsigned int AC_impurity = 10;
	const unsigned int AC_waste = 11;
	const unsigned int AC_first = 12;
	const unsigned int AC_last = 13;
	const unsigned int AC_mountains = 14;
	const unsigned int AC_raw_block_value = 15;
	const unsigned int AC_raw_slot_value = 16;
	const unsigned int AC_raw_range_value = 17;
	const unsigned int AC_hit_pct = 18;
	const unsigned int AC_blots_in_the_zone = 19;
	const unsigned int AC_stripped_in_the_zone = 20;
	const unsigned int AC_triples_in_the_zone = 21;
	const unsigned int AC_mountains_in_the_zone = 22;
	const unsigned int AC_max_value = 23;

	typedef EvaluationVector<11> TStructVec;

	struct AnalysisStat
	{
		float element[2];
	};
	struct AnalyzerVector
	{
		AnalysisStat stat[AC_max_value];
		void clear();
		void dump_stat_line(int player);
	};
	struct AnalyzerScan
	{
		AnalysisStat stat[AC_max_value];

		unsigned int blocked_points_mask[2] = { 0,0 };
		unsigned int blots_mask[2] = { 0,0 };
		unsigned int stripped_mask[2] = { 0,0 };
		unsigned int triples_mask[2] = { 0,0 };
		unsigned int mountains_mask[2] = { 0,0 };
		//unsigned int number_of_hits = 0;
		void render();
		void dump_stat_line(int player);
		void dump_stat_header();
		static void print_mask_desc(unsigned int mask);
		void clear();
	};
	class Analyzer
	{
	private:
		static void dump_block_mask_for_rolls();
	public:
		static std::string get_board_structure_desc(const BoardStructure& structure);
		static std::tuple<BoardStructure, BoardStructure> get_board_structure(const AnalyzerScan& scan, TStructVec& v, bool verbose = true);
		static std::tuple<float, float, TStructVec, TStructVec> get_board_structure_score(const AnalyzerScan& scan, TStructVec& v, bool verbose=true);
		static bool test_board_structure();

		static unsigned short get_number_of_hits(const PositionStruct& position, unsigned char player, MoveList& move_list, bool verbose = true);
		static unsigned short get_number_of_hits_fast(const PositionStruct& position, unsigned char player, AnalyzerScan& scan, bool verbose=true);
		static bool test_number_of_hits(std::string filename, MoveList& move_list);

		static short get_best_move_index(const PositionStruct& position, MoveList& move_list, unsigned char player, TStructVec& struct_v, bool verbose);
		static void scan_position(const PositionStruct& position, AnalyzerScan& scan);
		static float analyze(AnalyzerScan& scan, unsigned char player, const BoardStructure& player_0_structure, const BoardStructure& player_1_structure, bool verbose);
	};
}

#pragma once

template <typename TMoveType>
unsigned int get_num_moves(TMoveType move_mask)
{
	unsigned int num_moves = 0;

	TMoveType test_mask = 0b1;
	for (auto x = 0u; x < sizeof(move_mask) * 8u; x++)
	{
		if ((test_mask & move_mask) == test_mask) num_moves++;
		test_mask = test_mask << 1;
	}

	return num_moves;
}

enum class GameResult {
	player_0_win = 0,
	player_1_win = 1,
	tie = 2,
	keep_playing = 3
};

template <typename TPosition>
struct MoveResult {
	GameResult result;
	unsigned char next_players_turn;
	TPosition position;
};
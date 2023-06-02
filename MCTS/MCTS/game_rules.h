#pragma once

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
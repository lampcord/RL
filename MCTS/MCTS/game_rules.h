#pragma once

namespace GameRulesNS
{
	template <typename TMoveType>
	TMoveType get_first_move(const TMoveType& move_mask)
	{
		if (move_mask == 0) return 0;
		unsigned long index;

		_BitScanForward64(&index, move_mask);
		return 0b1 << index;
	}

	template <typename TMoveType>
	void clear_nth_move(TMoveType& move_mask, unsigned int n)
	{
		TMoveType move = 0;

		TMoveType test_mask = 0b1;
		unsigned int num_moves = 0;
		for (auto x = 0u; x < sizeof(move_mask) * 8u; x++)
		{
			if ((test_mask & move_mask) == test_mask)
			{
				if (n == num_moves)
				{
					move_mask &= ~test_mask;
					break;
				}
				num_moves++;
			}
			test_mask = test_mask << 1;
		}
	}

	// NOTE:
	// There is an intrinsic function for this
	//
	template <typename TMoveType>
	unsigned int get_num_moves(const TMoveType& move_mask)
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

	template <typename TMoveType>
	TMoveType get_nth_move(const TMoveType& move_mask, unsigned int n)
	{
		TMoveType move = 0;

		TMoveType test_mask = 0b1;
		unsigned int num_moves = 0;
		for (auto x = 0u; x < sizeof(move_mask) * 8u; x++)
		{
			if ((test_mask & move_mask) == test_mask)
			{
				if (n == num_moves)
				{
					move = test_mask;
					break;
				}
				num_moves++;
			}
			test_mask = test_mask << 1;
		}

		return move;
	}

	enum class GameResult : char {
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
}

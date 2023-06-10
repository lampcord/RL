#include "TicTacToe.h"

/*

Position is represented as follows in a 16 bit unsigned integer

.......XXXXXXXXX.......OOOOOOOOO

Move is represented by a number instead of a mask to keep under 256 bits

*/


namespace TicTacToeNS
{
	void TicTacToe::move(const PositionType& position, unsigned int player, unsigned int move, MoveResult<PositionType>& move_result)
	{
	}
	void TicTacToe::get_initial_position(PositionType& position)
	{
	}
	void TicTacToe::get_legal_moves(const PositionType& position, const unsigned int player, MoveType& legal_moves)
	{
	}
	void TicTacToe::render(const PositionType& position)
	{
	}
}
from enum import Enum
from abc import ABC, abstractmethod
"""
GameRules - Instead of having an ambiguous game class, we will instead use a stateless GameRules class. This class will encapsulate all of the rules of a given game.

Examples:
TTTGameRules - tic tac toe
C4GameRules - Connect 4
MancalaGameRules - Mancala
OthelloGameRules - Othello
BackgammonGameRules - Backgammon

The turn will always be represented by an index from 0 to N-1 where N is the number of players in the game.

Interface:
Init(NumberOfPlayers) - umber of players which is needed to determine the next player to move in order to perform all of its tasks. However, additional optional parameters may be available to specify things like:

GetPlayerBounds()
Returns:
A tuple (Min, Max) of the number of players that can legally play.

GetInitialState()
Returns:
GameState - The starting state for the game.

GetLegalMoves(GameState, TurnIndex)
Returns:
LegalMoves - a list of legal moves. Can be empty if no legal moves are available for that player (ie Backgammon).

Move(GameState, TurnIndex, Move)
Move indicates a move selected from the list returned by GetLegalMoves. It can be None if skipping is allowed.

Returns:
GameState - the new GameState after completing the move.
TurnIndex - the index of the next player to move (some games allow multiple moves by same player).
GameResult: Win, Loss, Tie, Continue. This is always from the point of view of the turn played by the call to Move.
Info - any other information in the form of a dict. Can be used for diagnostic info.


"""

class GameResult(Enum):
    WIN = 0
    LOSS = 1
    TIE = 2
    CONTINUE = 3

class GameRules(ABC):
    def __init__(self, number_of_players):
        self.number_of_players = number_of_players

    @abstractmethod
    def get_player_bounds(self):
        raise NotImplementedError("get_player_bounds")

    @abstractmethod
    def get_initial_position(self):
        raise NotImplementedError("get_initial_position")

    @abstractmethod
    def move(self, binary_state, move, turn):
        raise NotImplementedError("move")

    @abstractmethod
    def get_legal_moves(self, binary_state, turn):
        raise NotImplementedError("get_legal_moves")


from enum import Enum

"""
Game - Represents the rules to a board game.
    Reset - Reset game to initial state
    Move - Execute a move returning
    GetLegalMoves - Returns a list of legal move indexes.
    GetEncodedBinary - Returns the encoded binary of a list based position.
    GetDecodedList - Returns a list based position from a decoded binary.
    GetFeedForwardVector - Returns a vector that can be used to feed into a Net.
    Render - Render the game to stdout
"""

class GameTurn(Enum):
    PLAYER1 = 0
    PLAYER2 = 1
class GameResult(Enum):
    PLAYER1 = 0
    PLAYER2 = 1
    DRAW = 2
    NOT_COMPLETED = 3

game_result_for_turn = {
    GameTurn.PLAYER1: GameResult.PLAYER1,
    GameTurn.PLAYER2: GameResult.PLAYER2
}
class Game:
    def __init__(self):
        pass

    def get_initial_position(self):
        raise NotImplementedError("get_initial_position")

    def move(self, binary_state, move, turn):
        raise NotImplementedError("move")

    def get_legal_moves(self, binary_state):
        raise NotImplementedError("get_legal_moves")

    def get_encoded_binary(self, list_state):
        raise NotImplementedError("get_encoded_binary")

    def get_decoded_list(self, binary_state):
        raise NotImplementedError("get_decoded_list")

    def get_score_for_result(self, result, turn):
        if turn == GameTurn.PLAYER1:
            if result == GameResult.PLAYER1:
                return 1
            elif result == GameResult.PLAYER2:
                return 0

        if turn == GameTurn.PLAYER2:
            if result == GameResult.PLAYER2:
                return 1
            elif result == GameResult.PLAYER1:
                return 0

        return 0.5

    def switch_players(self, turn):
        return GameTurn.PLAYER1 if turn == GameTurn.PLAYER2 else GameTurn.PLAYER2
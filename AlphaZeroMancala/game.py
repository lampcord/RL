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
        return 0

    def move(self, binary_state, move, turn):
        new_binary_state = 0
        result = GameResult.NOT_COMPLETED
        switch_turns = True
        return new_binary_state, result, True

    def get_legal_moves(self, binary_state):
        return []

    def get_encoded_binary(self, list_state):
        return 0

    def get_score_for_result(self, result, turn):
        if result == GameResult.DRAW:
            return 0

        if turn == GameTurn.PLAYER1:
            if result == GameResult.PLAYER1:
                return 1
            elif result == GameResult.PLAYER2:
                return -1

        if turn == GameTurn.PLAYER2:
            if result == GameResult.PLAYER2:
                return 1
            elif result == GameResult.PLAYER1:
                return -1

        return None

    def switch_players(self, turn):
        return GameTurn.PLAYER1 if turn == GameTurn.PLAYER2 else GameTurn.PLAYER2
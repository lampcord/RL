from abc import ABC, abstractmethod

"""
Agent - The agent is responsible for making moves from a given position in a game. Types of Agents have a decision making mechanism.

Examples:
RandomAgent: an agent that makes random moves.
NNAgent: a Neural Network based agent
MCTSAgent: a Monte Carlo Tree Search based agent
ABAgent: an Alpha Beta MinMax based agent
GUIAgent: a graphical human interface agent
CommandLineAgent: a command line based agent

Interface:
Init(GameRules) - The Agent will only need the GameRules.
Optional initializers include:
MaxTimePerMove
MaxIterationsPerMove
TrainedData - Path to Trained NN, opening book, etc.
Policies - Different policies to use (UCB, rollout policy, etc.)

Move(GameState, TurnIndex) =>GameState, TurnIndex, GameResult, Info
Returns:
GameState - the new GameState after completing the move.
TurnIndex - the index of the next player to move (some games allow multiple moves by same player).
GameResult: Win, Loss, Tie, Continue. This is always from the point of view of the turn played by the call to Move.
Info - any other information in the form of a dict. Can be used for diagnostic info.

In addition, agents that can learn will have other yet to be determined interfaces that will be used in training.
"""


class Agent(ABC):
    def __init__(self, game_rules):
        self.game_rules = game_rules

    @abstractmethod
    def move(self, state, turn):
        raise NotImplementedError("move")

    @abstractmethod
    def get_description(self):
        raise NotImplementedError("get_description")


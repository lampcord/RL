from agent import Agent
import random

class RandomAgent(Agent):
    def __init__(self, game_rules):
        super().__init__(game_rules)


    def move(self, state, turn):
        moves = self.game_rules.get_legal_moves(state, turn)
        move = None
        if moves:
            move = random.choice(moves)
        return self.game_rules.move(state, move, turn)
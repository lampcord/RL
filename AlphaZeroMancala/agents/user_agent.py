import game_rules
from agent import Agent


class UserAgent(Agent):
    def __init__(self, game_rules, renderer):
        super().__init__(game_rules)
        self.renderer = renderer

    def move(self, state, turn):
        legal_moves = self.game_rules.get_legal_moves(state, turn)
        move = self.renderer.get_move(legal_moves)
        return self.game_rules.move(state, move, turn)

    def get_description(self):
        return "User Agent"









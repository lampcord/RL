import game_rules
from agent import Agent


class GuiAgent(Agent):
    def __init__(self, game_rules, renderer):
        super().__init__(game_rules)
        self.renderer = renderer

    def move(self, state, turn):
        move = self.renderer.get_move()
        return self.game_rules.move(state, move, turn)








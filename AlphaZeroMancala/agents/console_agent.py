import game_rules
from agent import Agent


class ConsoleAgent(Agent):
    def __init__(self, game_rules):
        super().__init__(game_rules)

    def move(self, state, turn):
        move = int(input(f"Choose move: "))
        return self.game_rules.move(state, move, turn)








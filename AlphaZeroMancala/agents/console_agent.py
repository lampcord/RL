from agent import Agent


class ConsoleAgent(Agent):
    def __init__(self, game_rules, renderer):
        super().__init__(game_rules, renderer)

    def move(self, state, turn):
        moves = self.game_rules.get_legal_moves(state, turn)
        print('=' * 60)
        self.render(state, turn, moves, {})

        move = int(input(f"Choose move: "))
        state, turn, result, info = self.game_rules.move(state, move, turn)

        print('-' * 60)
        print("Result:")
        self.render(state, turn, [], info)
        print('=' * 60)

        return state, turn, result, info








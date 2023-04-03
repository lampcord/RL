import numpy as np
from collections import defaultdict
import node_painter


class MonteCarloTreeSearchNode:
    def __init__(self, env, parent=None, parent_action=None):
        self.env = env
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        return

    def untried_actions(self):
        self._untried_actions = self.env.get_legal_actions()
        return self._untried_actions

    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses

    def expand(self):
        action = self._untried_actions.pop()
        new_env = self.env.clone()
        new_env.step(action)
        child_node = MonteCarloTreeSearchNode(
            new_env, parent=self, parent_action=action)

        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.env.is_game_over()

    def rollout(self):
        current_rollout_env = self.env.clone()

        while not current_rollout_env.is_game_over():
            possible_moves = current_rollout_env.get_legal_actions()

            action = self.rollout_policy(possible_moves)
            current_rollout_env.step(action)
        return current_rollout_env.game_result()



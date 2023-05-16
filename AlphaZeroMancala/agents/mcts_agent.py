from agent import Agent
import random

from game_rules import GameResult
import math
import time

class MCTSAgentConfig:
    def __init__(self):
        self.loops = 1000
        self.c = 1.14
        self.most_visits = True
        self.rollout_policy = None
        self.rollout_count = 1
        self.max_time = None

class MCTSNode:
    def __init__(self, game_rules, state, turn, parent=None, move=None, result=GameResult.CONTINUE):
        self.state = state
        self.game_rules = game_rules
        self.turn = turn
        self.parent = parent
        self.move = move
        self.unexplored_children = game_rules.get_legal_moves(state, turn)
        self.children = []
        self.result = result
        self.num_visits = 0.0
        self.num_wins = 0.0

    def select(self, c=1.41):
        if len(self.unexplored_children) > 0:
            return self
        if len(self.children) == 0:
            return self
        best_child = self.best_child(c)
        return best_child.select()

    def expand(self):
        if self.result != GameResult.CONTINUE:
            return self
        if len(self.unexplored_children) == 0:
            return self

        move = random.choice(self.unexplored_children)
        self.unexplored_children.remove(move)

        new_state, new_turn, result, info = self.game_rules.move(self.state, move, self.turn)
        child = MCTSNode(self.game_rules, new_state, new_turn, self, move, result)
        self.children.append(child)
        return child

    def rollout(self):
        state = self.state
        turn = self.turn
        result = self.result
        last_turn = self.parent.turn
        while result == GameResult.CONTINUE:
            moves = self.game_rules.get_legal_moves(state, turn)
            move = random.choice(moves)
            last_turn = turn
            state, turn, result, info = self.game_rules.move(state, move, turn)
        reward = 0
        if result == GameResult.WIN:
            reward = 1
        elif result == GameResult.TIE:
            reward = 0.5
        return reward, last_turn

    def external_rollout_policy(self, rollout_policy, rollouts):
        last_turn = self.parent.turn
        reward = 0
        if self.result == GameResult.WIN:
            reward = 1
        elif self.result == GameResult.TIE:
            reward = 0.5
        else:
            reward = rollout_policy(self.state, self.turn, rollouts) / rollouts
            last_turn = self.turn
        return reward, last_turn
    def back_propagate(self, reward, player_turn):
        self.num_visits += 1
        local_reward = 0
        if self.parent:
            local_reward = reward
        if self.parent and self.parent.turn != player_turn:
            local_reward = 1.0 - reward
        self.num_wins += local_reward
        if self.parent:
            self.parent.back_propagate(reward, player_turn)

    def ucb(self, c):
        if self.num_visits == 0 or self.parent.num_visits == 0:
            exploration = 1000000.0
            exploitation = 0.0
        else:
            exploration = c * math.sqrt(math.log(self.parent.num_visits) / self.num_visits)
            exploitation = self.num_wins / self.num_visits

        ucb = exploration + exploitation
        return ucb

    def best_child(self, c=1.41):
        return max(self.children, key=lambda child: child.ucb(c))

    def get_most_visited(self):
        return max(self.children, key=lambda child: child.num_visits)

    def dump(self, level, max_level):
        if level > max_level:
            return
        for _ in range(level):
            print ('....',end='')
        print(f'{self.move}:{self.num_wins}/{self.num_visits}')
        for child in self.children:
            child.dump(level + 1, max_level)


def mcts_search(game_rules, state, turn, loops, c, most_visits, rollout_policy=None, rollout_count=1, max_time=None):
    """
    Monte Carlo Tree Search - perform a MCTS from a given game_rules, state and player turn and return the best move.
    """
    root = MCTSNode(game_rules, state, turn)
    if max_time:
        start_time = time.time_ns()

    for _ in range(loops):
        node = root
        node = node.select(c)
        node = node.expand()
        if rollout_policy:
            reward, player_turn = node.external_rollout_policy(rollout_policy, rollout_count)
        else:
            reward, player_turn = node.rollout()
        node.back_propagate(reward, player_turn)
        if max_time:
            if start_time + max_time * 1000000000.0 < time.time_ns():
                break

    if most_visits:
        best_child = root.get_most_visited()
    else:
        best_child = root.best_child(c=0.0)

    return best_child.move

'''
        self.loops = 500
        self.c = 1.14
        self.most_visits = False
        self.rollout_policy = None
        self.rollout_count = 1
        self.max_time = None
'''
class MCTSAgent(Agent):
    def __init__(self, game_rules, config):
        super().__init__(game_rules)
        self.loops = config.loops
        self.c = config.c
        self.most_visits = config.most_visits
        self.rollout_policy = config.rollout_policy
        self.rollout_count = config.rollout_count
        self.max_time = config.max_time

    def move(self, state, turn):
        move = mcts_search(self.game_rules, state, turn, loops=self.loops, c=self.c, most_visits=self.most_visits, rollout_policy=self.rollout_policy, rollout_count=self.rollout_count, max_time=self.max_time)
        return self.game_rules.move(state, move, turn)

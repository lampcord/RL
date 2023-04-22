import time

import numpy as np
from tic_tac_toe.ttt_game import TicTacToeGame
# import node_painter
import pygame


class Node:
    def __init__(self, parent=None, action=None, env=None, root_player=None):
        self.parent = parent
        self.action = action
        self.env = env.clone() if env else None
        self.children = []
        self.num_visits = 0
        self.total_reward = 0
        self.is_expanded = False
        self.root_player = root_player

    def expand(self):
        legal_moves = self.env.get_legal_actions()
        self.children = [Node(parent=self, action=move, env=self.env, root_player=self.root_player) for move in legal_moves]
        for child in self.children:
            child.env.step(child.action)

        self.is_expanded = True

    def uct(self, c=1):
        if self.num_visits == 0 or self.parent is None:
            return np.inf
        return (self.total_reward / self.num_visits) + c * np.sqrt(np.log(self.parent.num_visits) / self.num_visits)

    def best_child(self, c=1):
        return max(self.children, key=lambda child: child.uct(c))

    def rollout(self):
        env_copy = self.env.clone()
        done = False
        while not done:
            legal_moves = env_copy.get_legal_actions()
            if len(legal_moves) == 0:
                break
            random_move = np.random.choice(legal_moves)
            _, _, done, _ = env_copy.step(random_move)

        result = env_copy.get_result()
        return result

    def backpropagate(self, rollout_result):
        self.num_visits += 1
        reward = 0
        if self.parent:
            reward = self.parent.env.get_points_for_result(rollout_result)
        self.total_reward += reward
        if self.parent:
            self.parent.backpropagate(rollout_result)

    def dump(self, level=1):
        for x in range(level):
            print(' ', end='')
        print(self.action, self.total_reward)
        for c in self.children:
            c.dump(level + 1)

    # def render_node(self, screen, font, selected=False):
    #     label = f"{self.total_reward}/{self.num_visits}=>{self.uct():.3}"
    #     text = font.render(label, True, (0, 0, 0))
    #     text_rect = text.get_rect(center=(self.pos[0], self.pos[1] - 30))
    #     screen.blit(text, text_rect)
    #
    #     self.env.render_node(screen, self.pos, font, selected)
    #
    # def get_path_label(self):
    #     return str(self.action)



# painter_on = False
def mcts(env, num_simulations=1000, c=1):
    root = Node(env=env, root_player=env.turn)
    game = TicTacToeGame()
    # if painter_on:
    #     painter = node_painter.NodePainter(root)

    for _ in range(num_simulations):
        node = root

        # if painter_on:
        #     painter.paint('Start', node)

        while node.is_expanded and node.children:
            node = node.best_child(c)

        if not node.is_expanded:
            node.expand()

        # if painter_on:
        #     painter.paint('Expanded', node)

        rollout_result = node.rollout()

        # if painter_on:
        #     painter.paint('Rollout', node)

        node.backpropagate(rollout_result)

        # if painter_on:
        #     painter.paint('Backpropogate', node)

    # if painter_on:
    #     painter.close()
    best_move = root.best_child(c=0).action
    # root.dump()
    return best_move

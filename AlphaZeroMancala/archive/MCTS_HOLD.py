import time

import numpy as np
from tic_tac_toe.ttt_game import TicTacToeGame
from tic_tac_toe.ttt_board import TicTacToeBoard
from game import GameResult, GameTurn
import node_painter
import pygame


class Node:
    def __init__(self, game, binary_state, turn, parent=None, move=None, result=GameResult.NOT_COMPLETED):
        self.game = game
        self.binary_state = binary_state
        self.turn = turn
        self.parent = parent
        self.move = move
        self.result = result

        self.children = []
        self.num_visits = 0
        self.total_reward = 0
        self.is_expanded = False

    def expand(self):
        legal_moves = self.game.get_legal_moves(self.binary_state)
        for move in legal_moves:
            child_binary_state, result, switch_turns, info = self.game.move(self.binary_state, move, self.turn)
            child_turn = self.game.switch_players(self.turn) if switch_turns else self.turn
            child = Node(self.game, child_binary_state, child_turn, self, move, result)
            self.children.append(child)

        self.is_expanded = True

    def uct(self, c=1):
        if self.num_visits == 0 or self.parent is None:
            return np.inf
        return (self.total_reward / self.num_visits) + c * np.sqrt(np.log(self.parent.num_visits) / self.num_visits)

    def best_child(self, c=1):
        return max(self.children, key=lambda child: child.uct(c))

    def rollout(self):
        rollout_binary_state = self.binary_state
        rollout_turn = self.turn
        rollout_result = self.result
        while rollout_result == GameResult.NOT_COMPLETED:
            legal_moves = self.game.get_legal_moves(rollout_binary_state)
            random_move = np.random.choice(legal_moves)
            rollout_binary_state, rollout_result, switch_turns, info = self.game.move(rollout_binary_state, random_move, rollout_turn)
            if switch_turns:
                rollout_turn = self.game.switch_players(rollout_turn)

        return rollout_result

    def backpropagate(self, rollout_result):
        self.num_visits += 1
        reward = 0
        if self.parent:
            reward = self.game.get_score_for_result(rollout_result, self.parent.turn)
        self.total_reward += reward
        if self.parent:
            self.parent.backpropagate(rollout_result)

    def dump(self, level=1):
        for x in range(level):
            print(' ', end='')
        print(self.action, self.total_reward)
        for c in self.children:
            c.dump(level + 1)

    def render_node(self, screen, board, font, selected=False, result=None):
        label = f"{self.total_reward}/{self.num_visits}=>{self.uct():.3}"
        if result:
            label += f" {result.name}"
        text = font.render(label, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1] - 30))
        screen.blit(text, text_rect)

        board.render_node(screen, self.binary_state, self.turn, self.pos, font, selected)

    def get_path_label(self):
        return str(self.move)


painter_on = True
def mcts(game, binary_state, turn, num_simulations=1000, c=1):
    root = Node(game, binary_state, turn)
    board = TicTacToeBoard()
    if painter_on:
        painter = node_painter.NodePainter(root, board)

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
        #     painter.paint('Rollout', node, rollout_result)

        node.backpropagate(rollout_result)

        # if painter_on:
        #     painter.paint('Backpropogate', node)

    if painter_on:
        painter.paint('Final', node)

    if painter_on:
        painter.close()
    best_move = root.best_child(c=0).move
    # root.dump()
    return best_move


if __name__ == "__main__":
    ttt = TicTacToeGame()
    binary_state = ttt.get_initial_position()
    ttt.render(binary_state)
    turn = GameTurn.PLAYER1
    result = GameResult.NOT_COMPLETED
    while result == GameResult.NOT_COMPLETED:
        move = mcts(ttt, binary_state, turn)
        binary_state, result, switch_turns, info = ttt.move(binary_state, move, turn)
        ttt.render(binary_state)
        if switch_turns:
            turn = ttt.switch_players(turn)
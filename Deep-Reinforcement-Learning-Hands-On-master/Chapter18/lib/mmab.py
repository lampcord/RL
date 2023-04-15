from minmaxabsearch import minmax_alpha_beta_node, minimax_alpha_beta
from lib import game, board, model
import node_painter
import pygame
import numpy as np
class game_node(minmax_alpha_beta_node):
    def __init__(self, position, moving_player, net):
        super().__init__(position)
        self.score = 0.0
        self.player = moving_player
        self.moving_player = moving_player
        self.children = []
        self.move = None
        self.mm_eval = None
        self.selected = False
        self.value = ""
        self.parent = None
        self.discount = 1.0
        self.net = net

    def evaluate(self):
        if self.score == 0.0:
            state_list = game.decode_binary(self.position)
            batch_v = model.state_lists_to_batch([state_list], [self.player])
            _, values_v = self.net(batch_v)
            self.score = values_v[0][0].item() * self.discount
        return self.score

    def is_terminal(self):
        moves = game.possible_moves(self.position)
        return self.score != 0.0 or len(moves) == 0

    def get_children(self):
        moves = game.possible_moves(self.position)
        self.children = []
        for move in moves:
            child_position, won = game.move(self.position, move, self.player)
            child_node = game_node(child_position, self.moving_player, self.net)
            child_node.player = game.get_oponent(self.player)
            child_node.move = move
            child_node.parent = self
            child_node.discount = self.discount - 0.001
            if won:
                if self.player == self.moving_player:
                    score = 1.0
                else:
                    score = -1.0
                child_node.score = score * child_node.discount
            self.children.append(child_node)
        return self.children

    def render_node(self, screen, font):
        # self.env.render_node(screen, self.pos)
        text_color = (0, 0, 0)
        if self.selected:
            node_color = (0, 255, 0)
        else:
            node_color = (0, 128, 0)
        pygame.draw.circle(screen, node_color, self.pos, 20)
        state_list = game.decode_binary(self.position)
        board.draw_small_board(screen, self.pos, state_list, self.player)
        text = font.render(self.get_value_label(), True, text_color)
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1] - 40))
        screen.blit(text, text_rect)
        text = font.render(str(self.score) + " " + str(game.possible_moves(self.position)), True, text_color)
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1] + 40))
        screen.blit(text, text_rect)

    def get_path_label(self):
        return str(self.move)

    def get_value_label(self):
        return str(self.mm_eval)

def get_best_move(position, moving_player, net):
    root = game_node(position, moving_player, net)
    minimax_alpha_beta(root, 6, float('-inf'), float('inf'), True)
    possible_moves = game.possible_moves(position)
    # painter = node_painter.NodePainter(root)
    # painter.paint()

    scores = []
    current_child = 0
    for x in range(7):
        if x in possible_moves:
            score = root.children[current_child].mm_eval
            scores.append(score if score is not None else 0.0)
            current_child += 1
        else:
            scores.append(-np.inf)

    return np.array(scores)
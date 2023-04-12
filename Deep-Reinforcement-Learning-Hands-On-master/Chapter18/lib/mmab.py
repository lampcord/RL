from minmaxabsearch import minmax_alpha_beta_node, minimax_alpha_beta
from lib import game
import node_painter
import pygame
class game_node(minmax_alpha_beta_node):
    def __init__(self, position, moving_player):
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

    def evaluate(self):
        return self.score

    def is_terminal(self):
        moves = game.possible_moves(self.position)
        return len(moves) == 0

    def get_children(self):
        moves = game.possible_moves(self.position)
        self.children = []
        for move in moves:
            child_position, won = game.move(self.position, move, self.player)
            child_node = game_node(child_position, self.moving_player)
            child_node.player = game.get_oponent(self.player)
            child_node.move = move
            child_node.parent = self
            if won:
                if self.player == self.moving_player:
                    score = 1.0
                else:
                    score = -1.0
                child_node.score = score
            self.children.append(child_node)
        return self.children

    def render_node(self, screen, font):
        # self.env.render_node(screen, self.pos)
        if self.selected:
            node_color = (0, 255, 0)
            text_color = (0, 0, 0)
        else:
            node_color = (0, 128, 0)
            text_color = (255, 255, 255)
        pygame.draw.circle(screen, node_color, self.pos, 20)
        text = font.render(self.get_value_label(), True, text_color)
        text_rect = text.get_rect(center=self.pos)
        screen.blit(text, text_rect)

    def get_path_label(self):
        return str(self.move)

    def get_value_label(self):
        return str(self.mm_eval)

def get_best_move(position, moving_player):
    root = game_node(position, moving_player)
    result = minimax_alpha_beta(root, 3, float('-inf'), float('inf'), True)
    # painter = node_painter.NodePainter(root)
    # painter.paint()
    return root.children
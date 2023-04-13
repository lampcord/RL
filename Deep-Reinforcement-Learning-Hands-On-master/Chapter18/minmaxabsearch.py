

class minmax_alpha_beta_node:
    def __init__(self, position):
        self.position = position

    def evaluate(self):
        return 0.0

    def is_terminal(self):
        return True

    def get_children(self):
        return []


def minimax_alpha_beta(node, depth, alpha, beta, maximizing_player):
    if depth == 0 or node.is_terminal():
        return node.evaluate()

    if maximizing_player:
        max_eval = float('-inf')
        for child in node.get_children():
            eval = minimax_alpha_beta(child, depth - 1, alpha, beta, False)
            child.mm_eval = eval
            max_eval = max(max_eval, eval)
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break  # Beta cut-off
        return max_eval
    else:
        min_eval = float('inf')
        for child in node.get_children():
            eval = minimax_alpha_beta(child, depth - 1, alpha, beta, True)
            child.mm_eval = eval
            min_eval = min(min_eval, eval)
            beta = min(beta, min_eval)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval

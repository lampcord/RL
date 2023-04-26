import random

from tic_tac_toe.ttt_game import TicTacToeGame
from tic_tac_toe.ttt_board import TicTacToeBoard
from replay_memory import ReplayMemory
from game import GameResult, GameTurn
import math
import node_painter

class MCTSNode:
    def __init__(self, game, binary_state, turn, parent=None, move=None, result=GameResult.NOT_COMPLETED, memory=None):
        self.binary_state = binary_state
        self.game = game
        self.turn = turn
        self.parent = parent
        self.move = move
        self.unexplored_children = game.get_legal_moves(binary_state, turn)
        self.children = []
        self.result = result
        self.memory = memory
        if memory:
            self.num_visits, self.num_wins = memory.get(self.binary_state)
        else:
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
        if self.result != GameResult.NOT_COMPLETED:
            return self
        if len(self.unexplored_children) == 0:
            return self

        move = random.choice(self.unexplored_children)
        self.unexplored_children.remove(move)

        turn = self.turn
        new_binary_state, result, switch_turns, info = game.move(self.binary_state, move, self.turn)
        if switch_turns:
            new_binary_state, turn = game.switch_players(new_binary_state, turn)
        child = MCTSNode(game, new_binary_state, turn, self, move, result, memory=self.memory)
        self.children.append(child)
        return child

    def rollout(self):
        binary_state = self.binary_state
        turn = self.turn
        result = self.result
        while result == GameResult.NOT_COMPLETED:
            moves = game.get_legal_moves(binary_state, turn)
            move = random.choice(moves)
            binary_state, result, switch_turns, info = game.move(binary_state, move, turn)
            if switch_turns:
                binary_state, turn = game.switch_players(binary_state, turn)
        return result

    def back_propagate(self, rollout_result):
        self.num_visits += 1
        reward = 0
        if self.parent:
            reward = self.game.get_score_for_result(rollout_result, self.parent.turn)
        self.num_wins += reward
        if self.memory:
            self.memory.update(self.binary_state, self.num_visits, self.num_wins)
        if self.parent:
            self.parent.back_propagate(rollout_result)

    def ucb(self, c):
        if self.parent is None:
            return 0.0
        if self.num_visits == 0:
            return 0.0
        exploitation = self.num_wins / self.num_visits
        exploration = c * math.sqrt(math.log(self.parent.num_visits) / self.num_visits)
        ucb = exploration + exploitation
        return ucb
    def best_child(self, c=1.41):
        return max(self.children, key=lambda child: child.ucb(c))

    def render_node(self, screen, board, font, selected=False, result=None):
        label = f"{self.num_wins:.2f}/{self.num_visits:.2f}=>{self.ucb(c=1.41):.3}"
        if result:
            label += f" {result.name}"
        text = font.render(label, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1] - 30))
        screen.blit(text, text_rect)

        board.render_node(screen, self.binary_state, self.turn, self.pos, font, selected)

    def get_path_label(self):
        return str(self.move)

    def get_most_visited(self):
        return max(self.children, key=lambda child: child.num_visits).move


painter_on = False
# painter_on = True
final_only = True


def mcts_search(game, binary_state, turn, loops=500, memory=None):
    root = MCTSNode(game, binary_state, turn, memory=memory)
    board = TicTacToeBoard()
    if painter_on:
        painter = node_painter.NodePainter(root, board)

    for _ in range(loops):
        node = root

        if painter_on and not final_only:
            painter.paint('Start', node)

        node = node.select()

        if painter_on and not final_only:
            painter.paint('Select', node)

        node = node.expand()

        if painter_on and not final_only:
            painter.paint('Expand', node)

        rollout_result = node.rollout()

        if painter_on and not final_only:
            painter.paint('Rollout', node)

        node.back_propagate(rollout_result)

    if painter_on:
        painter.paint('Final', node)

    # if painter_on:
    #     painter.close()
    # return root.get_most_visited()
    return root.best_child(c=0.0).move

if __name__ == "__main__":
    game = TicTacToeGame()
    memory1 = ReplayMemory("TicTacToeMemory_1000.bin")
    memory2 = ReplayMemory("TicTacToeMemory_2000.bin")
    # memory = None
    mcts_turn = GameTurn.PLAYER1
    random_turn = GameTurn.PLAYER2

    results = {}
    results[GameResult.PLAYER1] = 0
    results[GameResult.PLAYER2] = 0
    results[GameResult.DRAW] = 0
    for game_number in range(100):
        turn = GameTurn.PLAYER1 if game_number % 2 == 0 else GameTurn.PLAYER2
        binary_state = game.get_initial_position()
        result = GameResult.NOT_COMPLETED
        # game.render(binary_state, turn)
        while result == GameResult.NOT_COMPLETED:
            # print(binary_state)
            if turn == mcts_turn:
                move = mcts_search(game, binary_state, turn, loops=10, memory=memory1)
                # legal_moves = game.get_legal_moves(binary_state, turn)
                # move = random.choice(legal_moves)
            else:
                move = mcts_search(game, binary_state, turn, loops=1000, memory=None)
                # legal_moves = game.get_legal_moves(binary_state, turn)
                # move = random.choice(legal_moves)
                # move = int(input(f"Choose Move: {legal_moves}"))
            binary_state, result, switch_turns, info = game.move(binary_state, move, turn)
            # game.render(binary_state, turn)
            if switch_turns:
                binary_state, turn = game.switch_players(binary_state, turn)
        results[result] += 1
        # print(binary_state)
        # print(f"Size of replay memory: {len(memory.memory)}")
        print('.', end='')
        # memory.write()
    print(results)



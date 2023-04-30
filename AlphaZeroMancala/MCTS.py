import random

from tic_tac_toe.ttt_game import TicTacToeGame
# from tic_tac_toe.ttt_board import TicTacToeBoard
from Connect4.c4_game import C4Game
from Connect4.c4_board import C4Board

from replay_memory import ReplayMemory
from game import GameResult, GameTurn
import math
import node_painter
import time

class MCTSNode:
    def __init__(self, game, binary_state, turn, parent=None, move=None, result=GameResult.NOT_COMPLETED, memory=None, memory_depth=0):
        self.binary_state = binary_state
        self.game = game
        self.turn = turn
        self.parent = parent
        self.move = move
        self.unexplored_children = game.get_legal_moves(binary_state, turn)
        self.children = []
        self.result = result
        self.memory_depth = memory_depth
        self.memory = memory
        if memory and memory_depth > 0:
            self.num_visits, self.num_wins = memory.get(self.binary_state)
            if self.num_visits > 0:
                self.num_wins = self.num_wins / self.num_visits
                self.num_visits = 1
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
        child = MCTSNode(game, new_binary_state, turn, self, move, result, memory=self.memory, memory_depth=self.memory_depth - 1)
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

        board.render_node(self.binary_state, self.turn.value, self.pos, font, selected)

    def get_path_label(self):
        return str(self.move)

    def get_most_visited(self):
        return max(self.children, key=lambda child: child.num_visits).move


# painter_on = False
painter_on = True
# final_only = True
final_only = False

def update_memory(memory, node):
    memory.update(node.binary_state, node.num_visits, node.num_wins)
    for child in node.children:
        update_memory(memory, child)

def mcts_search(game, binary_state, turn, loops=500, memory=None, memory_depth=0, c=1.41, learn=False, board=None, most_visits=False):
    root = MCTSNode(game, binary_state, turn, memory=memory, memory_depth=memory_depth)
    if painter_on and board:
        painter = node_painter.NodePainter(root, board)

    stats = {}
    start = time.time_ns()
    cycles = 0
    if memory:
        memory.memory_found = 0.0
        memory.memory_checks = 0.0
    for _ in range(loops):
        node = root
        cycles += 1
        if painter_on and board and not final_only:
            painter.paint('Start', node)

        node = node.select(c)
        stats["S"] = stats.get("S", 0) + 1

        if painter_on and board and not final_only:
            painter.paint('Select', node)

        node = node.expand()
        stats["E"] = stats.get("E", 0) + 1

        if painter_on and board and not final_only:
            painter.paint('Expand', node)

        if learn or node.num_visits == 0:
            rollout_result = node.rollout()
            stats["R"] = stats.get("R", 0) + 1

            if painter_on and board and not final_only:
                painter.paint('Rollout', node)

            node.back_propagate(rollout_result)
            stats["B"] = stats.get("B", 0) + 1

        # if time.time_ns() - start > 1000000000.0:
        #     break

    if painter_on and board:
        painter.paint('Final', node)

    if memory and learn:
        update_memory(memory, root)
        
    print(stats)
    # if painter_on and board:
    #     painter.close()
    print(f"cycles {cycles}")
    if memory:
        print(f"{memory.memory_found}/{memory.memory_checks}")
    if most_visits:
        return root.get_most_visited()
    else:
        return root.best_child(c=0.0).move

if __name__ == "__main__":
    # game = TicTacToeGame()
    # board = TicTacToeBoard()
    game = C4Game()
    board = C4Board(1900, 1000, game)
    # memory1 = ReplayMemory("TicTacToeMemory_1000.bin")
    # memory2 = ReplayMemory("TicTacToeMemory_2000.bin")
    memory1 = ReplayMemory("C4Game_1000.bin")
    # memory1 = ReplayMemory("C4Game_2000.bin")

    # memory1 = None
    memory2 = None

    mcts_turn = GameTurn.PLAYER1
    random_turn = GameTurn.PLAYER2

    results = {}
    results[GameResult.PLAYER1] = 0
    results[GameResult.PLAYER2] = 0
    results[GameResult.DRAW] = 0

    accumulated_time = {}
    accumulated_time[GameTurn.PLAYER1] = 0.0
    accumulated_time[GameTurn.PLAYER2] = 0.0

    for game_number in range(10):
        turn = GameTurn.PLAYER1 if game_number % 2 == 0 else GameTurn.PLAYER2
        binary_state = game.get_initial_position()
        # turn = GameTurn.PLAYER2
        # binary_state = 1711255632655510
        # binary_state, turn = game.switch_players(binary_state, turn)

        result = GameResult.NOT_COMPLETED
        game.render(binary_state, turn)
        win = None
        while result == GameResult.NOT_COMPLETED:
            # print(binary_state)
            # legal_moves = game.get_legal_moves(binary_state, turn)
            # list_state = game.get_decoded_list(binary_state, turn)
            # board.draw_board(list_state, turn.value, legal_moves, "", win)
            start = time.time_ns()
            if turn == mcts_turn:
                move = mcts_search(game, binary_state, turn, loops=10000000, memory=memory1, memory_depth=3, c=1.41, learn=True, board=board)
                # move = random.choice(legal_moves)
                # move = int(input(f"Choose Move: {legal_moves}"))
            else:
                move = mcts_search(game, binary_state, turn, loops=10000000, memory=memory2, c=1.41, learn=True)
                # move = random.choice(legal_moves)
                # move = int(input(f"Choose Move: {legal_moves}"))
                # move = board.get_move(legal_moves)
            accumulated_time[turn] += (time.time_ns() - start) / 1000000000.0
            binary_state, result, switch_turns, info = game.move(binary_state, move, turn)
            win = game.check_for_win(binary_state, turn) if result == GameResult.PLAYER1 or result == GameResult.PLAYER2 else None
            game.render(binary_state, turn, win)
            if switch_turns:
                binary_state, turn = game.switch_players(binary_state, turn)
        results[result] += 1
        print(results)

        # print(binary_state)
        # print(f"Size of replay memory: {len(memory.memory)}")
        print('.', end='')
        # memory.write()
    # legal_moves = game.get_legal_moves(binary_state, turn)
    # list_state = game.get_decoded_list(binary_state, turn)
    # board.draw_board(list_state, turn.value, legal_moves, "", win)
    # board.wait_for_click()
    print('')
    print(results)
    print(accumulated_time)


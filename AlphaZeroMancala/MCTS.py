import random
from enum import Enum

from tic_tac_toe.ttt_game import TicTacToeGame
# from tic_tac_toe.ttt_board import TicTacToeBoard
from Connect4.c4_game import C4Game
from Connect4.c4_board import C4Board

from replay_memory import ReplayMemory, CondensedMemory
from game import GameResult, GameTurn
import math
import node_painter
import time

class MCTSNode:
    def __init__(self, game, binary_state, turn, parent=None, move=None, result=GameResult.NOT_COMPLETED):
        self.binary_state = binary_state
        self.game = game
        self.turn = turn
        self.parent = parent
        self.move = move
        self.unexplored_children = game.get_legal_moves(binary_state, turn)
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
        child = MCTSNode(game, new_binary_state, turn, self, move, result)
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
        if self.num_visits == 0 or self.parent.num_visits == 0:
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

# final_only = True
final_only = False

def update_memory(game, memory, node, root_turn):
    if node.parent:
        binary_state = node.binary_state
        if node.parent.turn != root_turn:
            binary_state, _ = game.switch_players(binary_state, node.parent.turn)
        memory.update(binary_state, node.num_visits, node.num_wins)
    for child in node.children:
        update_memory(game, memory, child, root_turn)

def mcts_search(game, binary_state, turn, loops=500, memory=None, condensed_memory=None, c=1.41, learn=False, board=None, most_visits=False):
    if condensed_memory:
        if binary_state == game.get_initial_position():
            move = 3
        else:
            move = condensed_memory.get(binary_state)
        if move is not None:
            return move
    root = MCTSNode(game, binary_state, turn)
    if board:
        painter = node_painter.NodePainter(root, board)

    cycles = 0
    for _ in range(loops):
        node = root
        cycles += 1
        if board and not final_only:
            painter.paint('Start', node)

        node = node.select(c)

        if board and not final_only:
            painter.paint('Select', node)

        node = node.expand()

        if board and not final_only:
            painter.paint('Expand', node)

        rollout_result = node.rollout()

        if board and not final_only:
            painter.paint('Rollout', node)

        node.back_propagate(rollout_result)

    if board:
        painter.paint('Final', node)

    if memory:
        update_memory(game, memory, root, turn)

    if board:
        painter.close()

    if most_visits:
        return root.get_most_visited()
    else:
        return root.best_child(c=0.0).move

class PLAYMODE(Enum):
    TRAIN = 0
    TEST = 1
    HUMAN = 2
    RANDOM = 3


if __name__ == "__main__":
    game = C4Game()
    # board = C4Board(1900, 1000, game)
    # board = C4Board(game=game)
    board = None
    # play_on_board = True
    play_on_board = False

    # player1_mode = PLAYMODE.TRAIN
    player1_mode = PLAYMODE.TEST
    # player1_mode = PLAYMODE.HUMAN
    # player1_mode = PLAYMODE.RANDOM
    # memory1 = ReplayMemory("C4Game_1000.bin")
    memory1 = None
    # condensed_memory1 = CondensedMemory("C4Game_2000.bin", 1000)
    condensed_memory1 = None

    # player2_mode = PLAYMODE.TRAIN
    player2_mode = PLAYMODE.TEST
    # player2_mode = PLAYMODE.HUMAN
    # player2_mode = PLAYMODE.RANDOM
    memory2 = None
    condensed_memory2 = CondensedMemory("C4Game_2000.bin", 1000)
    # condensed_memory2 = None

    results = {}
    results[GameResult.PLAYER1] = 0
    results[GameResult.PLAYER2] = 0
    results[GameResult.DRAW] = 0

    accumulated_time = {}
    accumulated_time[GameTurn.PLAYER1] = 0.0
    accumulated_time[GameTurn.PLAYER2] = 0.0

    for game_number in range(10):
        print("=" * 60)
        turn = GameTurn.PLAYER1 if game_number % 2 == 0 else GameTurn.PLAYER2
        binary_state = game.get_initial_position()

        result = GameResult.NOT_COMPLETED
        game.render(binary_state, turn)
        win = None
        if play_on_board:
            legal_moves = game.get_legal_moves(binary_state, turn)
            list_state = game.get_decoded_list(binary_state, turn)
            board.draw_board(list_state, turn.value, legal_moves, "")
            time.sleep(.3)
        while result == GameResult.NOT_COMPLETED:
            print('_' * 60)
            print(f"Player {turn.name} is thinking ...")
            start = time.time_ns()
            if turn == GameTurn.PLAYER1:
                if player1_mode == PLAYMODE.TRAIN:
                    move = mcts_search(game, binary_state, turn, loops=1000, memory=memory1, c=1.41, learn=True)
                elif player1_mode == PLAYMODE.TEST:
                    move = mcts_search(game, binary_state, turn, loops=1000, condensed_memory=condensed_memory1, c=1.41, learn=True, board=None)
                elif player1_mode == PLAYMODE.RANDOM:
                    legal_moves = game.get_legal_moves(binary_state, turn)
                    move = random.choice(legal_moves)
                elif player1_mode == PLAYMODE.HUMAN:
                    legal_moves = game.get_legal_moves(binary_state, turn)
                    if play_on_board:
                        list_state = game.get_decoded_list(binary_state, turn)
                        move = board.get_move(legal_moves)
                    else:
                        move = int(input(f"Choose Move: {legal_moves}"))
            else:
                if player2_mode == PLAYMODE.TRAIN:
                    move = mcts_search(game, binary_state, turn, loops=1000, memory=memory1, c=1.41, learn=True)
                elif player2_mode == PLAYMODE.TEST:
                    move = mcts_search(game, binary_state, turn, loops=1000, condensed_memory=condensed_memory2, c=1.41, learn=True, board=None)
                elif player2_mode == PLAYMODE.RANDOM:
                    legal_moves = game.get_legal_moves(binary_state, turn)
                    move = random.choice(legal_moves)
                elif player2_mode == PLAYMODE.HUMAN:
                    legal_moves = game.get_legal_moves(binary_state, turn)
                    if play_on_board:
                        list_state = game.get_decoded_list(binary_state, turn)
                        move = board.get_move(legal_moves)
                    else:
                        move = int(input(f"Choose Move: {legal_moves}"))

            print(f"Move {move}")
            accumulated_time[turn] += (time.time_ns() - start) / 1000000000.0
            binary_state, result, switch_turns, info = game.move(binary_state, move, turn)
            win = game.check_for_win(binary_state, turn) if result == GameResult.PLAYER1 or result == GameResult.PLAYER2 else None
            game.render(binary_state, turn, win)
            if switch_turns:
                binary_state, turn = game.switch_players(binary_state, turn)
            if play_on_board:
                legal_moves = game.get_legal_moves(binary_state, turn)
                list_state = game.get_decoded_list(binary_state, turn)
                board.draw_board(list_state, turn.value, legal_moves, "", win_set=win)
                if win:
                    time.sleep(5)
                else:
                    time.sleep(.3)

        results[result] += 1
        print(f"game_number: {game_number} {results}")

        # print(binary_state)
        print('.', end='')
        if player1_mode == PLAYMODE.TRAIN:
            memory1.write()
            print(f"Size of replay memory: {len(memory1.memory)}")

    print('')
    print(results)
    print(accumulated_time)


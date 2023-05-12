import random
from enum import Enum
import ctypes
import os

from tic_tac_toe.ttt_game import TicTacToeGame
# from tic_tac_toe.ttt_board import TicTacToeBoard
from Connect4.c4_game import C4Game
from Connect4.c4_board import C4Board

from replay_memory import ReplayMemory, CondensedMemory
from game import GameResult, GameTurn
import math
import node_painter
import time

class UCB_Type(Enum):
    UCB0 = 0
    UCB1 = 1
    UCB1_TUNED = 2

class MCTSNode:
    def __init__(self, game, binary_state, turn, parent=None, move=None, result=GameResult.NOT_COMPLETED, fast_rollout=None):
        """
        :param game:
        :param binary_state:
        :param turn:
        :param parent:
        :param move:
        :param result:
        """
        self.binary_state = binary_state
        self.game = game
        self.turn = turn
        self.parent = parent
        self.move = move
        self.unexplored_children = game.get_legal_moves(binary_state, turn)
        self.children = []
        self.result = result
        self.reward_history = {}
        self.num_visits = 0.0
        self.num_wins = 0.0
        self.fast_rollout = fast_rollout

    def select(self, c=1.41, ucb_type=UCB_Type.UCB1):
        if len(self.unexplored_children) > 0:
            return self
        if len(self.children) == 0:
            return self
        best_child = self.best_child(c, ucb_type)
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
        child = MCTSNode(game, new_binary_state, turn, self, move, result, fast_rollout=self.fast_rollout)
        self.children.append(child)
        return child

    def rollout(self):
        if self.fast_rollout:
            # self.game.render(self.binary_state, self.turn)
            reward = self.fast_rollout(self.binary_state, self.turn.value, 2000) / 2000
        else:
            binary_state = self.binary_state
            turn = self.turn
            result = self.result
            while result == GameResult.NOT_COMPLETED:
                moves = game.get_legal_moves(binary_state, turn)
                move = random.choice(moves)
                binary_state, result, switch_turns, info = game.move(binary_state, move, turn)
                if switch_turns:
                    binary_state, turn = game.switch_players(binary_state, turn)
            reward = self.game.get_score_for_result(result, self.turn)
        return reward, self.turn

    def back_propagate(self, reward, player_turn):
        self.num_visits += 1
        local_reward = 0
        if self.parent:
            local_reward = reward
        if self.parent and self.parent.turn != player_turn:
            local_reward = 1.0 - reward
        self.num_wins += local_reward
        self.reward_history[local_reward] = self.reward_history.get(local_reward, 0) + 1
        if self.parent:
            self.parent.back_propagate(reward, player_turn)

    def ucb(self, c, ucb_type=UCB_Type.UCB1):
        ucb = 0.0

        if self.parent is None:
            return ucb

        if self.num_visits == 0 or self.parent.num_visits == 0:
            exploration = 1000000.0
            exploitation = 0.0
        else:
            exploitation = self.num_wins / self.num_visits

        if ucb_type == UCB_Type.UCB0:
            '''
            Fabricated UCB to return only the exploitation value
            '''
            exploration = 0.0
        elif ucb_type == UCB_Type.UCB1:
            '''
            Bandit Upper Confidence Index = Sample Mean + c * √(logN / n)
            where 
              N = total rounds (parents visits)
              n = number of node's visits
            '''
            exploration = c * math.sqrt(math.log(self.parent.num_visits) / self.num_visits)
        elif ucb_type == UCB_Type.UCB1_TUNED:
            '''
            C = √( (logN / n) x min(1/4, V(n)) )
            where V(n) is an upper confidence bound on the variance
            V(n) = Σ(x_i² / n) - (Σ x_i / n)² + √(2log(N) / n) 
            and x_i are the rewards we got from the bandit so far.
            '''
            rewards_squared = 0.0
            for key in self.reward_history.keys():
                rewards_squared += self.reward_history[key] * key ** 2
            variance = rewards_squared / self.num_visits
            variance -= exploitation ** 2
            variance += math.sqrt(2 * math.log(self.parent.num_visits) / self.num_visits)
            exploration = math.sqrt((math.log(self.parent.num_visits) / self.num_visits) * min(variance, 0.25))

        ucb = exploration + exploitation
        return ucb

    def best_child(self, c=1.41, ucb_type=UCB_Type.UCB1):
        return max(self.children, key=lambda child: child.ucb(c, ucb_type))

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
        return max(self.children, key=lambda child: child.num_visits)

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


def mcts_search(game, binary_state, turn, loops=500, memory=None, condensed_memory=None, c=1.41,
                board=None, most_visits=False, ucb_type=UCB_Type.UCB1, fast_rollout=None):
    """
    Monte Carlo Tree Search - perform a MCTS from a given game, state and player turn and return the best move.
    :param game: game class
    :param binary_state: starting binary state
    :param turn: turn of searching player
    :param loops: how many iterations to run
    :param memory: memory to be trained by this run
    :param condensed_memory: condensed memory used to look up moves
    :param c: exploration constant usd by UCB1
    :param board: used if displaying tree for debugging
    :param most_visits: use most visits for the move choice instead of best score
    :param ucb_type: UCB1 or UCB1-Tuned
    :return: move, info. Info contains diagnostic info from search.
    """
    info = {}
    if condensed_memory:
        move = condensed_memory.get(binary_state)
        if move is not None:
            info["CondensedMemory"] = True
            return move, info
        info["CondensedMemory"] = False

    root = MCTSNode(game, binary_state, turn, fast_rollout=fast_rollout)

    if board:
        painter = node_painter.NodePainter(root, board)

    for _ in range(loops):
        node = root

        if board and not final_only:
            painter.paint('Start', node)

        node = node.select(c, ucb_type)

        if board and not final_only:
            painter.paint('Select', node)

        node = node.expand()

        if board and not final_only:
            painter.paint('Expand', node)

        reward, player_turn = node.rollout()

        if board and not final_only:
            painter.paint('Rollout', node)

        node.back_propagate(reward, player_turn)

    if board:
        painter.paint('Final', node)

    if memory:
        update_memory(game, memory, root, turn)

    if board:
        painter.close()

    if most_visits:
        best_child = root.get_most_visited()
    else:
        best_child = root.best_child(ucb_type=UCB_Type.UCB0)

    info["num_visits"] = best_child.num_visits
    info["num_wins"] = best_child.num_wins
    info["reward_history"] = best_child.reward_history

    return root.best_child(c=0.0).move, info

class PLAYMODE(Enum):
    TRAIN = 0
    TEST = 1
    HUMAN = 2
    RANDOM = 3


if __name__ == "__main__":
    # Load the DLL
    dll_path = os.path.join("FastRollout.dll")
    my_functions = ctypes.CDLL(dll_path)

    # Declare the argument types and return types of the C++ functions
    my_functions.C4_rollout.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64]
    my_functions.C4_rollout.restype = ctypes.c_float

    game = C4Game()
    num_games = 10
    # board = C4Board(1900, 1000, game)
    board = C4Board(game=game)
    # board = None
    play_on_board = True
    # play_on_board = False

    # player1_mode = PLAYMODE.TRAIN
    player1_mode = PLAYMODE.TEST
    # player1_mode = PLAYMODE.HUMAN
    # player1_mode = PLAYMODE.RANDOM
    # player1_ucb = UCB_Type.UCB1
    player1_ucb = UCB_Type.UCB1_TUNED
    # memory1 = ReplayMemory("C4Game_1000.bin")
    memory1 = None
    # condensed_memory1 = CondensedMemory("C4Game_1000_10000.bin", 1000)
    condensed_memory1 = None

    # player2_mode = PLAYMODE.TRAIN
    # player2_mode = PLAYMODE.TEST
    player2_mode = PLAYMODE.HUMAN
    # player2_mode = PLAYMODE.RANDOM
    player2_ucb = UCB_Type.UCB1
    # player2_ucb = UCB_Type.UCB1_TUNED
    memory2 = None
    # condensed_memory2 = CondensedMemory("C4Game_2000.bin", 1000)
    condensed_memory2 = None

    results = {}
    results[GameResult.PLAYER1] = 0
    results[GameResult.PLAYER2] = 0
    results[GameResult.DRAW] = 0

    accumulated_time = {}
    accumulated_time[GameTurn.PLAYER1] = 0.0
    accumulated_time[GameTurn.PLAYER2] = 0.0
    condensed_memory_tracker = []

    for game_number in range(num_games):
        print("=" * 60)
        turn = GameTurn.PLAYER1 if game_number % 2 == 0 else GameTurn.PLAYER2
        binary_state = game.get_initial_position()

        result = GameResult.NOT_COMPLETED
        game.render(binary_state, turn)
        win = None

        condensed_memory_set = []
        if play_on_board:
            legal_moves = game.get_legal_moves(binary_state, turn)
            list_state = game.get_decoded_list(binary_state, turn)
            board.draw_board(list_state, turn.value, legal_moves, "")
            time.sleep(.3)
        while result == GameResult.NOT_COMPLETED:
            print('_' * 60)
            print(f"Player {turn.name} is thinking ...")
            start = time.time_ns()
            mcts_info = {}
            if turn == GameTurn.PLAYER1:
                if player1_mode == PLAYMODE.TRAIN:
                    move, mcts_info = mcts_search(game, binary_state, turn, loops=1000, memory=memory1, c=1.41)
                elif player1_mode == PLAYMODE.TEST:
                    move, mcts_info = mcts_search(game, binary_state, turn, loops=1000,
                                                  condensed_memory=condensed_memory1, c=1.41, board=None,
                                                  ucb_type=player1_ucb, most_visits=True, fast_rollout=my_functions.C4_rollout)
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
                    move, mcts_info = mcts_search(game, binary_state, turn, loops=1000, memory=memory1, c=1.41)
                elif player2_mode == PLAYMODE.TEST:
                    move, mcts_info = mcts_search(game, binary_state, turn, loops=1000,
                                                  condensed_memory=condensed_memory2, c=1.41, board=None,
                                                  ucb_type=player2_ucb, most_visits=True)
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

            condensed_memory_test = mcts_info.get("CondensedMemory", None)
            if condensed_memory_test is not None:
                condensed_memory_set.append(mcts_info["CondensedMemory"])

            print(f"Move {move} Info {str(mcts_info)}")

            accumulated_time[turn] += (time.time_ns() - start) / 1000000000.0
            binary_state, result, switch_turns, info = game.move(binary_state, move, turn)
            win = game.check_for_win(binary_state, turn) if result == GameResult.PLAYER1 or result == GameResult.PLAYER2 else None
            game.render(binary_state, turn, win)

            if switch_turns:
                binary_state, turn = game.switch_players(binary_state, turn)
            if play_on_board:
                num_visits = mcts_info.get("num_visits", 1)
                num_wins = mcts_info.get("num_wins", 0)
                score = f"Score: {num_wins / num_visits:.3}"
                legal_moves = game.get_legal_moves(binary_state, turn)
                list_state = game.get_decoded_list(binary_state, turn)
                board.draw_board(list_state, turn.value, legal_moves, score, win_set=win)
                if win:
                    time.sleep(5)
                else:
                    time.sleep(.3)

        results[result] += 1
        print(f"game_number: {game_number} {results}")
        condensed_memory_tracker.append(condensed_memory_set)

        if player1_mode == PLAYMODE.TRAIN:
            memory1.write()
            print(f"Size of replay memory: {len(memory1.memory)}")

    for cmemory_set in condensed_memory_tracker:
        print(str(cmemory_set))

    print('')
    print(results)
    print(accumulated_time)


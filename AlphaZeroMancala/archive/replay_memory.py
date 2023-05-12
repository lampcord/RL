import msgpack
import os

from Connect4.c4_game import C4Game
from game import GameResult, GameTurn
import random

def get_condensed_filename(filename, min_visits):
    condensed_filename = filename.replace(".bin", "_C" + str(min_visits) + ".bin")
    return condensed_filename

def get_condensed_memory(filename, min_visits):
    cmemory = None
    cfilename = get_condensed_filename(filename, 1000)
    if os.path.exists(cfilename):
        with open(cfilename, 'rb') as f:
            packed_data = f.read()
            cmemory = msgpack.unpackb(packed_data, strict_map_key=False)
    return cmemory

class CondensedMemory:
    def __init__(self, filename, min_visits):
        self.condensed_memory = get_condensed_memory(filename, min_visits)

    def get(self, binary_state):
        return self.condensed_memory.get(binary_state, None)

class ReplayMemory:
    def __init__(self, filename=None):
        self.memory = {}
        self.filename = filename
        self.read()
        self.memory_found = 0.0
        self.memory_checks = 0.0

    def update(self, binary_state, visits, wins):
        current_visits, current_wins = self.memory.get(binary_state, (0, 0))
        value = (visits + current_visits, wins + current_wins)
        self.memory[binary_state] = value

    def get(self, binary_state):
        result = self.memory.get(binary_state, None)
        self.memory_checks += 1
        if result:
            self.memory_found += 1
        else:
            result = (0, 0)
        return result

    def read(self):
        if self.filename is None:
            return
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                packed_data = f.read()
                self.memory = msgpack.unpackb(packed_data, strict_map_key=False)

    def write(self):
        if self.filename is None:
            return
        packed_data = msgpack.packb(self.memory)
        with open(self.filename, 'wb') as f:
            f.write(packed_data)

    def scale(self, target=100.0):
        max_value = max(self.memory.values())[0]
        factor = target / max_value
        self.memory = {key: (visits * factor, wins * factor) for key, (visits, wins) in self.memory.items()}
        # for key, (visits, wins) in self.memory.items():
        #     print(key, visits, wins)
        # print(max(self.memory.values()))

    def get_move_from_memory(self, game, binary_state, turn, min_visits):
        # print("Checking memory for position...")
        num_visits, num_wins = self.get(binary_state)
        # print(num_visits, num_wins)
        legal_moves = game.get_legal_moves(binary_state, turn)
        total_visits = 0
        best_move = None
        best_score = 0
        for move in legal_moves:
            test_state, _, switch_turns, _ = game.move(binary_state, move, turn)
            if switch_turns:
                test_state, test_turn = game.switch_players(test_state, turn)
            num_visits, num_wins = self.get(test_state)
            score = 0 if num_visits == 0 else num_wins / num_visits
            if best_move is None or score > best_score:
                best_move = move
                best_score = score
            total_visits += num_visits
            # print(move, num_visits, num_wins, score)
            # game.render(test_state, test_turn)
        # print(f"Total Visits: {total_visits}")
        if total_visits < min_visits:
            best_move = None
        # print(f"Best Move: {str(best_move)}")
        # input()
        return best_move

    def condense(self, game, turn, min_visits):
        condensed_filename = get_condensed_filename(self.filename, min_visits)
        print(condensed_filename)
        condensed_memory = {}
        print()
        ndx = 0
        # initial position is not stored
        key = game.get_initial_position()
        move = self.get_move_from_memory(game, key, turn, min_visits)
        condensed_memory[key] = move

        for key in self.memory.keys():
            ndx += 1
            if ndx % 100 == 0:
                print()
            move = self.get_move_from_memory(game, key, turn, min_visits)
            if move is None:
                print('.', end='')
            else:
                condensed_memory[key] = move
                print('X', end='')
        packed_data = msgpack.packb(condensed_memory)
        with open(condensed_filename, 'wb') as f:
            f.write(packed_data)
        return condensed_filename


if __name__ == "__main__":
    game = C4Game()
    filename = "C4Game_1000_10000.bin"
    memory1 = ReplayMemory(filename)
    # memory1.condense(game, GameTurn.PLAYER1, 1000)
    cmemory = CondensedMemory(filename, 1000)
    # keys = random.sample(list(cmemory.keys()), 1000)
    keys = [1797558]
    for key in keys:
        move = memory1.get_move_from_memory(game, key, GameTurn.PLAYER1, 1000)
        cmove = cmemory.get(key)
        print(key, move, cmove)
        # assert move == cmove
#!/usr/bin/env python3
import time

import numpy as np
from lib import game, model, mcts, board, mmab
import torch
import pygame
import move_cache

MCTS_SEARCHES = 1000
# MCTS_SEARCHES = 5000
MCTS_BATCH_SIZE = 1
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600


class Session:
    BOT_PLAYER = game.PLAYER_BLACK
    USER_PLAYER = game.PLAYER_WHITE

    def __init__(self, model_file, player_moves_first, player_id, swap_players=False, dirichlet_pct=0.25, use_move_cache=False):
        self.model_file = model_file
        self.move_cache = move_cache.MoveCache(model_file) if use_move_cache else None
        self.model = model.Net(input_shape=model.OBS_SHAPE, actions_n=game.GAME_COLS)
        self.model.load_state_dict(torch.load(model_file, map_location=lambda storage, loc: storage))
        self.state = game.INITIAL_STATE
        # self.state = 7688512152522457160
        self.value = None
        self.player_moves_first = player_moves_first
        self.player_id = player_id
        self.moves = []
        self.mcts_store = mcts.MCTS(dirichlet_pct=dirichlet_pct)
        if swap_players:
            self.BOT_PLAYER = game.PLAYER_WHITE
            self.USER_PLAYER = game.PLAYER_BLACK

    def set_bot_player_as_black(self, black=True):
        if black:
            self.BOT_PLAYER = game.PLAYER_BLACK
            self.USER_PLAYER = game.PLAYER_WHITE
        else:
            self.BOT_PLAYER = game.PLAYER_WHITE
            self.USER_PLAYER = game.PLAYER_BLACK

    def reset(self):
        self.moves = []
        self.mcts_store.clear()
        self.state = game.INITIAL_STATE

    def move_player(self, col):
        self.moves.append(col)
        self.state, won = game.move(self.state, col, self.USER_PLAYER)
        return won

    def move_bot_mm(self, opponent=None):
        result = mmab.get_best_move(self.state, self.BOT_PLAYER, self.model)
        print(f"M:{result}")
        mm_action = np.argmax(result)
        action = int(mm_action)
        self.value = result[action]
        self.state, won = game.move(self.state, action, self.BOT_PLAYER)
        if opponent is not None:
            opponent.state = self.state
        return won

    def move_bot(self, opponent=None):
        data = None
        if self.move_cache is not None:
            data = self.move_cache.get(self.state)
        if data is None:
            self.mcts_store.search_batch(MCTS_SEARCHES, MCTS_BATCH_SIZE, self.state, self.BOT_PLAYER, self.model)
            probs, values = self.mcts_store.get_policy_value(self.state, tau=0)
            data = (probs, values)
            if self.move_cache is not None:
                self.move_cache.set(self.state, data)
        probs, values = data
        # print(f"P:{probs}")
        # print(f"V:{values}")
        action = np.random.choice(game.GAME_COLS, p=probs)
        self.value = values[action]
        self.moves.append(action)
        self.state, won = game.move(self.state, action, self.BOT_PLAYER)
        if opponent is not None:
            opponent.state = self.state
        return won

    def is_valid_move(self, move_col):
        return move_col in game.possible_moves(self.state)

    def is_draw(self):
        return len(game.possible_moves(self.state)) == 0

    def render(self):
        l = game.render(self.state)
        l = "\n".join(l)
        l = l.replace("0", 'O').replace("1", "X")
        board = "0123456\n-------\n" + l + "\n-------\n0123456"
        extra = ""
        if self.value is not None:
            extra = "Position evaluation: %.2f\n" % float(self.value)
        extra += f"{self.state}\n"
        return extra + "%s" % board

    def gui_render(self, screen, turn, possible_moves, message):
        state_list = game.decode_binary(self.state)
        board.draw_board(screen, state_list, turn, possible_moves, message)
        pygame.display.update()

def play_against_human(human_is_current, session):
    game_over = False
    value_label = ""
    label = ""
    while not game_over:
        current_player = 0 if human_is_current else 1
        print(session.render())
        print("===========================\n")
        if session.value is not None:
            value_label = "(%.2f)" % float(session.value)
        if human_is_current:
            possible_moves = game.possible_moves(session.state)
            session.gui_render(screen, current_player, possible_moves, "Click on checker to move... " + value_label)
            move = board.get_move(screen, possible_moves)
            won = session.move_player(int(move))
        else:
            session.gui_render(screen, current_player, [], "Bot is thinking... " + value_label)
            won = session.move_bot()
            # won = session.move_bot_mm()
        if won:
            label = f"{session.player_id if human_is_current else 'Bot'} won!"
            print(label)
            game_over = True
        elif session.is_draw():
            label = "Draw!"
            print(label)
            game_over = True
        human_is_current = not human_is_current
    print(session.render())
    possible_moves = game.possible_moves(session.state)
    session.gui_render(screen, current_player, possible_moves, "GAME OVER! " + label + " " + value_label)

def self_play(session1, session2, session_1_is_first, gui_each_turn=True):
    game_over = False
    value_label = ""
    session1.reset()
    session2.reset()
    while not game_over:
        current_player = 0 if session_1_is_first else 1
        # print(session1.render())
        # print("===========================\n")
        if current_player == 0:
            session = session1
            opponent = session2
        else:
            session = session2
            opponent = session1
        if session.value is not None:
            value_label = "(%.2f)" % float(session.value)
        if gui_each_turn:
            session.gui_render(screen, current_player, [], f"Bot {session.player_id} is thinking... {value_label}")
        won = session.move_bot(opponent=opponent)
        if won:
            label = f"Bot {session.player_id} won!"
            winner = session.player_id
            # print(label)
            game_over = True
        elif session.is_draw():
            label = "Draw!"
            # print(label)
            game_over = True
            winner = 'draw'
        session_1_is_first = not session_1_is_first
    # print(session.render())
    possible_moves = game.possible_moves(session.state)

    session.gui_render(screen, current_player, possible_moves, "GAME OVER! " + label + " " + value_label)
    return winner, session.state




def do_tournament(sessionNames):
    sessions = []
    for sessionName in sessionNames:
        sessions.append(Session('saves/Model128/' + sessionName, False, sessionName, dirichlet_pct=0.25))
    # play_against_human(human_is_current, session)
    results = {}

    for black_player in range(len(sessionNames)):
        for white_player in range(len(sessionNames)):
            if black_player >= white_player:
                continue
            print(sessionNames[black_player], sessionNames[white_player])
            session1 = sessions[black_player]
            session1.set_bot_player_as_black(True)
            session1Name = sessionNames[black_player]
            session2 = sessions[white_player]
            session2.set_bot_player_as_black(False)
            session2Name = sessionNames[white_player]
            for x in range(50):
                winner, state = self_play(session1, session2, x % 2 == 0, gui_each_turn=False)
                if winner == 'draw':
                    results[session1Name] = results.get(session1Name, 0) + 0.5
                    results[session2Name] = results.get(session2Name, 0) + 0.5
                else:
                    results[winner] = results.get(winner, 0) + 1
    print(results)
    sorted_dict = sorted(results.items(), key=lambda x: x[1], reverse=True)
    for k in sorted_dict:
        print(k)

if __name__ == "__main__":
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # screen = pygame.display.set_mode((1900, 1000))
    pygame.display.set_caption("Connect 4")

    human_is_current = True
    # human_is_current = False

    sessionNames = [
        'best_011_02100.dat',
        'best_018_01300.dat',
        'best_019_01400.dat',
        'best_020_01800.dat',
        'best_021_02100.dat',
        'best_022_00100.dat',
        'best_023_01400.dat'
    ]
    # do_tournament(sessionNames)
    #
    session1Name = 'best_020_01800.dat'
    session1 = Session('saves/Model128/' + session1Name, True, session1Name, dirichlet_pct=0.0)
    play_against_human(human_is_current, session1)

    time.sleep(3)


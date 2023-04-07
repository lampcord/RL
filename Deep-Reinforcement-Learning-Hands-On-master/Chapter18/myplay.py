#!/usr/bin/env python3
import time

import numpy as np
from lib import game, model, mcts, board
import torch
import pygame

MCTS_SEARCHES = 1000
MCTS_BATCH_SIZE = 4
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600


class Session:
    BOT_PLAYER = game.PLAYER_BLACK
    USER_PLAYER = game.PLAYER_WHITE

    def __init__(self, model_file, player_moves_first, player_id):
        self.model_file = model_file
        self.model = model.Net(input_shape=model.OBS_SHAPE, actions_n=game.GAME_COLS)
        self.model.load_state_dict(torch.load(model_file, map_location=lambda storage, loc: storage))
        self.state = game.INITIAL_STATE
        self.value = None
        self.player_moves_first = player_moves_first
        self.player_id = player_id
        self.moves = []
        self.mcts_store = mcts.MCTS(dirichlet_pct=0.0)

    def move_player(self, col):
        self.moves.append(col)
        self.state, won = game.move(self.state, col, self.USER_PLAYER)
        return won

    def move_bot(self, use_values=False):
        self.mcts_store.search_batch(MCTS_SEARCHES, MCTS_BATCH_SIZE, self.state, self.BOT_PLAYER, self.model)
        probs, values = self.mcts_store.get_policy_value(self.state, tau=0)
        print(f"P:{probs}")
        print(f"V:{values}")
        action = np.random.choice(game.GAME_COLS, p=probs)
        self.value = values[action]
        self.moves.append(action)
        self.state, won = game.move(self.state, action, self.BOT_PLAYER)
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
        return extra + "%s" % board

    def gui_render(self, screen, turn, possible_moves, message):
        state_list = game.decode_binary(self.state)
        board.draw_board(screen, state_list, turn, possible_moves, message)
        pygame.display.update()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Connect 4")
human_is_current = True
session = Session('saves/Test1CPU/best_026_01400.dat', human_is_current, 'Human')
if __name__ == "__main__":
    game_over = False
    value_label = ""
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
            won = session.move_bot(False)
        if won:
            label = f"{session.player_id if human_is_current else 'Bot'} won!"
            print(label)
            game_over = True
        elif session.is_draw():
            print("Draw!")
            game_over = True
        human_is_current = not human_is_current
    print(session.render())
    possible_moves = game.possible_moves(session.state)
    session.gui_render(screen, current_player, possible_moves, "GAME OVER! " + value_label)
    time.sleep(10)

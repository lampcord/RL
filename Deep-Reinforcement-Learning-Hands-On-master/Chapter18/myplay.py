#!/usr/bin/env python3
import time

import numpy as np
from lib import game, model, mcts, board, mmab
import torch
import pygame

MCTS_SEARCHES = 100
MCTS_BATCH_SIZE = 1
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600


class Session:
    BOT_PLAYER = game.PLAYER_BLACK
    USER_PLAYER = game.PLAYER_WHITE

    def __init__(self, model_file, player_moves_first, player_id, swap_players=False):
        self.model_file = model_file
        self.model = model.Net(input_shape=model.OBS_SHAPE, actions_n=game.GAME_COLS)
        self.model.load_state_dict(torch.load(model_file, map_location=lambda storage, loc: storage))
        self.state = game.INITIAL_STATE
        self.value = None
        self.player_moves_first = player_moves_first
        self.player_id = player_id
        self.moves = []
        # self.mcts_store = mcts.MCTS(dirichlet_pct=0.0)
        self.mcts_store = mcts.MCTS()
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

    def move_bot(self, use_values=False, opponent=None):
        result = mmab.get_best_move(self.state, self.BOT_PLAYER)
        self.mcts_store.search_batch(MCTS_SEARCHES, MCTS_BATCH_SIZE, self.state, self.BOT_PLAYER, self.model)
        probs, values = self.mcts_store.get_policy_value(self.state, tau=0)
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
            won = session.move_bot(False)
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
        won = session.move_bot(False, opponent=opponent)
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


'''
'best_001_00600.dat',
'best_002_01000.dat',
'best_003_01200.dat',
'best_004_02000.dat',
'best_006_01000.dat',
'best_007_01300.dat',
'best_008_02100.dat'
{'best_001_00600.dat': 42, 'best_002_01000.dat': 39, 'draw': 33, 'best_003_01200.dat': 47, 'best_004_02000.dat': 78, 'best_006_01000.dat': 58, 'best_007_01300.dat': 57, 'best_008_02100.dat': 66}
('best_004_02000.dat', 78)
('best_008_02100.dat', 66)
('best_006_01000.dat', 58)
('best_007_01300.dat', 57)
('best_003_01200.dat', 47)
('best_001_00600.dat', 42)
('best_002_01000.dat', 39)
('draw', 33)

Keeping top 2 from last run
'best_004_02000.dat',
'best_008_02100.dat'
'best_009_02300.dat',
'best_010_02400.dat',
'best_011_02500.dat',
'best_012_02700.dat',
'best_013_03200.dat',
{'best_004_02000.dat': 72, 'best_008_02100.dat': 50, 'best_009_02300.dat': 75, 'best_010_02400.dat': 57, 'best_011_02500.dat': 53, 'best_012_02700.dat': 57, 'best_013_03200.dat': 50, 'draw': 6}
('best_009_02300.dat', 75)
('best_004_02000.dat', 72)
('best_010_02400.dat', 57)
('best_012_02700.dat', 57)
('best_011_02500.dat', 53)
('best_008_02100.dat', 50)
('best_013_03200.dat', 50)
('draw', 6)

Keeping top 2 from last run
'best_004_02000.dat',
'best_009_02300.dat',
'best_014_03300.dat',
'best_015_03400.dat',
'best_016_03500.dat',
'best_017_00100.dat',
'best_018_00200.dat',
{'best_004_02000.dat': 48, 'best_009_02300.dat': 64, 'best_014_03300.dat': 53, 'best_015_03400.dat': 45, 'best_016_03500.dat': 57, 'draw': 22, 'best_017_00100.dat': 63, 'best_018_00200.dat': 68}
('best_018_00200.dat', 68)
('best_009_02300.dat', 64)
('best_017_00100.dat', 63)
('best_016_03500.dat', 57)
('best_014_03300.dat', 53)
('best_004_02000.dat', 48)
('best_015_03400.dat', 45)
('draw', 22)

Keeping top 3 from last run
'best_009_02300.dat',
'best_017_00100.dat',
'best_018_00200.dat',
'best_019_00300.dat',
'best_020_00500.dat',
'best_021_00700.dat',
'best_022_00900.dat',
{'best_017_00100.dat': 30, 'draw': 28, 'best_009_02300.dat': 49, 'best_018_00200.dat': 58, 'best_019_00300.dat': 56, 'best_020_00500.dat': 66, 'best_021_00700.dat': 50, 'best_022_00900.dat': 83}
('best_022_00900.dat', 83)
('best_020_00500.dat', 66)
('best_018_00200.dat', 58)
('best_019_00300.dat', 56)
('best_021_00700.dat', 50)
('best_009_02300.dat', 49)
('best_017_00100.dat', 30)
('draw', 28)

Keeping top 2 from last run
'best_020_00500.dat',
'best_022_00900.dat',
'best_023_01100.dat',
'best_024_00100.dat',
'best_025_00200.dat',
'best_025_01100.dat',
'best_026_00300.dat',
{'best_020_00500.dat': 32, 'best_022_00900.dat': 56, 'draw': 36, 'best_023_01100.dat': 47, 'best_024_00100.dat': 76, 'best_025_00200.dat': 74, 'best_025_01100.dat': 29, 'best_026_00300.dat': 70}
('best_024_00100.dat', 76)
('best_025_00200.dat', 74)
('best_026_00300.dat', 70)
('best_022_00900.dat', 56)
('best_023_01100.dat', 47)
('draw', 36)
('best_020_00500.dat', 32)
('best_025_01100.dat', 29)

Keeping top 3 from last run
'best_024_00100.dat',
'best_025_00200.dat',
'best_026_00300.dat',
'best_026_01400.dat',
'best_027_00600.dat',
'best_028_00700.dat',
'best_029_00800.dat',
{'best_024_00100.dat': 37, 'best_025_00200.dat': 44, 'best_026_00300.dat': 40, 'best_026_01400.dat': 58, 'draw': 54, 'best_027_00600.dat': 67, 'best_028_00700.dat': 67, 'best_029_00800.dat': 53}
('best_027_00600.dat', 67)
('best_028_00700.dat', 67)
('best_026_01400.dat', 58)
('draw', 54)
('best_029_00800.dat', 53)
('best_025_00200.dat', 44)
('best_026_00300.dat', 40)
('best_024_00100.dat', 37)

Keeping top 2 from last run
'best_027_00600.dat',
'best_028_00700.dat',
'best_030_00900.dat',
'best_031_01000.dat',
'best_032_01200.dat',
'best_033_01400.dat',
'best_034_01600.dat',
{'best_028_00700.dat': 45, 'draw': 88, 'best_027_00600.dat': 41, 'best_030_00900.dat': 48, 'best_031_01000.dat': 19, 'best_032_01200.dat': 62, 'best_033_01400.dat': 56, 'best_034_01600.dat': 61}
('draw', 88)
('best_032_01200.dat', 62)
('best_034_01600.dat', 61)
('best_033_01400.dat', 56)
('best_030_00900.dat', 48)
('best_028_00700.dat', 45)
('best_027_00600.dat', 41)
('best_031_01000.dat', 19)

Keeping top 2 from last run
'best_032_01200.dat',
'best_034_01600.dat',
'best_035_01700.dat',
'best_036_01900.dat',
'best_037_02000.dat',
'best_038_02100.dat',
'best_039_02400.dat',
{'best_032_01200.dat': 45, 'best_034_01600.dat': 61, 'draw': 27, 'best_035_01700.dat': 57, 'best_036_01900.dat': 58, 'best_037_02000.dat': 58, 'best_038_02100.dat': 54, 'best_039_02400.dat': 60}
('best_034_01600.dat', 61)
('best_039_02400.dat', 60)
('best_036_01900.dat', 58)
('best_037_02000.dat', 58)
('best_035_01700.dat', 57)
('best_038_02100.dat', 54)
('best_032_01200.dat', 45)

Keeping top 2 from last run
'best_034_01600.dat',
'best_039_02400.dat',
'best_040_03200.dat',
'best_041_03400.dat',
'best_042_04200.dat',
'best_043_04500.dat',
'best_044_04600.dat',
'best_045_04700.dat',
'best_046_04800.dat',
{'best_034_01600.dat': 80, 'best_039_02400.dat': 72, 'draw': 86, 'best_040_03200.dat': 96, 'best_041_03400.dat': 70, 'best_042_04200.dat': 39, 'best_043_04500.dat': 53, 'best_044_04600.dat': 68, 'best_045_04700.dat': 90, 'best_046_04800.dat': 66}
('best_040_03200.dat', 96)
('best_045_04700.dat', 90)
('draw', 86)
('best_034_01600.dat', 80)
('best_039_02400.dat', 72)
('best_041_03400.dat', 70)
('best_044_04600.dat', 68)
('best_046_04800.dat', 66)
('best_043_04500.dat', 53)
('best_042_04200.dat', 39)

New candidates
'best_040_03200.dat',
'best_045_04700.dat',
'best_047_00200.dat',
'best_048_00500.dat',
'best_049_01000.dat',
'best_050_01700.dat',
'best_051_01800.dat',
{'best_040_03200.dat': 71, 'best_047_00200.dat': 34, 2: 7.5, 0: 4.5, 3: 7.0, 'best_048_00500.dat': 54, 'best_049_01000.dat': 55, 4: 9.5, 'best_050_01700.dat': 73, 'best_051_01800.dat': 60, 'best_045_04700.dat': 26, 1: 4.0, 5: 8.5, 6: 6.0}
('best_050_01700.dat', 73)
('best_040_03200.dat', 71)
('best_051_01800.dat', 60)
('best_049_01000.dat', 55)
('best_048_00500.dat', 54)
('best_047_00200.dat', 34)
('best_045_04700.dat', 26)
(4, 9.5)
(5, 8.5)
(2, 7.5)
(3, 7.0)
(6, 6.0)
(0, 4.5)
(1, 4.0)
('best_050_01700.dat', 81.5)
('best_040_03200.dat', 75.5)
('best_051_01800.dat', 66.0)
('best_049_01000.dat', 64.5)
('best_048_00500.dat', 61.0)
('best_047_00200.dat', 41.5)
('best_045_04700.dat', 30.0)

Looks like our best by this measure is:
('best_050_01700.dat', 96)

files.txt

'''
sessionNames = [
'best_040_03200.dat',
'best_045_04700.dat',
'best_047_00200.dat',
'best_048_00500.dat',
'best_049_01000.dat',
'best_050_01700.dat',
'best_051_01800.dat'
]

def do_tournament(sessionNames):
    sessions = []
    for sessionName in sessionNames:
        sessions.append(Session('saves/Test1CPU/' + sessionName, False, sessionName))
    # play_against_human(human_is_current, session)
    results = {}

    for black_player in range(len(sessionNames)):
        for white_player in range(len(sessionNames)):
            if black_player >= white_player:
                continue
            print(sessionNames[black_player], sessionNames[white_player])
            session1 = sessions[black_player]
            session1.set_bot_player_as_black(True)
            session2 = sessions[white_player]
            session2.set_bot_player_as_black(False)
            for x in range(20):
                winner, state = self_play(session1, session2, x % 2 == 0, gui_each_turn=False)
                if winner == 'draw':
                    results[white_player] = results.get(white_player, 0) + 0.5
                    results[black_player] = results.get(black_player, 0) + 0.5
                else:
                    results[winner] = results.get(winner, 0) + 1
    print(results)
    sorted_dict = sorted(results.items(), key=lambda x: x[1], reverse=True)
    for k in sorted_dict:
        print(k)

if __name__ == "__main__":
    sessionNames = [
        'best_040_03200.dat',
        'best_045_04700.dat',
        'best_047_00200.dat',
        'best_048_00500.dat',
        'best_049_01000.dat',
        'best_050_01700.dat',
        'best_051_01800.dat'
    ]
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Connect 4")
    # human_is_current = True
    human_is_current = False
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Connect 4")

    # do_tournament(sessionNames)

    session1Name = 'best_040_03200.dat'
    session1 = Session('saves/Test1CPU/' + session1Name, True, session1Name)
    play_against_human(human_is_current, session1)

    time.sleep(10)


import time
import pygame
import numpy as np
import copy

background_color = (255, 255, 255)
line_color = (128, 128, 128)
win_line_color = (0, 0, 0)
text_color = (160, 160, 160)
blue_color = (0, 0, 255)
red_color = (255, 0, 0)

RED = 1
BLUE = 2
EMPTY = 0

dumpchar = {EMPTY: '.', BLUE: 'O', RED: 'X'}
win_test = np.array([
    [1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0, 1, 0, 0]
    ])
class TicTacToeEnv:
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode=None, reward_from_current_player=True):
        self.turn = RED
        self.reward_from_current_player = reward_from_current_player
        self.size = 3  # The size of the square grid
        self.window_size = 300  # The size of the PyGame window

        self.observation_space = np.full(shape=9, dtype=int, fill_value=EMPTY)
        self.action_space = np.zeros(shape=9, dtype=int)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    def reset(self):
        self.turn = RED
        self.observation_space[:] = EMPTY
        return self.observation_space

    def valid_actions(self):
        for ndx in range(self.observation_space.size):
            value = self.observation_space[ndx]
            if value == EMPTY:
                self.action_space[ndx] = 1
            else:
                self.action_space[ndx] = 0
        return self.action_space

    def is_game_over(self):
        legal_actions = self.get_legal_actions()
        return len(legal_actions) == 0

    def get_legal_actions(self):
        reward = self.check_for_win()
        if reward != 0:
            return []
        legal_moves = [x for x in range(9) if self.observation_space[x] == EMPTY]
        return legal_moves

    def dump(self):
        ndx = 0
        for y in range(3):
            for x in range(3):
                value = self.observation_space[ndx]
                print(dumpchar[value], end='')
                ndx += 1
            print()

        reward = self.check_for_win()
        print(f'T:{dumpchar[self.turn]} R:{reward}')

    def render_node(self, screen, pos, font, selected=False):
        if selected:
            text_color = (255, 0, 0)
        else:
            text_color = (0, 0, 0)
        self.render_board(pos, screen, 40, 6, False, 1)
        reward = self.check_for_win()
        label = f"{dumpchar[self.turn]} {reward}"
        text = font.render(label, True, text_color)
        text_rect = text.get_rect(center=(pos[0], pos[1] + 30))
        screen.blit(text, text_rect)


    def render_board(self, pos, screen, size, font_size=36, show_available_actions=True, line_thickness=5):
        cell_size = size / 3
        left_edge = pos[0] - size / 2
        right_edge = left_edge + size
        top_edge = pos[1] - size / 2
        bottom_edge = top_edge + size

        row = top_edge
        col = left_edge
        for r in range(4):
            pygame.draw.line(screen, line_color, (left_edge, row), (right_edge, row), line_thickness)
            row += cell_size
            pygame.draw.line(screen, line_color, (col, top_edge), (col, bottom_edge), line_thickness)
            col += cell_size

        big_font = pygame.font.Font(None, font_size * 3)  # Use the default font
        font = pygame.font.Font(None, font_size)  # Use the default font
        font_pos = [size / 6 + left_edge, size / 6 + top_edge]
        ndx = 0
        for row in range(3):
            for col in range(3):
                value = self.observation_space[ndx]
                paint_label = True
                if value == RED:
                    text_surface = big_font.render("X", True, red_color)
                elif value == BLUE:
                    text_surface = big_font.render("O", True, blue_color)
                elif show_available_actions:
                    text_surface = font.render(str(ndx), True, text_color)
                else:
                    paint_label = False

                if paint_label:
                    text_rect = text_surface.get_rect()
                    text_rect.center = font_pos
                    screen.blit(text_surface, text_rect)
                font_pos[0] += cell_size
                ndx += 1
            font_pos[0] = size / 6 + left_edge
            font_pos[1] += cell_size

        reward, t = self.check_for_win(include_test_number=True)
        if reward != 0:
            if t == 0:
                line_coords = ((0, size / 6), (size, size / 6))
            elif t == 1:
                line_coords = ((0, size / 2), (size, size / 2))
            elif t == 2:
                line_coords = ((0, size * 5 / 6), (size, size * 5 / 6))
            elif t == 3:
                line_coords = ((size / 6, 0), (size / 6, size))
            elif t == 4:
                line_coords = ((size / 2, 0), (size / 2, size))
            elif t == 5:
                line_coords = ((size * 5 / 6, 0), (size * 5 / 6, size))
            elif t == 6:
                line_coords = ((0, 0), (size, size))
            elif t == 7:
                line_coords = ((size, 0), (0, size))

            adjusted_coords = ((line_coords[0][0] + left_edge, line_coords[0][1] + top_edge), (line_coords[1][0] + left_edge, line_coords[1][1] + top_edge))
            pygame.draw.line(screen, win_line_color, adjusted_coords[0], adjusted_coords[1], line_thickness)

    def render(self):
        if self.window is None:
            pygame.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        self.window.fill(background_color)

        self.render_board((self.window_size / 2, self.window_size / 2), self.window, self.window_size, 36, True)

        pygame.display.flip()

    def step(self, action):
        valid_actions = self.valid_actions()
        if valid_actions[action] == 1:
            self.observation_space[action] = self.turn

        reward = self.check_for_win()
        if valid_actions[action] == 1:
            self.turn = RED if self.turn == BLUE else BLUE

        done = reward != 0 or np.sum(self.valid_actions()) == 0
        return self.observation_space, reward, done, {}

    def close(self):
        if self.window is not None:
            pygame.quit()
            self.window = None

    def get_result(self):
        winner = EMPTY
        for t in range(8):
            testarray = self.observation_space[win_test[t] == 1]
            redcount = np.count_nonzero(testarray == RED)
            if np.count_nonzero(self.observation_space[win_test[t] == 1] == RED) == 3:
                winner = RED
                break
            elif np.count_nonzero(self.observation_space[win_test[t] == 1] == BLUE) == 3:
                winner = BLUE
                break

        return winner

    def get_points_for_result(self, result):
        if result == self.turn:
            return 1
        elif result != EMPTY:
            return -1
        else:
            return 0

    def check_for_win(self, maximizing_player=None, include_test_number=False):
        if maximizing_player is None:
            maximizing_player = self.turn
        reward = 0
        winner = EMPTY
        for t in range(8):
            testarray = self.observation_space[win_test[t] == 1]
            redcount = np.count_nonzero(testarray == RED)
            if np.count_nonzero(self.observation_space[win_test[t] == 1] == RED) == 3:
                winner = RED
                break
            elif np.count_nonzero(self.observation_space[win_test[t] == 1] == BLUE) == 3:
                winner = BLUE
                break

        if winner != EMPTY:
            if self.reward_from_current_player:
                if maximizing_player == winner:
                    reward = 1
                else:
                    reward = -1
            else:
                if winner == RED:
                    reward = 1
                else:
                    reward = -1
        if include_test_number:
            return reward, t
        else:
            return reward
    def test_set(self, t):
        self.observation_space[:] = EMPTY
        self.observation_space[win_test[t] == 1] = RED

    def run_win_test(self):
        for t in range(8):
            self.test_set(t)
            self.render()
            time.sleep(1)

    def clone(self):
        new_env = TicTacToeEnv()
        new_env.reset()
        new_env.observation_space = copy.deepcopy(self.observation_space)
        new_env.turn = copy.deepcopy(self.turn)
        return new_env


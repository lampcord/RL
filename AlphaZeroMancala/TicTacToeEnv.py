import pygame
import numpy as np

grey = (128, 128, 128)
line_color = (255, 255, 255)
win_line_color = (0, 0, 0)
text_color = (160, 160, 160)
blue_color = (0, 0, 255)
red_color = (255, 0, 0)

RED = 1
BLUE = 2
EMPTY = 0

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

    def __init__(self, render_mode=None):
        self.turn = RED
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

    def render(self):
        if self.window is None:
            pygame.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        self.window.fill(grey)

        pygame.draw.line(self.window, line_color, (self.window_size / 3, 0), (self.window_size / 3, self.window_size), 5)
        pygame.draw.line(self.window, line_color, (2 * self.window_size / 3, 0), (2 * self.window_size / 3, self.window_size), 5)
        pygame.draw.line(self.window, line_color, (0, self.window_size / 3), (self.window_size, self.window_size / 3), 5)
        pygame.draw.line(self.window, line_color, (0, 2 * self.window_size / 3), (self.window_size, 2 * self.window_size / 3), 5)

        font_size = 36
        big_font = pygame.font.Font(None, font_size * 3)  # Use the default font
        font = pygame.font.Font(None, font_size)  # Use the default font
        pos = [self.window_size / 6, self.window_size / 6]
        ndx = 0
        for row in range(3):
            for col in range(3):
                value = self.observation_space[ndx]
                if value == RED:
                    text_surface = big_font.render("X", True, red_color)
                elif value == BLUE:
                    text_surface = big_font.render("O", True, blue_color)
                else:
                    text_surface = font.render(str(ndx), True, text_color)

                text_rect = text_surface.get_rect()
                text_rect.center = pos
                self.window.blit(text_surface, text_rect)
                pos[0] += self.window_size / 3
                ndx += 1
            pos[0] = self.window_size / 6
            pos[1] += self.window_size / 3

        reward, t = self.check_for_win()
        if reward != 0:
            if t == 0:
                line_coords = ((0, self.window_size / 6), (self.window_size, self.window_size / 6))
            elif t == 1:
                line_coords = ((0, self.window_size / 6), (self.window_size, self.window_size / 6))
            elif t == 2:
                line_coords = ((0, self.window_size / 6), (self.window_size, self.window_size / 6))
            elif t == 3:
                line_coords = ((0, self.window_size / 6), (self.window_size, self.window_size / 6))
            elif t == 4:
                line_coords = ((0, self.window_size / 6), (self.window_size, self.window_size / 6))
            elif t == 5:
                line_coords = ((0, self.window_size / 6), (self.window_size, self.window_size / 6))
            elif t == 6:
                line_coords = ((0, self.window_size / 6), (self.window_size, self.window_size / 6))
            elif t == 7:
                line_coords = ((0, self.window_size / 6), (self.window_size, self.window_size / 6))

            pygame.draw.line(self.window, win_line_color, line_coords[0], line_coords[1], 5)

        pygame.display.flip()

    def step(self, action):
        valid_actions = self.valid_actions()
        if valid_actions[action] == 1:
            self.observation_space[action] = self.turn
            self.turn = RED if self.turn == BLUE else BLUE

        reward, _ = self.check_for_win()
        done = reward != 0 or np.sum(self.valid_actions()) == 0
        return self.observation_space, reward, done, {}

    def close(self):
        if self.window is not None:
            pygame.quit()
            self.window = None

    def check_for_win(self):
        reward = 0
        for t in range(8):
            testarray = self.observation_space[win_test[t] == 1]
            redcount = np.count_nonzero(testarray == RED)
            if np.count_nonzero(self.observation_space[win_test[t] == 1] == RED) == 3:
                reward = 1
                break
            elif np.count_nonzero(self.observation_space[win_test[t] == 1] == BLUE) == 3:
                reward = -1
                break
        return reward, t

    def test_set(self, t):
        self.observation_space[:] = EMPTY
        self.observation_space[win_test[t] == 1] = RED
import pygame
import numpy as np

grey = (128, 128, 128)
line_color = (255, 255, 255)
text_color = (160, 160, 160)


class TicTacToeEnv:
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode=None):
        self.size = 3  # The size of the square grid
        self.window_size = 300  # The size of the PyGame window

        self.observation_space = np.zeros(9)
        self.action_space = np.zeros(9)

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
        font = pygame.font.Font(None, font_size)  # Use the default font
        pos = [self.window_size / 6, self.window_size / 6]
        ndx = 0
        for row in range(3):
            for col in range(3):
                text_surface = font.render(str(ndx), True, text_color)
                text_rect = text_surface.get_rect()
                text_rect.center = pos
                self.window.blit(text_surface, text_rect)
                pos[0] += self.window_size / 3
                ndx += 1
            pos[0] = self.window_size / 6
            pos[1] += self.window_size / 3

        pygame.display.flip()

    def close(self):
        if self.window is not None:
            pygame.quit()


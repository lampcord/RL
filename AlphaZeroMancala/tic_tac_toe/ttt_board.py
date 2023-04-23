import time

import pygame
from tic_tac_toe import ttt_game

background_color = (255, 255, 255)
line_color = (128, 128, 128)
win_line_color = (0, 0, 0)
text_color = (160, 160, 160)
blue_color = (0, 0, 255)
red_color = (255, 0, 0)

class TicTacToeBoard:
    def __init__(self):
        self.game = ttt_game.TicTacToeGame()
        self.window = None
        self.window_size = 300  # The size of the PyGame window

    def render_node(self, screen, state_int, turn, pos, font, selected=False):
        if selected:
            text_color = (255, 0, 0)
        else:
            text_color = (0, 0, 0)
        self.render_board(state_int, [], pos, screen, 40, 6, False, 1)
        label = f"{ttt_game.display_char[turn.value]}"
        text = font.render(label, True, text_color)
        text_rect = text.get_rect(center=(pos[0], pos[1] + 30))
        screen.blit(text, text_rect)

    def render_board(self, state_int, winning_set, pos, screen, size, font_size=36, show_available_actions=True, line_thickness=5):
        state_list = self.game.get_decoded_list(state_int)
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
                value = state_list[ndx]
                paint_label = True
                if value == 1:
                    text_surface = big_font.render("X", True, red_color)
                elif value == 2:
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

        if len(winning_set) != 0:
            line_coords = None
            if 0 in winning_set and 2 in winning_set:
                line_coords = ((0, size / 6), (size, size / 6))
            if 3 in winning_set and 5 in winning_set:
                line_coords = ((0, size / 2), (size, size / 2))
            if 6 in winning_set and 8 in winning_set:
                line_coords = ((0, size * 5 / 6), (size, size * 5 / 6))
            if 0 in winning_set and 6 in winning_set:
                line_coords = ((size / 6, 0), (size / 6, size))
            if 1 in winning_set and 7 in winning_set:
                line_coords = ((size / 2, 0), (size / 2, size))
            if 2 in winning_set and 8 in winning_set:
                line_coords = ((size * 5 / 6, 0), (size * 5 / 6, size))
            if 0 in winning_set and 8 in winning_set:
                line_coords = ((0, 0), (size, size))
            if 2 in winning_set and 6 in winning_set:
                line_coords = ((size, 0), (0, size))

            if line_coords is not None:
                adjusted_coords = ((line_coords[0][0] + left_edge, line_coords[0][1] + top_edge),
                                   (line_coords[1][0] + left_edge, line_coords[1][1] + top_edge))
                pygame.draw.line(screen, win_line_color, adjusted_coords[0], adjusted_coords[1], line_thickness)

    def render(self, state_int, winning_set=[]):
        if self.window is None:
            pygame.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        self.window.fill(background_color)

        self.render_board(state_int, winning_set, (self.window_size / 2, self.window_size / 2), self.window, self.window_size, 36, True)

        pygame.display.flip()

    def close(self):
        if self.window is not None:
            pygame.quit()
            self.window = None

if __name__ == "__main__":
    game = ttt_game.TicTacToeGame()
    board = TicTacToeBoard()
    board.render(game.get_initial_position())
    time.sleep(5)
    board.close()
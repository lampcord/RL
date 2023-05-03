import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
# self.screen = pygame.display.set_mode((1900, 1000))

BOARD_ROWS = 6
BOARD_COLS = 7
CELL_SIZE = min((WINDOW_WIDTH - 100) // BOARD_COLS, (WINDOW_HEIGHT - 100) // BOARD_ROWS)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 192, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREY = (190, 190, 190)
DARK_GREY = (96, 96, 96)

click_positions = []
cell_colors = [RED, BLUE]
font = pygame.font.Font(None, 24)


class C4Board:
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, game=None):
        self.screen = pygame.display.set_mode((width, height))
        self.width = width
        self.height = height
        self.game = game
        pygame.display.set_caption("Connect 4")

    def render_node(self, binary_state, turn, offset, font, selected, center=True):
        assert self.game is not None
        list_state = self.game.get_decoded_list(binary_state, turn)
        if center:
            total_width = BOARD_COLS * 9
            total_height = BOARD_ROWS * 9
            target_offset = [offset[0] - total_width / 2, offset[1] - total_height / 2]
        else:
            target_offset = offset
        turn_offset = [target_offset[0] + 5, target_offset[1] - 10]
        self.draw_node(9, target_offset, list_state, turn, [], cell_padding=0)
        pygame.draw.circle(self.screen, cell_colors[turn], turn_offset, 5)

    def draw_node(self, cell_size, offset, pos, turn, possible_moves, cell_padding=5, win_set=None):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                xpos = col * cell_size + offset[0]
                ypos = row * cell_size + offset[1]
                value = self.get_value_at(row, col, pos)
                cell_color = WHITE
                if value is not None:
                    cell_color = cell_colors[value]
                pygame.draw.rect(self.screen, DARK_GREY, (xpos, ypos, cell_size, cell_size), 0)
                if win_set and (col, row) in win_set:
                    pygame.draw.circle(self.screen, YELLOW, (xpos + cell_size // 2, ypos + cell_size // 2), cell_size // 2 - cell_padding)
                    pygame.draw.circle(self.screen, cell_color, (xpos + cell_size // 2, ypos + cell_size // 2), cell_size // 2 - 2 * cell_padding)
                else:
                    pygame.draw.circle(self.screen, cell_color, (xpos + cell_size // 2, ypos + cell_size // 2), cell_size // 2 - cell_padding)
                if row == 0:
                    if len(click_positions) <= col:
                        click_positions.append((xpos + cell_size // 2, ypos + cell_size // 2 - cell_size))
                    if col not in possible_moves:
                        continue
                    pygame.draw.circle(self.screen, cell_colors[turn], click_positions[col], cell_size // 2 - cell_padding)

    def draw_board(self, pos, turn, possible_moves, message, win_set=None):
        self.screen.fill(GREY)
        xoffset = (self.width - (CELL_SIZE * BOARD_COLS)) / 2
        yoffset = (self.height - (CELL_SIZE * BOARD_ROWS)) / 2
        text = font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(self.width / 2, self.height - 20))
        self.screen.blit(text, text_rect)
        self.draw_node(CELL_SIZE, (xoffset, yoffset), pos, turn, possible_moves, win_set=win_set)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def get_move(self, possible_moves):
        best_pos = None
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_coordinates = event.pos
                    print(f"Mouse clicked at {click_coordinates}")
                    best_pos = None
                    for test_click in range(len(click_positions)):
                        if test_click not in possible_moves:
                            continue
                        distance = (click_positions[test_click][0] - click_coordinates[0]) * (click_positions[test_click][0] - click_coordinates[0])
                        distance += (click_positions[test_click][1] - click_coordinates[1]) * (click_positions[test_click][1] - click_coordinates[1])
                        if distance < (CELL_SIZE / 2) * (CELL_SIZE / 2):
                            best_pos = test_click
                    if best_pos is not None:
                        return best_pos
            time.sleep(.3)

    def wait_for_click(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return
            time.sleep(.3)

    def get_value_at(self, row, col, pos):
        pos_col = BOARD_ROWS - row - 1
        pos_row = col
        row_values = pos[pos_row]
        if pos_col >= len(row_values):
            return None
        else:
            return row_values[pos_col]

def main():
    board = C4Board()
    testpos = [
      [1, 1, 1, 1, 0, 0],
      [0, 0, 0, 0],
      [1],
      [],
      [1, 1, 0],
      [1],
      [1, 1, 1, 1, 1, 1]
    ]
    possible_moves = [1,2,3,4,5]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        board.draw_board(testpos, 1, possible_moves, "")
        print(board.get_move(possible_moves))

if __name__ == "__main__":
    main()

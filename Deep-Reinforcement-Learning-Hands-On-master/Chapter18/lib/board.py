import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
BOARD_ROWS = 6
BOARD_COLS = 7
CELL_SIZE = min((WINDOW_WIDTH - 100) // BOARD_COLS, (WINDOW_HEIGHT - 100) // BOARD_ROWS)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)

def draw_board(screen, pos):
    screen.fill(GREY)
    xoffset = (WINDOW_WIDTH - (CELL_SIZE * BOARD_COLS)) / 2
    yoffset = (WINDOW_HEIGHT - (CELL_SIZE * BOARD_ROWS)) / 2
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            xpos = col * CELL_SIZE + xoffset
            ypos = row * CELL_SIZE + yoffset
            value = get_value_at(row, col, pos)
            cell_color = WHITE
            if value == 1:
                cell_color = BLUE
            elif value == 0:
                cell_color = RED
            pygame.draw.rect(screen, BLACK, (xpos, ypos, CELL_SIZE, CELL_SIZE), 0)
            pygame.draw.circle(screen, cell_color, (xpos + CELL_SIZE // 2, ypos + CELL_SIZE // 2), CELL_SIZE // 2 - 5)

def get_value_at(row, col, pos):
    pos_col = BOARD_ROWS - row - 1
    pos_row = col
    row_values = pos[pos_row]
    if pos_col >= len(row_values):
        return None
    else:
        return row_values[pos_col]

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Connect 4")
    testpos = [
      [1, 1, 1, 1, 0, 0],
      [0, 0, 0, 0],
      [1],
      [],
      [1, 1, 0],
      [1],
      [1, 1, 1, 1, 1, 1]
    ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_board(screen, testpos)
        pygame.display.update()

if __name__ == "__main__":
    main()

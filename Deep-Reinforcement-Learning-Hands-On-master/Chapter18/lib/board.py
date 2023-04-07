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

click_positions = []
cell_colors = [RED, BLUE]
font = pygame.font.Font(None, 24)


def draw_board(screen, pos, turn, possible_moves, message):
    screen.fill(GREY)
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 20))
    screen.blit(text, text_rect)
    xoffset = (WINDOW_WIDTH - (CELL_SIZE * BOARD_COLS)) / 2
    yoffset = (WINDOW_HEIGHT - (CELL_SIZE * BOARD_ROWS)) / 2
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            xpos = col * CELL_SIZE + xoffset
            ypos = row * CELL_SIZE + yoffset
            value = get_value_at(row, col, pos)
            cell_color = WHITE
            if value is not None:
                cell_color = cell_colors[value]
            pygame.draw.rect(screen, BLACK, (xpos, ypos, CELL_SIZE, CELL_SIZE), 0)
            pygame.draw.circle(screen, cell_color, (xpos + CELL_SIZE // 2, ypos + CELL_SIZE // 2), CELL_SIZE // 2 - 5)
            if row == 0:
                if len(click_positions) <= col:
                    click_positions.append((xpos + CELL_SIZE // 2, ypos + CELL_SIZE // 2 - CELL_SIZE))
                if col not in possible_moves:
                    continue
                pygame.draw.circle(screen, cell_colors[turn], click_positions[col], CELL_SIZE // 2 - 5)

def get_move(screen, possible_moves):
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
    possible_moves = [1,2,3,4,5]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_board(screen, testpos, 1, possible_moves, "")
        pygame.display.update()
        print(get_move(screen, possible_moves))

if __name__ == "__main__":
    main()

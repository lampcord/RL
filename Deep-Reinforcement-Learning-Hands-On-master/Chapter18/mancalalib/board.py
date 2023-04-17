import random
import pygame
import sys
from mancalalib import game

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 400
PADDING = 50
CELL_SIZE = min((WINDOW_WIDTH - PADDING * 2) // 8, (WINDOW_HEIGHT - PADDING * 2) // 2)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 192, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREY = (190, 190, 190)
DARK_GREY = (96, 96, 96)
font = pygame.font.Font(None, 24)
click_positions = {}


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


def draw_bucket(screen, rect, stone_size, num_stones):
    pygame.draw.rect(screen, DARK_GREY, rect, 0)
    pygame.draw.ellipse(screen, WHITE, rect)
    center = (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)
    pos_rect = (center[0] - stone_size // 2, center[1] - stone_size // 2, stone_size, stone_size)
    pygame.draw.ellipse(screen, BLACK, pos_rect)
    return center


def draw_node(screen, cell_size, offset, pos, turn, possible_moves, cell_padding=5):
    stone_size = 8

    # black castoff
    draw_bucket(screen, (offset[0], offset[1], cell_size, cell_size * 2), stone_size, pos[game.BLACK_CASTOFF_BUCKET])

    # white castoff
    draw_bucket(screen, (offset[0] + cell_size * 7, offset[1], cell_size, cell_size * 2),  stone_size, pos[game.WHITE_CASTOFF_BUCKET])

    bucket = game.WHITE_FIRST_BUCKET
    for bucket_offset in range(6):
        center = draw_bucket(screen, (offset[0] + cell_size * (bucket_offset + 1), offset[1] + cell_size, cell_size, cell_size), stone_size, pos[bucket])
        print(center)
        bucket += 1

    bucket = game.BLACK_FIRST_BUCKET
    for bucket_offset in range(6):
        center = draw_bucket(screen, (offset[0] + cell_size * (6 - bucket_offset), offset[1], cell_size, cell_size),  stone_size, pos[bucket])
        print(center)
        bucket -= 1


def draw_board(screen, pos, turn, possible_moves, message):
    screen.fill(GREY)
    xoffset = (WINDOW_WIDTH - (CELL_SIZE * 8)) // 2
    yoffset = (WINDOW_HEIGHT - (CELL_SIZE * 2)) // 2
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - PADDING // 2))
    screen.blit(text, text_rect)
    draw_node(screen, CELL_SIZE, (xoffset, yoffset), pos, turn, possible_moves)


def render_gui(screen, state_int, turn, message):
    state_list = game.decode_binary(state_int)
    possible_moves = game.possible_moves(state_int, turn)
    draw_board(screen, state_list, turn, possible_moves, message)
    pygame.display.update()
    get_move(screen, possible_moves)


def render(state_int, turn):
    state_list = game.decode_binary(state_int)
    possible_moves = game.possible_moves(state_int, turn)
    print('-' * 60)
    print(state_int)
    print('-' * 60)
    if turn == game.PLAYER_BLACK:
        print("     ", end='')
        ndx = game.BLACK_CASTOFF_BUCKET - 1
        move = 5
        while move >= 0:
            if move in possible_moves:
                print("{:>3} ".format(move), end='')
            else:
                print("  - ", end='')
            ndx -= 1
            move -= 1
        print("    Black's Turn")

    print("+---+---+---+---+---+---+---+---+")

    print("|   |", end='')
    ndx = game.BLACK_CASTOFF_BUCKET - 1
    for _ in range(6):
        print("{:>3}|".format(state_list[ndx]), end='')
        ndx -= 1
    print("   |")

    print("|{:>3}|".format(state_list[game.BLACK_CASTOFF_BUCKET]), end='')
    print("---+---+---+---+---+---", end='')
    print("|{:>3}|".format(state_list[game.WHITE_CASTOFF_BUCKET]))

    print("|   |", end='')
    ndx = game.WHITE_FIRST_BUCKET
    for _ in range(6):
        print("{:>3}|".format(state_list[ndx]), end='')
        ndx += 1
    print("   |")

    print("+---+---+---+---+---+---+---+---+")

    if turn == game.PLAYER_WHITE:
        print("     ", end='')
        ndx = game.WHITE_FIRST_BUCKET
        for move in range(6):
            if move in possible_moves:
                print("{:>3} ".format(move), end='')
            else:
                print("  - ", end='')
            ndx += 1
        print("    White's Turn")
    print('-' * 60)


# RULE1: if the last stone goes in your castoff bucket, you can keep going
def test_rule_1():
    state_int = game.encode_lists([6, 5, 4, 3, 2, 1, 3, 6, 5, 4, 3, 2, 1, 3])
    turn = game.PLAYER_WHITE
    render(state_int, turn)
    move = 5
    while move >= 0:
        possible_moves = game.possible_moves(state_int, turn)
        assert move in possible_moves
        state_int, winner, swap_players = game.move(state_int, move, turn)
        render(state_int, turn)
        assert not winner
        assert not swap_players
        move -= 1

    state_int, winner, swap_players = game.move(state_int, 1, turn)
    render(state_int, turn)
    assert not winner
    assert swap_players
    turn = game.get_opponent(turn)

    move = 5
    while move >= 0:
        possible_moves = game.possible_moves(state_int, turn)
        assert move in possible_moves
        state_int, winner, swap_players = game.move(state_int, move, turn)
        render(state_int, turn)
        assert not winner
        assert not swap_players
        move -= 1


# RULE2: if next player has no legal moves, all the stones remaining go into next player's opponent's castoff bucket
def test_rule_2():
    state_int = 148764069216649217
    turn = game.PLAYER_BLACK
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 5, turn)
    assert state_int == 4539628428650872833
    assert not swap_players
    render(state_int, turn)

    state_int = 148764069208260609
    turn = game.PLAYER_BLACK
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 5, turn)
    assert swap_players
    turn = game.get_opponent(turn)
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 0, turn)
    assert state_int == 4539628426520166401
    render(state_int, turn)


# RULE4: If the last piece you drop is in an empty hole on your side,
# you capture that piece and any pieces in the hole directly opposite.
def test_rule_4():
    state_int = 2311054832843284497
    turn = game.PLAYER_BLACK
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 2, turn)
    turn = game.get_opponent(turn)
    render(state_int, turn)
    assert state_int == 2313179504850174081
    assert swap_players

    turn = game.PLAYER_BLACK
    state_int = 148764067119728707
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 0, turn)
    render(state_int, turn)
    assert swap_players
    assert state_int == 73201369230622977


def play_human_against_random():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mancala")
    state_int = game.INITIAL_STATE
    done = False
    turn = game.PLAYER_WHITE
    while not done:
        print('')
        render(state_int, turn)
        render_gui(screen, state_int, turn, "White to move" if turn == game.PLAYER_WHITE else "Black to move")
        possible_moves = game.possible_moves(state_int, turn)
        if len(possible_moves) == 0:
            print('No legal moves!')
            turn = game.get_opponent(turn)
            break
        if turn == game.PLAYER_WHITE:
            move = random.choice(possible_moves)
        else:
            move = int(input("Enter move:"))
        print(f"Move {move}")
        state_int, winner, swap_players = game.move(state_int, move, turn)
        if swap_players:
            turn = game.get_opponent(turn)
        if winner is not None:
            message = "White " if winner == game.PLAYER_WHITE else "Black "
            message += "wins!"
            print(message)
            render(state_int, turn)
            render_gui(screen, state_int, turn, message)
            break

if __name__ == "__main__":
    # test_rule_1()
    # test_rule_2()
    # test_rule_4()
    play_human_against_random()
    # turn = game.PLAYER_BLACK
    # for _ in range(10):
    #     print('')
    #     state_int = game.encode_lists(game.generate_random_board())
    #     render(state_int,turn)
    #     turn = game.get_opponent(turn)
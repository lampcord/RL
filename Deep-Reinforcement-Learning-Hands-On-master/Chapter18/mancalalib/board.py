import math
import random
import time

import pygame
import sys
from mancalalib import game

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500
PADDING = 50
CELL_SIZE = min((WINDOW_WIDTH - PADDING * 2) // 8, (WINDOW_HEIGHT - PADDING * 2) // 2)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GREY = (190, 190, 190)
DARK_GREY = (96, 96, 96)
font = pygame.font.Font(None, 24)
click_positions = {}

def get_move(screen, possible_moves, turn):
    best_pos = None
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_coordinates = event.pos
                print(f"Mouse clicked at {click_coordinates}")
                for move in possible_moves:
                    bucket = move + 7 if turn == game.PLAYER_BLACK else move
                    cc = click_positions[bucket]
                    distance = (cc[0] - click_coordinates[0]) ** 2 + (cc[1] - click_coordinates[1]) ** 2
                    if distance < (CELL_SIZE // 2) ** 2:
                        return move
                return None

def draw_bucket(screen, rect, stone_size, num_stones, highlight, highlightcolor=YELLOW, background=True):
    if background:
        pygame.draw.rect(screen, DARK_GREY, rect, 0)
        pygame.draw.ellipse(screen, highlightcolor if highlight else WHITE, rect)
    center = (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)
    pos_rect = [center[0] - stone_size // 2, center[1] - stone_size // 2, stone_size, stone_size]
    cur_radius = stone_size * 5 // 4
    cur_direction = 0
    cur_rect = pos_rect
    for stone in range(num_stones):
        if stone == 0:
            pygame.draw.ellipse(screen, BLUE, pos_rect)
            cur_direction = 0
        elif stone < 7:
            cur_rect = list(pos_rect)
            cur_rect[0] += math.cos(cur_direction) * cur_radius
            cur_rect[1] += math.sin(cur_direction) * cur_radius
            pygame.draw.ellipse(screen, BLUE, cur_rect)
            cur_direction += 2 * math.pi / 6
        elif stone < 22:
            if stone == 7:
                cur_direction = math.pi / 6
                cur_radius *= 2
            cur_rect = list(pos_rect)
            cur_rect[0] += math.cos(cur_direction) * cur_radius
            cur_rect[1] += math.sin(cur_direction) * cur_radius
            pygame.draw.ellipse(screen, BLUE, cur_rect)
            cur_direction += 2 * math.pi / 15
        elif stone < 48:
            if stone == 22:
                cur_direction = 0
                cur_radius = cur_radius * 3 / 2
            cur_rect = list(pos_rect)
            cur_rect[0] += math.cos(cur_direction) * cur_radius
            cur_rect[1] += math.sin(cur_direction) * cur_radius
            pygame.draw.ellipse(screen, BLUE, cur_rect)
            cur_direction += 2 * math.pi / 26


    return center


def draw_node(screen, cell_size, offset, pos, turn, possible_moves, highlight_cells=[], player=None):
    stone_size = 14
    if len(highlight_cells) > 0:
        highlight_color = GREEN
    else:
        highlight_color = YELLOW
    # black castoff
    draw_bucket(screen, (offset[0], offset[1], cell_size, cell_size * 2), stone_size, pos[game.BLACK_CASTOFF_BUCKET],
                game.BLACK_CASTOFF_BUCKET in highlight_cells, highlight_color)

    # white castoff
    draw_bucket(screen, (offset[0] + cell_size * 7, offset[1], cell_size, cell_size * 2),  stone_size, pos[game.WHITE_CASTOFF_BUCKET],
                game.WHITE_CASTOFF_BUCKET in highlight_cells, highlight_color)

    bucket = game.WHITE_FIRST_BUCKET
    for bucket_offset in range(6):
        center = draw_bucket(screen, (offset[0] + cell_size * (bucket_offset + 1), offset[1] + cell_size, cell_size, cell_size), stone_size, pos[bucket],
                             (bucket_offset in possible_moves and turn == game.PLAYER_WHITE) or bucket in highlight_cells, highlight_color)
        if bucket not in click_positions:
            click_positions[bucket] = center
            print(click_positions)
        bucket += 1

    bucket = game.BLACK_FIRST_BUCKET
    for bucket_offset in range(6):
        center = draw_bucket(screen, (offset[0] + cell_size * (6 - bucket_offset), offset[1], cell_size, cell_size),  stone_size, pos[bucket],
                             (bucket_offset in possible_moves and turn == game.PLAYER_BLACK) or bucket in highlight_cells, highlight_color)
        if bucket not in click_positions:
            click_positions[bucket] = center
            print(click_positions)
        bucket += 1

    if player is not None:
        stones_on_board = 48
        for stones in pos:
            stones_on_board -= stones
        if stones_on_board > 0:
            y_pos = offset[1] - cell_size if player == game.PLAYER_BLACK else offset[1] + 2 * cell_size
            _ = draw_bucket(screen, (offset[0] + cell_size * 7 // 2, y_pos, cell_size, cell_size), stone_size, stones_on_board, False, background=False)



def draw_board(screen, pos, turn, possible_moves, message, highlight_cells=[], player=None):
    screen.fill(GREY)
    xoffset = (WINDOW_WIDTH - (CELL_SIZE * 8)) // 2
    yoffset = (WINDOW_HEIGHT - (CELL_SIZE * 2)) // 2
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - PADDING // 2))
    screen.blit(text, text_rect)
    draw_node(screen, CELL_SIZE, (xoffset, yoffset), pos, turn, possible_moves, highlight_cells, player)


def render_gui(screen, state_int, turn, message, animation=None):
    if animation is not None:
        last_state_list = None
        player = animation[0]
        for state_list in animation[1:]:
            highlight_cells = []
            if last_state_list:
                for ndx in range(len(state_list)):
                    if state_list[ndx] != last_state_list[ndx]:
                        highlight_cells.append(ndx)
            draw_board(screen, state_list, turn, [], f"Animating {'white' if player == game.PLAYER_WHITE else 'black'} player...", highlight_cells, player)
            pygame.display.update()
            last_state_list = list(state_list)
            time.sleep(.3)

    state_list = game.decode_binary(state_int)
    possible_moves = game.possible_moves(state_int, turn)
    draw_board(screen, state_list, turn, possible_moves, message)
    pygame.display.update()
    time.sleep(.3)


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

    turn = game.PLAYER_WHITE
    state_int = 1009096596887699713
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 5, turn)
    render(state_int, turn)
    assert swap_players
    assert state_int == 504550512320315649




def play_human_against_random():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mancala")
    state_int = game.INITIAL_STATE
    done = False
    turn = game.PLAYER_WHITE
    animation = None
    while not done:
        print('')
        render(state_int, turn)
        render_gui(screen, state_int, turn, "White to move" if turn == game.PLAYER_WHITE else "Black to move", animation)
        possible_moves = game.possible_moves(state_int, turn)
        if len(possible_moves) == 0:
            print('No legal moves!')
            turn = game.get_opponent(turn)
            break
        if turn == game.PLAYER_WHITE:
            move = random.choice(possible_moves)
            time.sleep(.5)
        else:
            # move = int(input("Enter move:"))
            # move = random.choice(possible_moves)
            while True:
                move = get_move(screen, possible_moves, turn)
                if move is not None:
                    break
        print(f"Move {move}")
        state_int, winner, swap_players, animation = game.move(state_int, move, turn, True)
        if swap_players:
            turn = game.get_opponent(turn)
        if winner is not None:
            if winner == game.PLAYER_WHITE:
                message = "White wins!"
            elif winner == game.PLAYER_BLACK:
                message = "Black wins!"
            else:
                message = "Draw!"
            print(message)
            render(state_int, turn)
            render_gui(screen, state_int, turn, message, None)
            time.sleep(2)
            break

if __name__ == "__main__":
    test_rule_1()
    test_rule_2()
    test_rule_4()
    # play_human_against_random()
    # turn = game.PLAYER_BLACK
    # for _ in range(10):
    #     print('')
    #     state_int = game.encode_lists(game.generate_random_board())
    #     render(state_int,turn)
    #     turn = game.get_opponent(turn)
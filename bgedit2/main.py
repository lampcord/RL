import os
import sys

import pygame
import pygame.draw
import pygame.image
import copy
import json
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Constants
FRAME = 40
BORDER = 5
CHECKER_SIZE = 40
TOTAL_WIDTH = 14 * CHECKER_SIZE
TOTAL_HEIGHT = 11 * CHECKER_SIZE
WINDOW_SIZE = (TOTAL_WIDTH + BORDER * 3 + FRAME * 2, TOTAL_HEIGHT + FRAME * 2)
CIRCLE_RADIUS = (CHECKER_SIZE - 2) // 2

C0_COLOR = (39, 33, 19)
C1_COLOR = (220, 200, 190)
BG_COLOR = (143, 192, 143)
LINE_COLOR = (64, 64, 64)
T0_COLOR = (235, 119, 34)
T1_COLOR = (128, 128, 128)
POS_TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (255, 0, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)
DBL_CUBE_COLOR = (192, 193, 255)
DBL_CUBE_TEXT_COLOR = (0, 0, 128)

POSITIONS_FILE_NAME = 'positions.json'

DICE_SIZE = 36
DOT_SIZE = 4
BUTTON_SIZE = 40

BAR_0_LOC = 24
BAR_1_LOC = 25
DIE_0_LOC = 26
DIE_1_LOC = 27
CUBE_LOC = 28
HAS_ROLLED_LOC = 29
RESET_LOC = 30
CLR_LOC = 31
SAVE_LOC = 32
SAVE_ALL_LOC = 33

theme = {}
theme["C0_COLOR"] = (39, 33, 19)
theme["C1_COLOR"] = (220, 200, 190)
theme["BG_COLOR"] = (143, 192, 143)
theme["LINE_COLOR"] = (64, 64, 64)
theme["T0_COLOR"] = (235, 119, 34)
theme["T1_COLOR"] = (128, 128, 128)
theme["POS_TEXT_COLOR"] = (255, 255, 255)
theme["BUTTON_COLOR"] = (255, 0, 0)
theme["BUTTON_TEXT_COLOR"] = (255, 255, 255)
theme["DBL_CUBE_COLOR"] = (192, 193, 255)
theme["DBL_CUBE_TEXT_COLOR"] = (0, 0, 128)
with open('default.json', 'w') as json_file:
    json.dump(theme, json_file, indent=4)

theme_file_name = None
theme_dir = None
if len(sys.argv) > 1:
    theme_file_name = sys.argv[1]
    theme_dir = theme_file_name.split('.')[0]
    if not os.path.exists(theme_dir):
        os.makedirs(theme_dir)
if len(sys.argv) > 2:
    theme_dir = sys.argv[2]
if len(sys.argv) > 3:
    POSITIONS_FILE_NAME = sys.argv[3]

if theme_file_name:
    try:
        with open(theme_file_name, 'r') as json_file:
            theme = json.load(json_file)
        C0_COLOR = theme["C0_COLOR"]
        C1_COLOR = theme["C1_COLOR"]
        BG_COLOR = theme["BG_COLOR"]
        LINE_COLOR = theme["LINE_COLOR"]
        T0_COLOR = theme["T0_COLOR"]
        T1_COLOR = theme["T1_COLOR"]
        POS_TEXT_COLOR = theme["POS_TEXT_COLOR"]
        BUTTON_COLOR = theme["BUTTON_COLOR"]
        BUTTON_TEXT_COLOR = theme["BUTTON_TEXT_COLOR"]
        DBL_CUBE_COLOR = theme["DBL_CUBE_COLOR"]
        DBL_CUBE_TEXT_COLOR = theme["DBL_CUBE_TEXT_COLOR"]

    except Exception as e:
        pass

# Initialize the window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Backgammon Position Editor")

# Create a blank image to represent the backgammon board
board_image = pygame.Surface(WINDOW_SIZE)
board_image.fill(BG_COLOR)

# Initialize a clock for controlling the frame rate
clock = pygame.time.Clock()

font = pygame.font.Font(None, 24)

'''
0   4
1 3 5
2   6
'''
dot_offsets = {}
dot_offsets[0] = (-2 * DOT_SIZE, -2 * DOT_SIZE)
dot_offsets[1] = (-2 * DOT_SIZE, 0)
dot_offsets[2] = (-2 * DOT_SIZE, 2 * DOT_SIZE)
dot_offsets[3] = (0, 0)
dot_offsets[4] = (2 * DOT_SIZE, -2 * DOT_SIZE)
dot_offsets[5] = (2 * DOT_SIZE, 0)
dot_offsets[6] = (2 * DOT_SIZE, 2 * DOT_SIZE)

dots = {}
dots[1] = [3]
dots[2] = [0, 6]
dots[3] = [0, 3, 6]
dots[4] = [0, 2, 4, 6]
dots[5] = [0, 2, 3, 4, 6]
dots[6] = [0, 1, 2, 4, 5, 6]

cube_values = {}
cube_values[-6] = 64
cube_values[-5] = 32
cube_values[-4] = 16
cube_values[-3] = 8
cube_values[-2] = 4
cube_values[-1] = 2
cube_values[0] = 64
cube_values[1] = 2
cube_values[2] = 4
cube_values[3] = 8
cube_values[4] = 16
cube_values[5] = 32
cube_values[6] = 64

# Position data (you can customize this)
starting_checkers = [2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5, -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2, 0, 0]
clear_checkers =    [0, 0, 0, 0, 0,  0, 0,  0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]

try:
    # Attempt to open and read the JSON file
    with open(POSITIONS_FILE_NAME, 'r') as json_file:
        positions = json.load(json_file)

except Exception as e:
    positions = []

position = {}
position["checkers"] = list(starting_checkers)
position["turn"] = 0
position["has_rolled"] = True
position["dice"] = [1, 1]
position["cube"] = 0
locations = {}


def draw_slot(target, x, y, cnt, delta):
    color = C0_COLOR
    text_color = C1_COLOR
    if cnt < 0:
        color = C1_COLOR
        text_color = C0_COLOR
        cnt = -cnt

    for c in range(cnt):
        draw_checker(color, target, x, y)
        if c >= 4:
            break
        y += delta * CHECKER_SIZE

    if cnt > 5:
        display_text(x, y, str(cnt), text_color, target)


def draw_bar(pos, target):
    x = CHECKER_SIZE / 2 + FRAME + CHECKER_SIZE * 6 + BORDER / 2
    y = CHECKER_SIZE * 3 + FRAME
    locations[BAR_0_LOC] = (x, y)

    if pos["checkers"][BAR_0_LOC] > 0:
        draw_checker(C0_COLOR, target, x, y)
    if pos["checkers"][BAR_0_LOC] > 1:
        display_text(x, y, str(pos["checkers"][BAR_0_LOC]), C1_COLOR, target)

    y = TOTAL_HEIGHT - CHECKER_SIZE * 3 + FRAME
    locations[BAR_1_LOC] = (x, y)

    if pos["checkers"][BAR_1_LOC] < 0:
        draw_checker(C1_COLOR, target, x, y)
    if pos["checkers"][BAR_1_LOC] < -1:
        display_text(x, y, str(abs(pos["checkers"][BAR_1_LOC])), C0_COLOR, target)


def draw_checker(color, target, x, y):
    gfxdraw.aacircle(target, int(x), int(y), CIRCLE_RADIUS, LINE_COLOR)
    gfxdraw.filled_circle(target, int(x), int(y), CIRCLE_RADIUS, LINE_COLOR)
    gfxdraw.aacircle(target, int(x), int(y), CIRCLE_RADIUS - 2, color)
    gfxdraw.filled_circle(target, int(x), int(y), CIRCLE_RADIUS - 2, color)


def draw_triangle(target, x, y, delta, ndx):
    color = T0_COLOR if ndx % 2 == 0 else T1_COLOR
    gfxdraw.filled_trigon(target, x - CIRCLE_RADIUS, y, x + CIRCLE_RADIUS, y, x, y + delta * CHECKER_SIZE * 5, color)
    gfxdraw.aatrigon(target, x - CIRCLE_RADIUS, y, x + CIRCLE_RADIUS, y, x, y + delta * CHECKER_SIZE * 5, LINE_COLOR)


def draw_button(target, x, y, text):
    x -= BUTTON_SIZE / 2
    y -= BUTTON_SIZE / 2
    pygame.draw.rect(target, LINE_COLOR, pygame.Rect(x, y, BUTTON_SIZE, BUTTON_SIZE), 30, 10)
    pygame.draw.rect(target, BUTTON_COLOR, pygame.Rect(x + 2, y + 2, BUTTON_SIZE - 4, BUTTON_SIZE - 4), 30, 10)
    x += DICE_SIZE / 2
    y += DICE_SIZE / 2
    display_text(x, y, text, BUTTON_TEXT_COLOR, target)


def draw_interface(target):
    x = FRAME + CHECKER_SIZE / 2
    y = FRAME + 5 * CHECKER_SIZE + CHECKER_SIZE / 2
    draw_button(target, x, y, "R/D")
    locations[HAS_ROLLED_LOC] = (x, y)

    x += CHECKER_SIZE
    draw_button(target, x, y, "RST")
    locations[RESET_LOC] = (x, y)

    x += CHECKER_SIZE
    draw_button(target, x, y, "CLR")
    locations[CLR_LOC] = (x, y)

    x += CHECKER_SIZE

    x += CHECKER_SIZE
    draw_button(target, x, y, "ALL")
    locations[SAVE_ALL_LOC] = (x, y)

    x += CHECKER_SIZE
    draw_button(target, x, y, "SAV")
    locations[SAVE_LOC] = (x, y)


def draw_cube(pos, target):
    x = WINDOW_SIZE[0] - FRAME / 2
    if pos["cube"] == 0:
        y = CHECKER_SIZE * 5 + CHECKER_SIZE / 2 + FRAME
    elif pos["cube"] < 0:
        y = FRAME / 2 + CHECKER_SIZE
    else:
        y = WINDOW_SIZE[1] - FRAME / 2 - CHECKER_SIZE

    x -= DICE_SIZE / 2
    y -= DICE_SIZE / 2
    pygame.draw.rect(target, LINE_COLOR, pygame.Rect(x, y, DICE_SIZE, DICE_SIZE), 30, 10)
    pygame.draw.rect(target, DBL_CUBE_COLOR, pygame.Rect(x + 2, y + 2, DICE_SIZE - 4, DICE_SIZE - 4), 30, 10)
    locations[CUBE_LOC] = (x, y)

    x += DICE_SIZE / 2
    y += DICE_SIZE / 2
    value = cube_values[pos["cube"]]
    display_text(x, y, str(value), DBL_CUBE_TEXT_COLOR, target)


def draw_die(target, x, y, color, dot_color, number):
    x -= DICE_SIZE / 2
    y -= DICE_SIZE / 2
    pygame.draw.rect(target, LINE_COLOR, pygame.Rect(x, y, DICE_SIZE, DICE_SIZE), 30, 10)
    pygame.draw.rect(target, color, pygame.Rect(x + 2, y + 2, DICE_SIZE - 4, DICE_SIZE - 4), 30, 10)
    x += DICE_SIZE / 2
    y += DICE_SIZE / 2

    for dot in dots[number]:
        dx, dy = dot_offsets[dot]
        gfxdraw.aacircle(target, int(x + dx), int(y + dy), DOT_SIZE - 1, dot_color)
        gfxdraw.filled_circle(target, int(x + dx), int(y + dy), DOT_SIZE - 1, dot_color)


def draw_dice(pos, target):
    if pos["turn"] == 0:
        die_color = C0_COLOR
        dot_color = C1_COLOR
    else:
        die_color = C1_COLOR
        dot_color = C0_COLOR

    if pos["has_rolled"]:
        x = FRAME + CHECKER_SIZE * 9 + BORDER + CHECKER_SIZE / 2
        y = CHECKER_SIZE * 5 + CHECKER_SIZE / 2 + FRAME
        draw_die(target, x, y, die_color, dot_color, pos["dice"][0])
        locations[DIE_0_LOC] = (x, y)

        x += CHECKER_SIZE
        draw_die(target, x, y, die_color, dot_color, pos["dice"][1])
        locations[DIE_1_LOC] = (x, y)
    else:
        x = FRAME / 2
        y = FRAME + CHECKER_SIZE * 5
        draw_die(target, x, y, die_color, dot_color, 1)
        locations[DIE_0_LOC] = (x, y)

        y += CHECKER_SIZE
        draw_die(target, x, y, die_color, dot_color, 1)
        locations[DIE_1_LOC] = (x, y)


def spares(side, pos):
    spares = 15
    if side == 0:
        for c in pos["checkers"]:
            if c > 0:
                spares -= c
    else:
        for c in pos["checkers"]:
            if c < 0:
                spares += c
    return spares


def is_vali_position(pos):
    return spares(0, pos) >= 0 and spares(1, pos) >= 0 and pos["checkers"][BAR_0_LOC] >= 0 and pos["checkers"][BAR_1_LOC] <= 0


def draw_pip_count(pos, target):
    pip0 = 0
    pip1 = 0
    loc0_value = 24
    for ndx in range(24):
        c = pos["checkers"][ndx]
        loc1_value = 25 - loc0_value

        if c > 0:
            pip0 += c * loc0_value
        if c < 0:
            pip1 += abs(c) * loc1_value
        loc0_value -= 1

    pip0 += 25 * pos["checkers"][BAR_0_LOC]
    pip1 += 25 * abs(pos["checkers"][BAR_1_LOC])

    x = WINDOW_SIZE[0] - FRAME
    y = FRAME / 2
    display_text(x, y, f"({str(pip1)})", POS_TEXT_COLOR, target)
    y = WINDOW_SIZE[1] - FRAME / 2
    display_text(x, y, f"({str(pip0)})", POS_TEXT_COLOR, target)


def draw_board(pos, target):
    x = CHECKER_SIZE / 2 + FRAME
    y = CHECKER_SIZE / 2 + FRAME - 1

    target.fill(BG_COLOR)
    gfxdraw.box(target, (0, 0, WINDOW_SIZE[0], FRAME), LINE_COLOR)
    gfxdraw.box(target, (0, WINDOW_SIZE[1] - FRAME, WINDOW_SIZE[0], FRAME), LINE_COLOR)
    gfxdraw.box(target, (0, 0, FRAME, WINDOW_SIZE[1]), LINE_COLOR)
    gfxdraw.box(target, (WINDOW_SIZE[0] - FRAME, 0, FRAME, WINDOW_SIZE[1]), LINE_COLOR)
    gfxdraw.box(target, (CHECKER_SIZE * 6 + FRAME, 0, BORDER, WINDOW_SIZE[1]), LINE_COLOR)
    gfxdraw.box(target, (CHECKER_SIZE * 7 + FRAME, 0, BORDER, WINDOW_SIZE[1]), LINE_COLOR)
    gfxdraw.box(target, (CHECKER_SIZE * 13 + BORDER * 2 + FRAME, 0, BORDER, WINDOW_SIZE[1]), LINE_COLOR)

    ndx = 0
    start_slot_num = 1
    slot_delta = 1
    if pos["turn"] == 0:
        start_slot_num = 24
        slot_delta = -1
    slot_y = y - FRAME / 2 - CHECKER_SIZE / 2
    for c in range(6):
        draw_triangle(target, int(x), int(y - CIRCLE_RADIUS), 1, ndx)
        draw_slot(target, x, y, pos["checkers"][ndx], 1)
        display_text(x, slot_y, str(start_slot_num), POS_TEXT_COLOR, target)
        start_slot_num += slot_delta
        locations[ndx] = (x, y)
        x += CHECKER_SIZE
        ndx += 1

    x += CHECKER_SIZE + BORDER
    for c in range(6):
        draw_triangle(target, int(x), int(y - CIRCLE_RADIUS), 1, ndx)
        draw_slot(target, x, y, pos["checkers"][ndx], 1)
        display_text(x, slot_y, str(start_slot_num), POS_TEXT_COLOR, target)
        start_slot_num += slot_delta
        locations[ndx] = (x, y)
        x += CHECKER_SIZE
        ndx += 1

    x -= CHECKER_SIZE
    y = WINDOW_SIZE[1] - FRAME - CHECKER_SIZE / 2
    slot_y = y + FRAME / 2 + CHECKER_SIZE / 2
    for c in range(6):
        draw_triangle(target, int(x), int(y + CIRCLE_RADIUS), -1, ndx)
        draw_slot(target, x, y, pos["checkers"][ndx], -1)
        display_text(x, slot_y, str(start_slot_num), POS_TEXT_COLOR, target)
        start_slot_num += slot_delta
        locations[ndx] = (x, y)
        x -= CHECKER_SIZE
        ndx += 1

    x -= CHECKER_SIZE + BORDER
    for c in range(6):
        draw_triangle(target, int(x), int(y + CIRCLE_RADIUS), -1, ndx)
        draw_slot(target, x, y, pos["checkers"][ndx], -1)
        display_text(x, slot_y, str(start_slot_num), POS_TEXT_COLOR, target)
        start_slot_num += slot_delta
        locations[ndx] = (x, y)
        x -= CHECKER_SIZE
        ndx += 1

    x = CHECKER_SIZE * 13 + BORDER * 3 + FRAME + 2
    y = FRAME + 2
    num_spares = spares(1, pos)
    for c in range(num_spares):
        gfxdraw.box(target, (x, y, CHECKER_SIZE - 5, 6), C0_COLOR)
        gfxdraw.box(target, (x + 1, y + 1, CHECKER_SIZE - 7, 4), C1_COLOR)
        y += 8
        if c % 5 == 4:
            y += 3

    y = WINDOW_SIZE[1] - FRAME - 8
    num_spares = spares(0, pos)
    for c in range(num_spares):
        gfxdraw.box(target, (x, y, CHECKER_SIZE - 5, 6), C0_COLOR)
        y -= 8
        if c % 5 == 4:
            y -= 3

    draw_bar(pos, target)

    draw_dice(pos, target)

    draw_cube(pos, target)

    draw_pip_count(pos, target)


def display_text(x, y, text, color, target):
    text_surface = font.render(text, True, color)  # Text, antialiasing, color
    x -= text_surface.get_width() // 2
    y -= text_surface.get_height() // 2
    target.blit(text_surface, (x, y))  # Position of the text


def get_ndx_for_click(x, y):
    best = 0
    best_distance = 1000000
    for c in range(len(locations)):
        tx, ty = locations.get(c, (0, 0))
        distance = (x - tx) * (x - tx) + (y - ty) * (y - ty)
        if distance < best_distance:
            best = c
            best_distance = distance
    return best


def handle_mouse_click(event):
    ndx = get_ndx_for_click(event.pos[0], event.pos[1])

    if ndx == DIE_0_LOC:
        if event.button == 1:
            position["dice"][0] += 1
            if position["dice"][0] > 6:
                position["dice"][0] = 1
        if event.button == 2:
            position["turn"] = 1 - position["turn"]
        if event.button == 3:
            position["dice"][0] -= 1
            if position["dice"][0] < 1:
                position["dice"][0] = 6

    elif ndx == DIE_1_LOC:
        if event.button == 1:
            position["dice"][1] += 1
            if position["dice"][1] > 6:
                position["dice"][1] = 1
        if event.button == 2:
            position["turn"] = 1 - position["turn"]
        if event.button == 3:
            position["dice"][1] -= 1
            if position["dice"][1] < 1:
                position["dice"][1] = 6

    elif ndx == CUBE_LOC:
        if event.button == 1 and position["cube"] < 6:
            position["cube"] += 1
        if event.button == 2:
            position["cube"] = 0
        if event.button == 3 and position["cube"] > -6:
            position["cube"] -= 1

    elif ndx == HAS_ROLLED_LOC:
        position["has_rolled"] = not position["has_rolled"]

    elif ndx == RESET_LOC:
        position["checkers"] = list(starting_checkers)

    elif ndx == CLR_LOC:
        position["checkers"] = list(clear_checkers)

    elif ndx == SAVE_LOC:
        save_position(False)

    elif ndx == SAVE_ALL_LOC:
        save_position(True)

    else:
        hold_position = list(position["checkers"])

        if event.button == 1:
            position["checkers"][ndx] += 1
        if event.button == 2:
            position["checkers"][ndx] = 0
        if event.button == 3:
            position["checkers"][ndx] -= 1

        if not is_vali_position(position):
            position["checkers"] = hold_position


def save_position(all_files):
    if all_files:
        for x in range(len(positions)):
            pos = positions[x]
            filename = 'position_{:06d}.png'.format(x)
            if theme_dir:
                filename = theme_dir + '/' + filename
            draw_board(pos, board_image)
            pygame.image.save(board_image, filename)

    else:
        filename = 'position_{:06d}.png'.format(len(positions))
        if theme_dir:
            filename = theme_dir + '/' + filename
        positions.append(copy.deepcopy(position))
        with open(POSITIONS_FILE_NAME, 'w') as json_file:
            json.dump(positions, json_file, indent=4)

        pygame.image.save(board_image, filename)

    # Save the result as a black and white PNG file


def edit_position():
    # Game loop
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                handle_mouse_click(event)

        # Clear the screen
        screen.fill(BG_COLOR)

        # Draw the backgammon board
        draw_board(position, board_image)

        screen.blit(board_image, (0, 0))

        draw_interface(screen)

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        clock.tick(60)

if __name__ == "__main__":
    edit_position()

    # Quit Pygame
    pygame.quit()

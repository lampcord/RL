import pygame
import pygame.draw
import pygame.image
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
C0_COLOR = (39, 33, 19)
C1_COLOR = (220, 200, 190)
BG_COLOR = (143, 192, 143)
LINE_COLOR = (64, 64, 64)
CIRCLE_RADIUS = (CHECKER_SIZE - 2) // 2
T1_COLOR = (235, 119, 34)
T2_COLOR = (128, 128, 128)
BAR_0_LOC = 24
BAR_1_LOC = 25
DIE_0_LOC = 26
DIE_1_LOC = 27
DICE_SIZE = 36
DOT_SIZE = 4

# Initialize the window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Backgammon Position Editor")

# Create a blank image to represent the backgammon board
board_image = pygame.Surface(WINDOW_SIZE)
board_image.fill(BG_COLOR)

# Initialize a clock for controlling the frame rate
clock = pygame.time.Clock()

font = pygame.font.Font(None, 32)

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

# Position data (you can customize this)
position = {}
checkers = [2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5, -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2, 0, 0]
position["checkers"] = checkers
position["turn"] = 1
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


def draw_bar(target):
    x = CHECKER_SIZE / 2 + FRAME + CHECKER_SIZE * 6 + BORDER / 2
    y = CHECKER_SIZE * 3 + FRAME
    locations[BAR_0_LOC] = (x, y)

    if position["checkers"][BAR_0_LOC] > 0:
        draw_checker(C0_COLOR, target, x, y)
    if position["checkers"][BAR_0_LOC] > 1:
        display_text(x, y, str(position["checkers"][BAR_0_LOC]), C1_COLOR, target)

    y = TOTAL_HEIGHT - CHECKER_SIZE * 3 + FRAME
    locations[BAR_1_LOC] = (x, y)

    if position["checkers"][BAR_1_LOC] < 0:
        draw_checker(C1_COLOR, target, x, y)
    if position["checkers"][BAR_1_LOC] < -1:
        display_text(x, y, str(abs(position["checkers"][BAR_1_LOC])), C0_COLOR, target)


def draw_checker(color, target, x, y):
    gfxdraw.aacircle(target, int(x), int(y), CIRCLE_RADIUS, LINE_COLOR)
    gfxdraw.filled_circle(target, int(x), int(y), CIRCLE_RADIUS, LINE_COLOR)
    gfxdraw.aacircle(target, int(x), int(y), CIRCLE_RADIUS - 2, color)
    gfxdraw.filled_circle(target, int(x), int(y), CIRCLE_RADIUS - 2, color)


def draw_triangle(target, x, y, delta, ndx):
    color = T1_COLOR if ndx % 2 == 0 else T2_COLOR
    gfxdraw.aatrigon(target, x - CIRCLE_RADIUS, y, x + CIRCLE_RADIUS, y, x, y + delta * CHECKER_SIZE * 5, color)
    gfxdraw.filled_trigon(target, x - CIRCLE_RADIUS, y, x + CIRCLE_RADIUS, y, x, y + delta * CHECKER_SIZE * 5, color)


def draw_die(target, x, y, color, dot_color, number):
    x -= DICE_SIZE / 2
    y -= DICE_SIZE / 2
    pygame.draw.rect(target, LINE_COLOR, pygame.Rect(x, y, DICE_SIZE, DICE_SIZE), 30, 10)
    pygame.draw.rect(target, color, pygame.Rect(x + 2, y + 2, DICE_SIZE - 4, DICE_SIZE - 4), 30, 10)
    x += DICE_SIZE / 2
    y += DICE_SIZE / 2
    # display_text(x, y, str(number), dot_color, target)

    for dot in dots[number]:
        dx, dy = dot_offsets[dot]
        gfxdraw.aacircle(target, int(x + dx), int(y + dy), DOT_SIZE - 1, dot_color)
        gfxdraw.filled_circle(target, int(x + dx), int(y + dy), DOT_SIZE - 1, dot_color)


def draw_dice(target):
    if position["turn"] == 0:
        die_color = C0_COLOR
        dot_color = C1_COLOR
    else:
        die_color = C1_COLOR
        dot_color = C0_COLOR

    x = FRAME + CHECKER_SIZE * 9 + BORDER + CHECKER_SIZE / 2
    y = CHECKER_SIZE * 5 + CHECKER_SIZE / 2 + FRAME
    draw_die(target, x, y, die_color, dot_color, position["dice"][0])
    locations[DIE_0_LOC] = (x, y)

    x += CHECKER_SIZE
    draw_die(target, x, y, die_color, dot_color, position["dice"][1])
    locations[DIE_1_LOC] = (x, y)

def spares(side):
    spares = 15
    if side == 0:
        for c in position["checkers"]:
            if c > 0:
                spares -= c
    else:
        for c in position["checkers"]:
            if c < 0:
                spares += c
    return spares

def is_vali_position():
    return spares(0) >= 0 and spares(1) >= 0 and position["checkers"][BAR_0_LOC] >= 0 and position["checkers"][BAR_1_LOC] <= 0

def draw_board(target):
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
    if position["turn"] == 0:
        start_slot_num = 24
        slot_delta = -1
    slot_y = y - FRAME / 2 - CHECKER_SIZE / 2
    for c in range(6):
        draw_triangle(target, int(x), int(y - CIRCLE_RADIUS), 1, ndx)
        draw_slot(target, x, y, position["checkers"][ndx], 1)
        display_text(x, slot_y, str(start_slot_num), (255, 255, 255), target)
        start_slot_num += slot_delta
        locations[ndx] = (x, y)
        x += CHECKER_SIZE
        ndx += 1

    x += CHECKER_SIZE + BORDER
    for c in range(6):
        draw_triangle(target, int(x), int(y - CIRCLE_RADIUS), 1, ndx)
        draw_slot(target, x, y, position["checkers"][ndx], 1)
        display_text(x, slot_y, str(start_slot_num), (255, 255, 255), target)
        start_slot_num += slot_delta
        locations[ndx] = (x, y)
        x += CHECKER_SIZE
        ndx += 1

    x -= CHECKER_SIZE
    y = WINDOW_SIZE[1] - FRAME - CHECKER_SIZE / 2
    slot_y = y + FRAME / 2 + CHECKER_SIZE / 2
    for c in range(6):
        draw_triangle(target, int(x), int(y + CIRCLE_RADIUS), -1, ndx)
        draw_slot(target, x, y, position["checkers"][ndx], -1)
        display_text(x, slot_y, str(start_slot_num), (255, 255, 255), target)
        start_slot_num += slot_delta
        locations[ndx] = (x, y)
        x -= CHECKER_SIZE
        ndx += 1

    x -= CHECKER_SIZE + BORDER
    for c in range(6):
        draw_triangle(target, int(x), int(y + CIRCLE_RADIUS), -1, ndx)
        draw_slot(target, x, y, position["checkers"][ndx], -1)
        display_text(x, slot_y, str(start_slot_num), (255, 255, 255), target)
        start_slot_num += slot_delta
        locations[ndx] = (x, y)
        x -= CHECKER_SIZE
        ndx += 1

    x = CHECKER_SIZE * 13 + BORDER * 3 + FRAME + 2
    y = FRAME + 2
    num_spares = spares(1)
    for c in range(num_spares):
        gfxdraw.box(target, (x, y, CHECKER_SIZE - 5, 6), C0_COLOR)
        gfxdraw.box(target, (x + 1, y + 1, CHECKER_SIZE - 7, 4), C1_COLOR)
        y += 8
        if c % 5 == 4:
            y += 3

    y = WINDOW_SIZE[1] - FRAME - 8
    num_spares = spares(0)
    for c in range(num_spares):
        gfxdraw.box(target, (x, y, CHECKER_SIZE - 5, 6), C0_COLOR)
        y -= 8
        if c % 5 == 4:
            y -= 3

    draw_bar(target)

    draw_dice(target)


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

# Game loop
running = True


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

    else:
        hold_position = list(position["checkers"])

        if event.button == 1:
            position["checkers"][ndx] += 1
        if event.button == 2:
            position["checkers"][ndx] = 0
        if event.button == 3:
            position["checkers"][ndx] -= 1

        if not is_vali_position():
            position["checkers"] = hold_position


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            handle_mouse_click(event)

    # Clear the screen
    screen.fill(BG_COLOR)

    # Draw the backgammon board
    draw_board(board_image)
    screen.blit(board_image, (0, 0))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Save the result as a black and white PNG file
pygame.image.save(board_image, "backgammon_position.png")

# Quit Pygame
pygame.quit()

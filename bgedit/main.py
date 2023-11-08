import pygame
import pygame.draw
import pygame.image
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Constants
BORDER = 5
CHECKER_SIZE = 40
TOTAL_WIDTH = 14 * CHECKER_SIZE
TOTAL_HEIGHT = 11 * CHECKER_SIZE
WINDOW_SIZE = (TOTAL_WIDTH + BORDER * 2, TOTAL_HEIGHT + BORDER * 2)
C0_COLOR = (39, 33, 19)
C1_COLOR = (220, 200, 190)
BG_COLOR = (143, 192, 143)
LINE_COLOR = (64, 64, 64)
CIRCLE_RADIUS = (CHECKER_SIZE - 2) // 2
T1_COLOR = (235, 119, 34)
T2_COLOR = (128, 128, 128)

# Initialize the window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Backgammon Position Editor")

# Create a blank image to represent the backgammon board
board_image = pygame.Surface(WINDOW_SIZE)
board_image.fill(BG_COLOR)

# Initialize a clock for controlling the frame rate
clock = pygame.time.Clock()

# Position data (you can customize this)
position = [2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5, -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2]
locations = {}


def draw_slot(target, x, y, cnt, delta):
    color = 0
    if cnt < 0:
        color = 1
        cnt = -cnt
    for c in range(cnt):
        gfxdraw.aacircle(target, int(x), int(y), CIRCLE_RADIUS, LINE_COLOR)
        gfxdraw.filled_circle(target, int(x), int(y), CIRCLE_RADIUS, C0_COLOR)
        if color == 1:
            gfxdraw.aacircle(target, int(x), int(y), CIRCLE_RADIUS - 2, C1_COLOR)
            gfxdraw.filled_circle(target, int(x), int(y), CIRCLE_RADIUS - 2, C1_COLOR)

        y += delta * CHECKER_SIZE


def draw_triangle(target, x, y, delta, ndx):
    color = T1_COLOR if ndx % 2 == 0 else T2_COLOR
    gfxdraw.aatrigon(target, x - CIRCLE_RADIUS, y, x + CIRCLE_RADIUS, y, x, y + delta * CHECKER_SIZE * 5, color)
    gfxdraw.filled_trigon(target, x - CIRCLE_RADIUS, y, x + CIRCLE_RADIUS, y, x, y + delta * CHECKER_SIZE * 5, color)


def spares(side):
    spares = 15
    if side == 0:
        for c in position:
            if c > 0:
                spares -= c
    else:
        for c in position:
            if c < 0:
                spares += c
    return spares


def draw_board(target):
    x = CHECKER_SIZE / 2 + BORDER
    y = CHECKER_SIZE / 2 + BORDER

    target.fill(BG_COLOR)
    gfxdraw.box(target, (0, 0, TOTAL_WIDTH + BORDER, BORDER), LINE_COLOR)
    gfxdraw.box(target, (0, TOTAL_HEIGHT + BORDER, TOTAL_WIDTH + BORDER, BORDER), LINE_COLOR)
    gfxdraw.box(target, (0, 0, BORDER, TOTAL_HEIGHT + BORDER), LINE_COLOR)
    gfxdraw.box(target, (TOTAL_WIDTH + BORDER, 0, BORDER, TOTAL_HEIGHT + BORDER * 2), LINE_COLOR)
    gfxdraw.box(target, (CHECKER_SIZE * 6 + BORDER, 0, BORDER, TOTAL_HEIGHT + BORDER), LINE_COLOR)
    gfxdraw.box(target, (CHECKER_SIZE * 7, 0, BORDER, TOTAL_HEIGHT + BORDER), LINE_COLOR)
    gfxdraw.box(target, (CHECKER_SIZE * 13 + BORDER, 0, BORDER, TOTAL_HEIGHT + BORDER), LINE_COLOR)

    ndx = 0
    for c in range(6):
        draw_triangle(target, int(x), int(y - CIRCLE_RADIUS), 1, ndx)
        draw_slot(target, x, y, position[ndx], 1)
        locations[ndx] = (x, y)
        x += CHECKER_SIZE
        ndx += 1

    x += CHECKER_SIZE
    for c in range(6):
        draw_triangle(target, int(x), int(y - CIRCLE_RADIUS), 1, ndx)
        draw_slot(target, x, y, position[ndx], 1)
        locations[ndx] = (x, y)
        x += CHECKER_SIZE
        ndx += 1

    x -= CHECKER_SIZE
    y = TOTAL_HEIGHT - CHECKER_SIZE / 2 + BORDER
    for c in range(6):
        draw_triangle(target, int(x), int(y + CIRCLE_RADIUS), -1, ndx)
        draw_slot(target, x, y, position[ndx], -1)
        locations[ndx] = (x, y)
        x -= CHECKER_SIZE
        ndx += 1

    x -= CHECKER_SIZE
    for c in range(6):
        draw_triangle(target, int(x), int(y + CIRCLE_RADIUS), -1, ndx)
        draw_slot(target, x, y, position[ndx], -1)
        locations[ndx] = (x, y)
        x -= CHECKER_SIZE
        ndx += 1

    x = CHECKER_SIZE * 13 + BORDER * 2 + 2
    y = BORDER + 2
    num_spares = spares(1)
    for c in range(num_spares):
        gfxdraw.box(target, (x, y, CHECKER_SIZE - 9, 6), C0_COLOR)
        gfxdraw.box(target, (x + 1, y + 1, CHECKER_SIZE - 11, 4), C1_COLOR)
        y += 8
        if c % 5 == 4:
            y += 3

    x = CHECKER_SIZE * 13 + BORDER * 2 + 2
    y = TOTAL_HEIGHT - BORDER + 2
    num_spares = spares(0)
    for c in range(num_spares):
        gfxdraw.box(target, (x, y, CHECKER_SIZE - 9, 6), C0_COLOR)
        y -= 8
        if c % 5 == 4:
            y -= 3


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
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            ndx = get_ndx_for_click(event.pos[0], event.pos[1])
            hold_position = list(position)
            if event.button == 1:
                position[ndx] += 1
            if event.button == 2:
                position[ndx] = 0
            if event.button == 3:
                position[ndx] -= 1
            if spares(0) < 0 or spares(1) < 0:
                position = hold_position

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

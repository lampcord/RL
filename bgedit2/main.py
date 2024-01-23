import os
import sys

import pygame
import pygame.draw
import pygame.image
import copy
import json
from pygame import gfxdraw
from bg_board import *

# Initialize Pygame

# Constants

POSITIONS_FILE_NAME = 'positions.json'




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
    update_theme(theme_file_name)

# Initialize the window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Backgammon Position Editor")

# Create a blank image to represent the backgammon board
board_image = pygame.Surface(WINDOW_SIZE)
board_image.fill(BG_COLOR)

# Initialize a clock for controlling the frame rate
clock = pygame.time.Clock()


'''
0   4
1 3 5
2   6
'''

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

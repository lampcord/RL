# import the pygame module
import random
import time
import pygame

# Define the background colour
# using RGB color coding.
padding = 5
hinge_width = 20
target_checker_size = 60
checker_thickness = 20
target_background_width = target_checker_size * 6
target_background_height = (5 * target_checker_size) / .4
border_size = 20
message_size = 30

background_colour = (255, 255, 255)
edge_color = (64, 64, 64)
surface_color = (28, 24, 75)
triangle_color = ((255, 255, 255), (216, 151, 0))
checker_color = ((128, 0, 0), (28, 24, 75))
border_color = (192, 192, 192)

dimensions = (2 * padding + 4 * border_size + 2 * target_background_width + hinge_width + border_size + target_checker_size, 2 * padding + 2 * border_size + target_background_height + message_size)
screen = pygame.display.set_mode(dimensions)

# Set the caption of the screen
pygame.display.set_caption('Pip Count Trainer')


def get_slot_count(board_string, slot):
    player = ''
    count = 0

    if slot >= 0 and slot < 24:
        cell = board_string[slot * 3: slot * 3 + 3]
        player = cell[0]
        count = int(cell[1:])

    return (player, count)


def get_bar_count(board_string):
    player1_count = int(board_string[24 * 3: 25 * 3])
    player2_count = int(board_string[25 * 3: 26 * 3])
    return player1_count, player2_count


def draw_triangle_set(_screen, starting_x, starting_y, up, width, height, color_ndx):
    offset = -height if up else height

    for _ in range(6):
        pygame.draw.polygon(_screen, triangle_color[color_ndx], ((starting_x, starting_y), (starting_x + width / 2, starting_y + offset), (starting_x + width, starting_y)))
        starting_x += width
        color_ndx = 1 - color_ndx


def paint_background(_screen):
    surface_width = target_background_width
    surface_height = target_background_height
    surface_1_origin_x = padding + border_size
    surface_origin_y = padding + border_size
    surface_2_origin_x = padding + border_size * 3 + hinge_width + target_background_width
    triangle_height = surface_height * 0.4
    triangle_width = target_checker_size

    pygame.draw.rect(_screen, edge_color, (padding, padding, dimensions[0] - padding * 2, dimensions[1] - padding * 2 - message_size))
    pygame.draw.rect(_screen, surface_color, (surface_1_origin_x, surface_origin_y, surface_width, surface_height))
    pygame.draw.rect(_screen, surface_color, (surface_2_origin_x, surface_origin_y, surface_width, surface_height))
    pygame.draw.rect(_screen, (0, 0, 0), (surface_2_origin_x + surface_width + border_size, surface_origin_y, target_checker_size, checker_thickness * 15))
    pygame.draw.rect(_screen, (0, 0, 0), (surface_2_origin_x + surface_width + border_size, surface_origin_y + surface_height - checker_thickness * 15, target_checker_size, checker_thickness * 15))

    draw_triangle_set(_screen, surface_1_origin_x, padding + border_size, False, triangle_width, triangle_height, 0)
    draw_triangle_set(_screen, surface_2_origin_x, padding + border_size, False, triangle_width, triangle_height, 0)
    draw_triangle_set(_screen, surface_1_origin_x, padding + border_size + surface_height, True, triangle_width, triangle_height, 1)
    draw_triangle_set(_screen, surface_2_origin_x, padding + border_size + surface_height, True, triangle_width, triangle_height, 1)

    return surface_width, surface_height, surface_1_origin_x, surface_2_origin_x, surface_origin_y, triangle_width


def paint_checkers(_screen, player, count, first_x, first_y, size, up):
    offset = -size if up else size
    orig_first_y = first_y

    for num in range(count):
        pygame.draw.circle(_screen, border_color, (first_x + size / 2, first_y + offset / 2), size / 2 - 1)
        pygame.draw.circle(_screen, checker_color[player], (first_x + size / 2, first_y + offset / 2), size / 2 - 3)
        first_y += offset
        if num == 5:
            first_y = orig_first_y + offset / 2
        if num == 10:
            first_y = orig_first_y + offset


def paint_cast_off_checkers(_screen, player, count, first_x, first_y, up):
    offset = -checker_thickness if up else checker_thickness

    for _ in range(count):
        pygame.draw.rect(_screen, border_color, (first_x, first_y, target_checker_size, checker_thickness - 1))
        pygame.draw.rect(_screen, checker_color[player], (first_x + 2, first_y + 2, target_checker_size - 4, checker_thickness - 5))
        first_y += offset

def paint_board(_screen, board_string):
    _screen.fill(background_colour)

    surface_width, surface_height, surface_1_origin, surface_2_origin, surface_origin_y, triangle_width = paint_background(_screen)
    castoffs = [15, 15]
    for slot in range(24):
        player, count = get_slot_count(board_string, slot)
        # player = 0
        # count = slot % 6 + 1
        # count = 15
        if count == 0: continue

        player_ndx = 0 if player == 'W' else 1
        castoffs[player_ndx] -= count
        quadrant = slot // 6
        # print (quadrant)
        y_origin = surface_origin_y + surface_height
        up = True
        x_origin = surface_2_origin + 5 * triangle_width - (slot % 6) * triangle_width

        if quadrant == 1:
            y_origin = surface_origin_y + surface_height
            up = True
            x_origin = surface_1_origin + 5 * triangle_width - (slot % 6) * triangle_width
        elif quadrant == 2:
            y_origin = surface_origin_y
            up = False
            x_origin = surface_1_origin + (slot % 6) * triangle_width
        elif quadrant == 3:
            y_origin = surface_origin_y
            up = False
            x_origin = surface_2_origin + (slot % 6) * triangle_width

        paint_checkers(_screen, player_ndx, count, x_origin, y_origin, triangle_width, up)
        # print(f"{slot:3} {player} {count}")

    # checkers on the bar
    player_1_bar, player_2_bar = get_bar_count(board_string)
    paint_checkers(_screen, 0, player_1_bar, surface_1_origin + target_background_width + border_size + hinge_width / 2 - triangle_width / 2, surface_origin_y + surface_height - triangle_width / 4, triangle_width, True)
    paint_checkers(_screen, 1, player_2_bar, surface_1_origin + target_background_width + border_size + hinge_width / 2 - triangle_width / 2, surface_origin_y + triangle_width / 4, triangle_width, False)

    # castoffs
    paint_cast_off_checkers(_screen, 0, castoffs[0], surface_2_origin + surface_width + border_size, surface_origin_y, False)
    paint_cast_off_checkers(_screen, 1, castoffs[1], surface_2_origin + surface_width + border_size, surface_origin_y + surface_height - checker_thickness, True)

# Variable to keep our game loop running
running = True
test_strings = open('positions.txt', 'r').read().split('\n')



def get_pip_count(board_string):
    counts = [0, 0]
    for slot in range(24):
        player, count = get_slot_count(board_string, slot)
        player_ndx = 0 if player == 'W' else 1
        value = (slot + 1) * count if player_ndx == 1 else (24 - slot) * count
        counts[player_ndx] += value
    bar = get_bar_count(board_string)
    counts[0] += 25 * bar[0]
    counts[1] += 25 * bar[1]

    return counts

keys = {}
keys[pygame.K_0] = '0'
keys[pygame.K_1] = '1'
keys[pygame.K_2] = '2'
keys[pygame.K_3] = '3'
keys[pygame.K_4] = '4'
keys[pygame.K_5] = '5'
keys[pygame.K_6] = '6'
keys[pygame.K_7] = '7'
keys[pygame.K_8] = '8'
keys[pygame.K_9] = '9'
keys[pygame.K_KP0] = '0'
keys[pygame.K_KP1] = '1'
keys[pygame.K_KP2] = '2'
keys[pygame.K_KP3] = '3'
keys[pygame.K_KP4] = '4'
keys[pygame.K_KP5] = '5'
keys[pygame.K_KP6] = '6'
keys[pygame.K_KP7] = '7'
keys[pygame.K_KP8] = '8'
keys[pygame.K_KP9] = '9'
keys[pygame.K_SPACE] = ' '
# game loop
test_ndx = random.randint(0, len(test_strings) - 1)
pygame.font.init() # you have to call this at the start,
                   # if you want to use this module.
my_font = pygame.font.SysFont('Arial.ttf', 30)
mode = 'COUNTING'
error = ''
count_string = ''
while running:
    if test_ndx >= len(test_strings):
        break

    test_string = test_strings[test_ndx]
    pip_counts = get_pip_count(test_string)
    # print(pip_counts[0], pip_counts[1])
    paint_board(screen, test_string)

    message = ''
    background_colour = (255, 255, 255)
    font_color = (0, 0, 0)

    if mode == 'COUNTING':
        message = 'Count Pips Then Hit Space Bar When Ready'
    elif mode == 'ENTERING':
        background_colour = (0, 255, 0)
        message = 'Enter Counts Separated by Space then hit ENTER ' + count_string

    if len(error) > 0:
        background_colour = (255, 0, 0)
        font_color = (255, 255, 255)
        message = error

    text_surface = my_font.render(message, False, font_color)

    screen.blit(text_surface, (dimensions[0] / 2 - text_surface.get_size()[0] / 2, dimensions[1] - message_size / 2 - text_surface.get_size()[1] / 2))
    pygame.display.flip()

    # for loop through the event queue
    for event in pygame.event.get():

        # Check for QUIT event
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                print(test_string)

            if event.key == pygame.K_x:
                mode = 'COUNTING'
                error = ''
                count_string = ''
                test_ndx = random.randint(0, len(test_strings) - 1)
                continue

            if event.key == pygame.K_ESCAPE:
                running = False
                break
            if len(error) > 0:
                if event.key == pygame.K_SPACE:
                    error = ''
                    count_string = ''
            elif mode == 'COUNTING':
                if event.key == pygame.K_SPACE:
                    mode = 'ENTERING'
                    count_string = ''
            elif mode == 'ENTERING':
                print(event.key, pygame.K_KP_0)
                if event.key == pygame.K_RETURN:
                    counts = count_string.split(' ')
                    if len(counts) < 2:
                        error = 'Invalid entry'
                    else:
                        guess1 = int(counts[0])
                        guess0 = int(counts[1])
                        if guess0 != pip_counts[0] or guess1 != pip_counts[1]:
                            error = f'WRONG! Guessed: ({count_string}) actual ({pip_counts[1]} {pip_counts[0]})'

                        mode = 'COUNTING'
                        test_ndx = random.randint(0, len(test_strings) - 1)
                elif event.key in keys:
                    count_string += keys[event.key]


    time.sleep(.03) # ~30 FPS





# import the pygame module
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

background_colour = (255, 255, 255)
edge_color = (64, 64, 64)
surface_color = (28, 24, 75)
triangle_color = ((255, 255, 255), (216, 151, 0))
checker_color = ((128, 0, 0), (28, 24, 75))
border_color = (192, 192, 192)

dimensions = (2 * padding + 4 * border_size + 2 * target_background_width + hinge_width + border_size + target_checker_size, 2 * padding + 2 * border_size + target_background_height)
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

    pygame.draw.rect(_screen, edge_color, (padding, padding, dimensions[0] - padding * 2, dimensions[1] - padding * 2))
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
    pygame.display.flip()

# Variable to keep our game loop running
running = True
test_strings = [
    "W02  0  0  0  0B05  0B03  0  0  0W05B05  0  0  0W03  0W05  0  0  0  0B02  0  0",
    "W01W01  0  0  0B05  0B03  0  0  0W04B05  0  0W01W03  0W05  0  0  0  0B02  0  0",
    "W01W01  0  0  0B05  0B04  0  0  0W04B04  0  0W01W03  0W05B01  0  0  0B01  0  0",
    "  0  0  0  0  0B05W02B04  0  0  0W04B04  0  0W01W03  0W05B01  0  0  0B01  0  0",
    "  0  0  0  0B01B04W02B04  0  0  0W04B04B01  0W01W03  0W05  0  0  0  0B01  0  0",
    "  0  0  0  0B01B04  0B04  0  0  0W06B04B01  0W01W03  0W03  0  0  0  0W02  0  1",
    "  0  0  0  0B01B04  0B05  0  0  0W06B04  0  0W01W03  0W03  0B01  0  0W02  0  0",
    "  0  0  0  0B01B04  0B05  0  0  0W05B04  0  0  0W04  0W04  0B01  0  0W02  0  0",
    "  0  0  0  0B02B04  0B05  0  0  0W05B03  0  0  0W04  0W04  0B01  0  0W02  0  0",
    "  0  0  0  0B02B04  0B05  0  0  0W04B03  0  0  0W05  0W03  0B01  0W01W02  0  0",
    "  0  0  0  0B02B04B02B04  0  0  0W04B02  0  0  0W05  0W03  0B01  0W01W02  0  0",
    "  0  0  0  0B02B04B02B04  0  0  0W03B02  0  0  0W04W02W03  0B01  0W01W02  0  0",
    "  0  0  0B02B02B04B02B02  0  0  0W03B02  0  0  0W04W02W03  0B01  0W01W02  0  0",
    "  0  0  0B02B02B04B02B02  0  0  0  0B02  0  0  0W06W02W03  0B01W01W01W02  0  0",
    "  0  0B01B02B02B04B02B01  0B01  0  0B01  0  0  0W06W02W03  0B01W01W01W02  0  0",
    "  0  0B01B02B02B04B02B01  0B01  0  0B01  0  0  0W05W02W03  0B01W01W01W03  0  0",
    "  0B01B01B02B03B03B01B01  0B01B01  0  0  0  0  0W05W02W03  0B01W01W01W03  0  0",
    "  0B01B01B02B03B03B01B01  0B01B01  0  0  0  0  0W04W02W03  0B01W02W01W03  0  0",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0W04W02W03  0B01W02W01W03  0  0",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0W03  0W03  0W02W02W02W03  0  1",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0W03  0W03  0W02W02W02W03  0  1",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0W01  0W04  0W02W03W02W03  0  1",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0W01  0W04  0W02W03W02W03  0  1",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0  0  0W04  0W02W03W03W03  0  1",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0  0  0W04  0W02W03W03W03  0  1",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0  0  0W04  0W02W03W02W02  0  1",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0  0  0W04  0W02W03W02W02  0  1",
    "  0B01B02B04B03B02  0B01  0  0B01  0  0  0  0  0  0  0W02  0W03W03W02W03  0  1",
    "  0B01B02B04B03B02B01B01  0  0  0  0  0  0  0  0  0  0W02B01W03W03W02W03  0  0",
    "  0B01B02B04B03B02B01B01  0  0  0  0  0  0  0  0  0  0W02B01W03W02W02W02  0  0",
    "  0B01B03B04B03B03  0  0  0  0  0  0  0  0  0  0  0  0W02B01W03W02W02W02  0  0",
    "  0B01B03B04B03B03  0  0  0  0  0  0  0  0  0  0  0  0W02B01W03W01W02W01  0  0",
    "B01B02B03B03B03B02  0  0  0  0  0  0  0  0  0  0  0  0W02B01W03W01W02W01  0  0",
    "B01B02B03B03B03B02  0  0  0  0  0  0  0  0  0  0  0  0W02B01W02W01W02  0  0  0",
    "B01B02B03B03B03B02  0  0  0  0  0  0B01  0  0  0  0  0W02  0W02W01W02  0  0  0",
    "B01B02B03B03B03B02  0  0  0  0  0  0B01  0  0  0  0  0W02  0W01W01W01  0  0  0",
    "B01B02B03B03B04B02  0  0  0  0  0  0  0  0  0  0  0  0W02  0W01W01W01  0  0  0",
    "B01B02B03B03B04B02  0  0  0  0  0  0  0  0  0  0  0  0W01W01W01  0W01  0  0  0",
    "B01B01B02B03B04B02  0  0  0  0  0  0  0  0  0  0  0  0W01W01W01  0W01  0  0  0",
    "B01B01B02B03B04B02  0  0  0  0  0  0  0  0  0  0  0  0W01  0  0  0W02  0  0  0",
    "B01  0B01B03B04B02  0  0  0  0  0  0  0  0  0  0  0  0W01  0  0  0W02  0  0  0",
    "B01  0B01B03B04B02  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0W02W01  0  0",
    "B01  0  0B03B04B01  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0W02W01  0  0",
    "B01  0  0B03B04B01  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0W01  0  0  0",
    "B01B01  0B02B03B01  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0W01  0  0  0",
    "B01B01  0B02B03B01  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0",
    "B01B01  0B02B03B01  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0"
]


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


# game loop
test_ndx = 0
while running:
    if test_ndx >= len(test_strings):
        break

    test_string = test_strings[test_ndx]
    counts = get_pip_count(test_string)
    print(counts[0], counts[1])
    paint_board(screen, test_string)

    # for loop through the event queue
    for event in pygame.event.get():

        # Check for QUIT event
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                test_ndx += 1

    time.sleep(.03) # ~30 FPS





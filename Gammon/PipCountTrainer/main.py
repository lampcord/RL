# import the pygame module
import time
import pygame

# Define the background colour
# using RGB color coding.
target_checker_size = 60
target_background_width = target_checker_size * 6
target_background_height = (5 * target_checker_size) / .4
padding = 5
border_size = 10
background_colour = (255, 255, 255)
edge_color = (64, 64, 64)
surface_color = (28, 24, 75)
triangle_color = ((255, 255, 255), (216, 151, 0))
checker_color = ((128, 0, 0), (0, 0, 128))
border_color = (192, 192, 192)

dimensions = (2 * padding + 4 * border_size + 2 * target_background_width, 2 * padding + 2 * border_size + target_background_height)
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

def draw_triangle_set(_screen, starting_x, starting_y, up, width, height, color_ndx):
    offset = -height if up else height

    for _ in range(6):
        pygame.draw.polygon(_screen, triangle_color[color_ndx], ((starting_x, starting_y), (starting_x + width / 2, starting_y + offset), (starting_x + width, starting_y)))
        starting_x += width
        color_ndx = 1 - color_ndx


def paint_background(_screen):
    surface_width = (dimensions[0] - border_size  * 4 - padding * 2) / 2
    surface_height = dimensions[1] - (border_size + padding) * 2
    surface_1_origin_x = padding + border_size
    surface_origin_y = padding + border_size
    surface_2_origin_x = padding + border_size + dimensions[0] / 2 - padding
    triangle_height = surface_height * 0.4
    triangle_width = surface_width / 6

    pygame.draw.rect(_screen, edge_color, (padding, padding, dimensions[0] - padding * 2, dimensions[1] - padding * 2))
    pygame.draw.rect(_screen, surface_color, (surface_1_origin_x, surface_origin_y, surface_width, surface_height))
    pygame.draw.rect(_screen, surface_color, (surface_2_origin_x, surface_origin_y, surface_width, surface_height))

    draw_triangle_set(_screen, surface_1_origin_x, padding + border_size, False, triangle_width, triangle_height, 0)
    draw_triangle_set(_screen, surface_2_origin_x, padding + border_size, False, triangle_width, triangle_height, 0)
    draw_triangle_set(_screen, surface_1_origin_x, padding + border_size + surface_height, True, triangle_width, triangle_height, 1)
    draw_triangle_set(_screen, surface_2_origin_x, padding + border_size + surface_height, True, triangle_width, triangle_height, 1)

    return surface_width, surface_height, surface_1_origin_x, surface_2_origin_x, surface_origin_y, triangle_width


def paint_checkers(_screen, player, count, first_x, first_y, size, up):
    offset = -size if up else size

    for _ in range(count):
        pygame.draw.circle(_screen, border_color, (first_x + size / 2, first_y + offset / 2), size / 2 - 1)
        pygame.draw.circle(_screen, checker_color[player], (first_x + size / 2, first_y + offset / 2), size / 2 - 3)
        first_y += offset

def paint_board(_screen, board_string):
    _screen.fill(background_colour)

    surface_width, surface_height, surface_1_origin, surface_2_origin, surface_origin_y, triangle_width = paint_background(_screen)
    for slot in range(24):
        player, count = get_slot_count(board_string, slot)
        # player = 0
        # count = slot % 6 + 1
        if count == 0: continue

        player_ndx = 0 if player == 'W' else 1

        quadrant = slot // 6
        print (quadrant)
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

    pygame.display.flip()

# Variable to keep our game loop running
running = True
test_string = "W02  0  0  0  0B05  0B03  0  0  0W05B05  0  0  0W03  0W05  0  0  0  0B02  0  0"





# game loop
while running:

    paint_board(screen, test_string)

    # for loop through the event queue
    for event in pygame.event.get():

        # Check for QUIT event
        if event.type == pygame.QUIT:
            running = False

    time.sleep(.03) # ~30 FPS





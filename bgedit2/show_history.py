import os
import sys

import pygame
import pygame.draw
import pygame.image
import copy
import random
import json

import pyperclip

from quiz_controller import QuizController
import bg_board
from XGID_to_position import *

WINDOW_SIZE = (800, 800)
EXTENDED_WINDOW_SIZE = (1500, 800)
BG_COLOR = (192, 192, 192)
COLUMNS = 3
COLUMN_WIDTH = WINDOW_SIZE[0] // (COLUMNS + 1)
CAT_COLS = (800, 1000)

bg_board.update_theme('greyscale.json')

columns = []
next_column = COLUMN_WIDTH
for x in range(COLUMNS):
    columns.append(next_column)
    next_column += COLUMN_WIDTH

quiz_name = 'test'
if len(sys.argv) > 1:
    quiz_name = sys.argv[1]

directory = './quiz/' + quiz_name + '/'
print(directory)
try:
    quiz_filename = directory + 'quiz.json'
    # Attempt to open and read the JSON file
    with open(quiz_filename, 'r') as json_file:
        quiz = json.load(json_file)
except Exception as e:
    print(f'ERROR: Problem loading quiz {str(e)}')
    sys.exit(1)


category_map = {
    '0': ['Opening', 'First 4 moves'],
    '1': ['Middlegame', 'Both players have men back and developing.'],
    '2': ['Blitz - O', 'Attacking and building points. Defender has blots or on bar.'],
    '3': ['Blitz - D', 'Attacking and building points. Defender has blots or on bar.'],
    '4': ['Long Race', 'Bearing in no contact.'],
    '5': ['Bearoff Race', 'Bearing off no contact.'],
    '6': ['Bearoff W/Cont - O', 'Bearing off with oponents back.'],
    '7': ['Bearoff W/Cont - D', 'Bearing off with oponents back.'],
    '8': ['Roll vs Roll', 'Late bearoff where you are counting rolls not pips.'],
    '9': ['Mutual Holding', 'Both players have high anchor and are trying to hold and run'],
    'A': ['One Way Holding - O', 'High anchor (6, 7, 9) vs. no one back.'],
    'B': ['One Way Holding - D', 'High anchor (6, 7, 9) vs. no one back.'],
    'C': ['Deep Anchor - O', 'Low anchor (1, 2) vs. no one back.'],
    'D': ['Deep Anchor - D', 'Low anchor (1, 2) vs. no one back.'],
    'E': ['3 Pt. Anchor - O', '3 point anchor vs. no one back.'],
    'F': ['3 Pt. Anchor - D', '3 point anchor vs. no one back.'],
    'G': ['No Anchor H - O', 'Holding game with no anchor but multiple blots.'],
    'H': ['No Anchor H - D', 'Holding game with no anchor but multiple blots.'],
    'I': ['One Man Back - O', 'Holding game with no anchor but one blot.'],
    'J': ['One Man Back - D', 'Holding game with no anchor but one blot.'],
    'K': ['6 Prime - O', 'One side has a 6 prime.'],
    'L': ['6 Prime - D', 'One side has a 6 prime.'],
    'M': ['Late Game Cont - O', 'Holding game at end.'],
    'N': ['Late Game Cont - D', 'Holding game at end.'],
    'O': ['Early Bk Game - O', 'Back game where both sides have men back'],
    'P': ['Early Bk Game - D', 'Back game where both sides have men back'],
    'Q': ['Mid Bk Game - O', 'Back game where offense has escaped.'],
    'R': ['Mid Bk Game - D', 'Back game where offense has escaped.'],
    'S': ['Late Bk Game - O', 'Bearing off / in'],
    'T': ['Late Bk Game - D', 'Bearing off / in'],
    'U': ['Containment - O', 'Post hit contain'],
    'V': ['Containment - D', 'Post hit contain'],
    'W': ['Stack Straggle - O', 'Bear off vs Straggler'],
    'X': ['Stack Straggle - D', 'Bear off vs Straggler'],
    'Y': ['Prime v Prime', 'Both priming with trapped checkers.'],
    'Z': ['Blitz v Prime - B', 'One side blitzing other sid priming.'],
    ',': ['Blitz v Prime - P', 'One side blitzing other sid priming.'],
    '.': ['Crunch', 'Both sides have men back trying not to crunch'],
    '/': ['Hypergammon', 'Both players trying to get 3 or less around and past each other.']
}

key = 'A'
key_mappings = {}
for k in range(pygame.K_a, pygame.K_z + 1):
    key = chr(ord('A') + k - pygame.K_a)
    key_mappings[k] = key

for k in range(pygame.K_0, pygame.K_9 + 1):
    key = chr(ord('0') + k - pygame.K_0)
    key_mappings[k] = key

key_mappings[pygame.K_COMMA] = ','
key_mappings[pygame.K_PERIOD] = '.'
key_mappings[pygame.K_SLASH] = '/'

print(category_map)
decay = 0.90
new_mult = 2.0

qc = QuizController(directory + 'qc.json', len(quiz), decay, new_mult)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(EXTENDED_WINDOW_SIZE)
pygame.display.set_caption("Backgammon History")
font = pygame.font.Font(None, 24)

running = True


def load_flashcard(quiz_line):
    if '.png' in quiz_line['flashcard']:
        image_path = directory + 'flashcards/' + quiz_line['flashcard']
        return pygame.image.load(image_path)
    else:
        board_image = pygame.Surface(bg_board.WINDOW_SIZE)
        board_image.fill(BG_COLOR)
        position = get_position(quiz_line['flashcard'])
        # print(position)
        bg_board.draw_board(position, board_image)
        return board_image



def display_text(x, y, text, color, target, center_x=True, center_y=True):
    text_surface = font.render(text, True, color)  # Text, antialiasing, color
    if center_x:
        x -= text_surface.get_width() // 2
    if center_y:
        y -= text_surface.get_height() // 2
    target.blit(text_surface, (x, y))  # Position of the text

def get_text_size(text):
    text_surface = font.render(text, True, (0, 0, 0,))  # Text, antialiasing, color
    return text_surface.get_size()

key = ''

line_spacing = 20
score_history = {}
for k in qc.history.keys():
    hist = qc.history[k]
    print(k, hist)
    total_score = 0.0
    total_choices = 0.0
    for choice, score in hist:
        total_score += score
        total_choices += 1.0
    print(total_score / total_choices)
    score_history[k] = total_score / total_choices

sorted_dict = {k: v for k, v in sorted(score_history.items(), key=lambda item: item[1])}
for k in sorted_dict.keys():
    print(k, sorted_dict[k])
hist_keys = [k for k in sorted_dict.keys()]
print(hist_keys)
current_key = 0

quiz_line_index = int(hist_keys[current_key])
quiz_line = quiz[quiz_line_index]
current_categories = qc.categories.get(str(quiz_line_index), [])
image = load_flashcard(quiz_line)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pyperclip.copy("XGID=" + quiz_line['flashcard'])
            if event.key == pygame.K_ESCAPE:
                running = False
                break
            elif event.key == pygame.K_TAB:
                current_key += 1
                if current_key >= len(hist_keys):
                    running = False
                    break
                quiz_line_index = int(hist_keys[current_key])
                quiz_line = quiz[quiz_line_index]
                image = load_flashcard(quiz_line)
                current_categories = qc.categories.get(str(quiz_line_index), [])
            elif event.key in key_mappings.keys():
                key = key_mappings[event.key]
                print(key)
                if key in category_map.keys():
                    if key in current_categories:
                        current_categories.remove(key)
                    else:
                        current_categories.append(key)
                    qc.categories[str(quiz_line_index)] = current_categories


    # Clear the screen
    screen.fill(BG_COLOR)
    left = (WINDOW_SIZE[0] - image.get_size()[0]) // 2
    screen.blit(image, (left, 0))  # Drawing the image at position (0, 0)
    bottom = image.get_size()[1]
    center = WINDOW_SIZE[0] / 2
    text_line = bottom + line_spacing
    display_text(center, text_line, f'[{quiz_line_index}] ' + quiz_line['flashcard'] + ' (SPACE to copy)', (0, 0, 0), screen)
    text_line += line_spacing

    hist = qc.history[str(quiz_line_index)]
    counts = {}
    for c, s in hist:
        counts[c] = counts.get(c, 0) + 1

    text_line += line_spacing
    for x in range(len(quiz_line['answers'])):
        color = (0, 0, 0)
        c = counts.get(x, 0)
        if c > 0:
            if x == 0:
                color = (0, 128, 0)
            else:
                color = (255, 0 ,0)
        display_text(columns[0], text_line, f'{quiz_line["answers"][x][0]}', color, screen, center_x=False)
        display_text(columns[1], text_line, f'{counts.get(x, 0)}', color, screen, center_x=False)
        display_text(columns[2], text_line, f'{float(quiz_line["answers"][x][1]):8.3f}', color, screen, center_x=False)
        text_line += line_spacing

    text_line += line_spacing
    display_text(center, text_line, 'Press X to continue or Q to quit', (0, 0, 0), screen)

    text_line += line_spacing

    text_line = line_spacing
    for k in category_map.keys():
        color = (0, 0, 0)
        if k in current_categories:
            color = (0, 128, 0)

        display_text(CAT_COLS[0], text_line, f'{k}) {category_map[k][0]}', color, screen, center_x=False)
        display_text(CAT_COLS[1], text_line, f'{category_map[k][1]}', color, screen, center_x=False)
        text_line += line_spacing



    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

qc.save()
pygame.quit()
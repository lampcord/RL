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
BG_COLOR = (192, 192, 192)
COLUMNS = 3
COLUMN_WIDTH = WINDOW_SIZE[0] // (COLUMNS + 1)

bg_board.update_theme('greyscale.json')

columns = []
next_column = COLUMN_WIDTH
for x in range(COLUMNS):
    columns.append(next_column)
    next_column += COLUMN_WIDTH

if len(sys.argv) > 1:
    directory = './quiz/' + sys.argv[1] + '/'
    print(directory)
    try:
        quiz_filename = directory + 'quiz.json'
        # Attempt to open and read the JSON file
        with open(quiz_filename, 'r') as json_file:
            quiz = json.load(json_file)
    except Exception as e:
        print(f'ERROR: Problem loading quiz {str(e)}')
        sys.exit(1)

else:
    print('USAGE: quiz <directory> <opt: decay> <opt: new mult>')
    sys.exit(1)

decay = 0.95 if len(sys.argv) <= 2 else float(sys.argv[2])
new_mult = 2.0 if len(sys.argv) <= 3 else float(sys.argv[3])

print(f'{directory} {decay} {new_mult}')

qc = QuizController(directory + 'qc.json', len(quiz), decay, new_mult)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Backgammon Position Editor")
font = pygame.font.Font(None, 24)

running = True


def choose_quiz_line():
    return qc.get_question_index()


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


def get_choices(quiz_line):
    choices = {}
    answers = list(range(len(quiz_line['answers'])))
    first_letter = ord('A')
    random.shuffle(answers)
    for answer in answers:
        choices[chr(first_letter)] = answer
        first_letter += 1
    return choices


def display_text(x, y, text, color, target, center_x=True, center_y=True):
    text_surface = font.render(text, True, color)  # Text, antialiasing, color
    if center_x:
        x -= text_surface.get_width() // 2
    if center_y:
        y -= text_surface.get_height() // 2
    target.blit(text_surface, (x, y))  # Position of the text


quiz_line_index = choose_quiz_line()
quiz_line = quiz[quiz_line_index]
choices = get_choices(quiz_line)
image = load_flashcard(quiz_line)
key = ''

line_spacing = 20

stage = 0
session = {}
user_choice = None
num_questions = 1
done_reviewing = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pyperclip.copy("XGID=" + quiz_line['flashcard'])
            if pygame.K_a <= event.key <= pygame.K_z:
                key = chr(ord('A') + event.key - pygame.K_a)
                # print(key)

                if stage == 0:
                    if key in choices:
                        answer = quiz_line['answers'][choices[key]]
                        qc.post_result(quiz_line_index, choices[key], float(answer[1]))
                        qc.dump()
                        quiz_line_index = choose_quiz_line()
                        quiz_line = quiz[quiz_line_index]
                        choices = get_choices(quiz_line)
                        # print(choices)
                        image = load_flashcard(quiz_line)
                        num_questions += 1
                elif stage == 1:
                    if len(session) > 0:
                        quiz_line_index = list(session.keys())[0]
                        user_choice = session.pop(quiz_line_index)
                        quiz_line = quiz[int(quiz_line_index)]
                        choices = get_choices(quiz_line)
                        # print(choices)
                        image = load_flashcard(quiz_line)
                    else:
                        done_reviewing = True


    # Clear the screen
    screen.fill(BG_COLOR)
    left = (WINDOW_SIZE[0] - image.get_size()[0]) // 2
    screen.blit(image, (left, 0))  # Drawing the image at position (0, 0)
    bottom = image.get_size()[1]
    center = WINDOW_SIZE[0] / 2
    text_line = bottom + line_spacing
    display_text(center, text_line, f'[{quiz_line_index}] ' + quiz_line['flashcard'] + ' (SPACE to copy)', (0, 0, 0), screen)
    text_line += line_spacing
    text_line += line_spacing

    if stage == 0:
        display_text(center, text_line, quiz_line['prompt'], (0, 0, 0), screen)
        text_line += line_spacing
        display_text(center, text_line, f'Question {num_questions}. Press letter of choice below or Q to quit', (0, 0, 0), screen)
        text_line += line_spacing
        text_line += line_spacing

        col = 0
        for choice in choices.keys():
            answer_index = choices[choice]
            answer = quiz_line['answers'][answer_index]
            display = '[' + choice + '] ' + answer[0]
            color = (0, 0, 0)
            display_text(columns[col], text_line, display, color, screen, center_x=False)
            col += 1
            if col >= COLUMNS:
                col = 0
                text_line += line_spacing
    elif stage == 1:
        if done_reviewing:
            display_text(center, text_line, 'No more positions to review. Pres Q key to see summary.', (0, 0, 0), screen)
        else:
            user_answer = quiz_line['answers'][user_choice[0][0]][0]
            correct_answer = quiz_line['answers'][0][0]
            display_text(center, text_line, f'You chose {user_answer} the correct choice was {correct_answer}', (0, 0, 0), screen)
            text_line += line_spacing

            for x in range(len(quiz_line['answers'])):
                color = (0, 0, 0)
                if x == user_choice[0][0]:
                    color = (0, 128, 0) if x == 0 else (255, 0, 0)
                display_text(columns[0], text_line, f'{quiz_line["answers"][x][0]}', color, screen, center_x=False)
                display_text(columns[2], text_line, f'{float(quiz_line["answers"][x][1]):8.3f}', color, screen, center_x=False)
                text_line += line_spacing
            text_line += line_spacing

            total_right_h = 0.0
            total_wrong_h = 0.0
            total_error_h = 0.0
            history = copy.deepcopy(qc.history)
            v_list = history.get(str(quiz_line_index), [])
            for v in v_list:
                if v[1] < 0.0:
                    total_wrong_h += 1.0
                else:
                    total_right_h += 1.0
                total_error_h += v[1]

            display_text(center, text_line, f'Right {total_right_h} Wrong {total_wrong_h} Error {total_error_h:.3}', (0, 0, 0), screen)
            text_line += line_spacing
            display_text(center, text_line, 'Press any key to continue or Q to quit', (0, 0, 0), screen)

    elif stage == 2:
        total_answers = total_right + total_wrong
        pct = 0.0 if total_answers == 0.0 else total_right / total_answers
        average_error = 0.0 if total_answers == 0.0 else total_error / total_answers
        display_text(center, text_line, f'You got {total_right:.1f} out of {total_answers:.1f} correct for pct of {pct:.3f}', (0, 0, 0), screen)
        text_line += line_spacing
        display_text(center, text_line, f'Your average error was {average_error:.3f} for a PR of {average_error * -500.0:.3f}', (0, 0, 0), screen)
        text_line += line_spacing
        text_line += line_spacing
        total_answers_h = total_right_h + total_wrong_h
        pct_h = 0.0 if total_answers_h == 0.0 else total_right_h / total_answers_h
        average_error_h = 0.0 if total_answers_h == 0.0 else total_error_h / total_answers_h
        display_text(center, text_line, f'Overall, you got {total_right_h:.1f} out of {total_answers_h:.1f} correct for pct of {pct_h:.3f}', (0, 0, 0), screen)
        text_line += line_spacing
        display_text(center, text_line, f'Your overall error was {average_error_h:.3f} for a PR of {average_error_h * -500.0:.3f}', (0, 0, 0), screen)

    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

    if key == 'Q':
        key = ''
        stage += 1
        if stage == 1:
            session = copy.deepcopy(qc.session)
            quiz_line_index = list(session.keys())[0]
            user_choice = session.pop(quiz_line_index)
            quiz_line = quiz[int(quiz_line_index)]
            choices = get_choices(quiz_line)
            # print(choices)
            image = load_flashcard(quiz_line)
        elif stage == 2:
            session = copy.deepcopy(qc.session)
            total_right = 0.0
            total_wrong = 0.0
            total_error = 0.0
            for k in session.keys():
                v_list = session[k]
                for v in v_list:
                    if v[1] < 0.0:
                        total_wrong += 1.0
                    else:
                        total_right += 1.0
                    total_error += v[1]
            history = copy.deepcopy(qc.history)
            total_right_h = 0.0
            total_wrong_h = 0.0
            total_error_h = 0.0
            for k in history.keys():
                v_list = history[k]
                for v in v_list:
                    if v[1] < 0.0:
                        total_wrong_h += 1.0
                    else:
                        total_right_h += 1.0
                    total_error_h += v[1]
        if stage > 2:
            break

qc.print_report()
qc.save()
pygame.quit()
import os
import sys

import pygame
import pygame.draw
import pygame.image
import copy
import random
import json
from quiz_controller import QuizController

WINDOW_SIZE = (800, 800)
BG_COLOR = (255, 255, 255)
COLUMNS = 3
COLUMN_WIDTH = WINDOW_SIZE[0] // (COLUMNS + 1)

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
        qc = QuizController(directory + 'qc.json', len(quiz), 10)
    except Exception as e:
        print(f'ERROR: Problem loading quiz {str(e)}')
        sys.exit(1)

else:
    print('USAGE: quiz <directory>')
    sys.exit(1)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Backgammon Position Editor")
font = pygame.font.Font(None, 24)

running = True


def choose_quiz_line():
    return qc.get_question_index()


def load_flashcard(quiz_line):
    image_path = directory + 'flashcards/' + quiz_line['flashcard']
    return pygame.image.load(image_path)


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
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if pygame.K_a <= event.key <= pygame.K_z:
                key = chr(ord('A') + event.key - pygame.K_a)
                print(key)

                if stage == 0:
                    if key in choices:
                        answer = quiz_line['answers'][choices[key]]
                        qc.post_result(quiz_line_index, choices[key], float(answer[1]))
                        qc.dump()
                        quiz_line_index = choose_quiz_line()
                        quiz_line = quiz[quiz_line_index]
                        choices = get_choices(quiz_line)
                        print(choices)
                        image = load_flashcard(quiz_line)
                elif stage == 1:
                    if len(session) > 0:
                        quiz_line_index = list(session.keys())[0]
                        user_choice = session.pop(quiz_line_index)
                        quiz_line = quiz[quiz_line_index]
                        choices = get_choices(quiz_line)
                        print(choices)
                        image = load_flashcard(quiz_line)


    # Clear the screen
    screen.fill(BG_COLOR)
    left = (WINDOW_SIZE[0] - image.get_size()[0]) // 2
    screen.blit(image, (left, 0))  # Drawing the image at position (0, 0)
    bottom = image.get_size()[1]
    center = WINDOW_SIZE[0] / 2
    text_line = bottom + line_spacing

    if stage == 0:
        display_text(center, text_line, quiz_line['prompt'], (0, 0, 0), screen)
        text_line += line_spacing
        display_text(center, text_line, 'Press letter of choice below or Q to quit', (0, 0, 0), screen)
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
        user_answer = quiz_line['answers'][user_choice[0][0]][0]
        correct_answer = quiz_line['answers'][0][0]
        display_text(center, text_line, f'You chose {user_answer} the correct choice was {correct_answer}', (0, 0, 0), screen)
        text_line += line_spacing
        if user_answer == correct_answer:
            display_text(center, text_line, 'CORRECT', (0, 255, 0), screen)
        else:
            display_text(center, text_line, f'ERROR! ({quiz_line["answers"][user_choice[0][0]][1]})', (255, 0, 0), screen)

        text_line += line_spacing
        display_text(center, text_line, 'Press any key to continue or Q to quit', (0, 0, 0), screen)

    elif stage == 2:
        total_answers = total_right + total_wrong
        pct = 0.0 if total_answers == 0.0 else total_right / total_answers
        average_error = 0.0 if total_answers == 0.0 else total_error / total_answers
        display_text(center, text_line, f'You got {total_right} out of {total_answers} correct for pct of {pct}', (0, 0, 0), screen)
        text_line += line_spacing
        display_text(center, text_line, f'Your average error was {average_error} for a PR of {average_error * -500.0}', (0, 0, 0), screen)

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
            quiz_line = quiz[quiz_line_index]
            choices = get_choices(quiz_line)
            print(choices)
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
        if stage > 2:
            break

qc.save()
pygame.quit()
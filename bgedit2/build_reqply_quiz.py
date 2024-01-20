import json
import sys

BASE_FILENAME = 'return_report.json'

try:
    # Attempt to open and read the JSON file
    with open(BASE_FILENAME, 'r') as json_file:
        report = json.load(json_file)

except Exception as e:
    report = []
    sys.exit(1)

directory = './quiz/return_shots/'
quiz = []
for line in report:
# for line in report[:5]:
    quiz_line = {}
    dice = line[3]
    dice_str = str(dice[0]) + str(dice[1])
    filename = directory + str(line[1][0]) + str(line[1][1]) + str(line[2]) + '/' + dice_str + '.txt'
    quiz_line['flashcard'] = line[0]
    try:
        # Attempt to open and read the JSON file
        with open(filename, 'r') as data_file:
            data = data_file.read().split('\n')
            roll_to_play = data[19].split(' ')[3]
            if dice_str != roll_to_play:
                print(f'ERROR: Dice mismatch! [{dice_str}] [{roll_to_play}]')
                continue
            quiz_line['prompt'] = 'Choose best move for ' + roll_to_play
            first_play_line = 21
            best_move = True
            answers = []
            while first_play_line < len(data):
                data_line = data[first_play_line]
                if 'eq:' in data_line:
                    play = data_line[19:48].strip()
                    score = '0.000'
                    if best_move:
                        best_move = False
                    else:
                        score_line = data_line.split('eq:')[1]
                        if '(' in score_line:
                            score = score_line.split('(')[1].split(')')[0]

                    print(f'[{play}] [{score}]')
                    answers.append([play, score])
                    # print(f'[{score}]')
                first_play_line+= 1
            quiz_line['answers'] = answers
            quiz.append(quiz_line)
    except Exception as e:
        print(f'ERROR: in file: {filename}, {str(e)}')

    # print(line, filename, filename)

with open(directory + 'quiz.json', 'w') as json_file:
    json.dump(quiz, json_file, indent=4)

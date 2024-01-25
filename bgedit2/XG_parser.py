

def file_to_quiz_line(filename):
    quiz_line = {}
    try:
        # Attempt to open and read the JSON file
        with open(filename, 'r') as data_file:
            data = data_file.read().split('\n')

            quiz_line['flashcard'] = data[0].split('=')[1]

            roll_to_play = data[19].split(' ')[3]
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

                    # print(f'[{play}] [{score}]')
                    answers.append([play, score])
                    # print(f'[{score}]')
                first_play_line += 1
            quiz_line['answers'] = answers
    except Exception as e:
        print(f'ERROR: in file: {filename}, {str(e)}')

    return quiz_line

if __name__ == '__main__':
    print(file_to_quiz_line('C:\\GitHub\\RL\\bgedit2\\quiz\\return_shots\\210\\43.txt'))

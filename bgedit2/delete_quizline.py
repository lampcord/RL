import json
import os
import sys
from quiz_controller import QuizController

if len(sys.argv) < 3:
    print('Usage: delete_quizline.py <quiz_dir> <quizline index>')
    sys.exit(0)

dest_dir = './quiz/' + sys.argv[1]
pos_dir = dest_dir + '/positions'

quizline_index = int(sys.argv[2])

try:
    quiz_filename = dest_dir + '/quiz.json'
    print(quiz_filename)
    # Attempt to open and read the JSON file
    with open(quiz_filename, 'r') as json_file:
        quiz = json.load(json_file)
except Exception as e:
    quiz = []

qc = QuizController(dest_dir + '/qc.json', len(quiz), 0.99)

print("=" * 180)


def dump_state(label):
    print("-" * 180)
    print(label)
    print("-" * 180)
    for x in range(len(quiz)):
        line = str(quiz[x])
        print(f'{x:3} {line[:160]}')

    qc.dump()


last_quizline_index = len(quiz) - 1
if quizline_index < 0 or quizline_index >= len(quiz):
    print(f'quizline out of range.')
    sys.exit(0)

dump_state("Start")

# remove last quizline
source_quizline = quiz.pop()
target_file = quiz[quizline_index]['flashcard'] + '.txt'
target_file = target_file.replace(':', '_')
target = pos_dir + '/' + target_file

dump_state("Last Removed")
print(source_quizline)

# copy last quizline over target quizline
if quizline_index < len(quiz):
    quiz[quizline_index] = source_quizline
    dump_state("Target Replaced")


# copy last quizline hist over target hist
# remove last quizline hist
if str(quizline_index) in qc.history:
    del qc.history[str(quizline_index)]

if str(last_quizline_index) in qc.history:
    qc.history[str(quizline_index)] = qc.history[str(last_quizline_index)]
    del qc.history[str(last_quizline_index)]


dump_state("Old hist deleted")

# remove source file
print(target)

if os.path.exists(target):
    os.remove(target)
else:
    print(f"The file {target} does not exist")

with open(quiz_filename, 'w') as json_file:
    json.dump(quiz, json_file, indent=4)

qc.save()



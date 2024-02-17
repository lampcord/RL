import json
import os
import sys
from quiz_controller import QuizController

if len(sys.argv) < 3:
    print('Usage: append_quiz.py <target_quiz_dir> <source_quiz_dir>')
    sys.exit(0)

dest_dir_target = './quiz/' + sys.argv[1]
dest_dir_source = './quiz/' + sys.argv[2]

quizline_index = int(sys.argv[2])

# read the target quiz
try:
    quiz_filename_target = dest_dir_target + '/quiz.json'
    print(quiz_filename_target)
    # Attempt to open and read the JSON file
    with open(quiz_filename_target, 'r') as json_file:
        quiz_target = json.load(json_file)
except Exception as e:
    quiz_target = []

# read the target controller
qc_target = QuizController(dest_dir_target + '/qc.json', len(quiz_target), 0.99)

# read the source quiz
try:
    quiz_filename_source = dest_dir_source + '/quiz.json'
    print(quiz_filename_source)
    # Attempt to open and read the JSON file
    with open(quiz_filename_source, 'r') as json_file:
        quiz_source = json.load(json_file)
except Exception as e:
    quiz_source = []

# read the source controller
qc_source = QuizController(dest_dir_source + '/qc.json', len(quiz_source), 0.99)

# calculate append offset
append_offset = len(quiz_target) + 1

# for each quiz line in source quiz
for quizline in quiz_source:
    # add quiz line to target quiz
    quiz_target.append(quizline)

for k in qc_source.history.keys():
    # target index = source index + append offset
    target_k = str(int(k) + append_offset)
    # add source hist to target hist
    qc_target.history[target_k] = qc_source.history[k]

for k in qc_source.last_visited.keys():
    # target index = source index + append offset
    target_k = str(int(k) + append_offset)
    # add source last visited to target last visited
    qc_target.last_visited[target_k] = qc_source.last_visited[k]


# save target quiz
with open(quiz_filename_target, 'w') as json_file:
    json.dump(quiz_target, json_file, indent=4)

# save target controller
qc_target.save()



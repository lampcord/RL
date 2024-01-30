import os.path
import sys
import json
import glob
from XG_parser import file_to_quiz_line

if len(sys.argv) < 2:
    print('Usage: build_quiz <quiz_dir>')
    sys.exit(0)

dest_dir = './quiz/' + sys.argv[1]
pos_dir = dest_dir + '/positions'

try:
    quiz_filename = dest_dir + '/quiz.json'
    # Attempt to open and read the JSON file
    with open(quiz_filename, 'r') as json_file:
        quiz = json.load(json_file)
except Exception as e:
    quiz = []

keys = {}
for quiz_line in quiz:
    keys[quiz_line['flashcard']] = True

files = glob.glob(pos_dir + '/*.txt')
print (files)

new_files = 0
for file in files:
    filename = os.path.basename(file)
    quiz_line = file_to_quiz_line(file)
    # print(filename)
    if quiz_line['flashcard'] not in keys:
        print(quiz_line)
        quiz.append(quiz_line)
        new_files += 1

print(f'Found {new_files} new files.')

with open(quiz_filename, 'w') as json_file:
    json.dump(quiz, json_file, indent=4)


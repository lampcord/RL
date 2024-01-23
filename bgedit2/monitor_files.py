import os
import sys, glob
import time
from XG_parser import file_to_quiz_line

if len(sys.argv) < 3:
    print('Usage: monitor_files <file_pattern> <dest_dir>')
    sys.exit(0)

file_pattern = sys.argv[1]
dest_dir = sys.argv[2] + '\\positions'

while True:
    files = glob.glob(file_pattern)
    print(files)
    if len(files) > 0:
        time.sleep(2.0)
        position = file_to_quiz_line(files[0])
        print(position)
        target_file = position['flashcard'] + '.txt'
        target_file = target_file.replace(':', '_')
        target = dest_dir + '\\' + target_file
        print(target)
        os.rename(files[0], target)
    time.sleep(1.0)
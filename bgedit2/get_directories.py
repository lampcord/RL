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

last_directory = ''
for line in report:
    directory = str(line[1][0]) + str(line[1][1]) + str(line[2])
    if directory != last_directory:
        filename = line[0]
        print(filename, directory)
        last_directory = directory
import os
import sys
import copy

import json

BASE_FILENAME = 'return_base.json'
TARGET_FILENAME = 'return.json'
REPORT_FILENAME = 'return_report.json'

try:
    # Attempt to open and read the JSON file
    with open(BASE_FILENAME, 'r') as json_file:
        positions = json.load(json_file)

except Exception as e:
    positions = []

target = []
report = []
pos_number = 0
prev_dice = []
version = 0

for pos in positions:
    new_pos = copy.deepcopy(pos)
    new_pos['turn'] = 0
    orig_dice = new_pos['dice']
    version += 1
    if orig_dice != prev_dice:
        version = 0
    prev_dice = copy.deepcopy(orig_dice)

    for d1 in range(1, 7):
        for d2 in range(d1, 7):
            new_pos['dice'] = [d2, d1]
            target.append(copy.deepcopy(new_pos))
            report.append(['position_{:06d}.png'.format(pos_number), orig_dice, version, [d2,d1]])
            pos_number += 1



with open(TARGET_FILENAME, 'w') as json_file:
    json.dump(target, json_file, indent=4)

with open(REPORT_FILENAME, 'w') as json_file:
    json.dump(report, json_file, indent=4)



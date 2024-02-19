path = 'C:\\GitHub\\RL\\Gammon\\training_games\\X001.txt'

data = open(path, 'r').read().split('\n')

last_number = 0
test = ''
counts = []
for line in data:
    if 'Wins' in line:
        print(test)
        counts.append(test)
    test = line[:4]
    if ')' in test:
        test = int(test.replace(')', ''))

counts.sort()
print(counts)
total = 0.0
breakdown = {}
for result in counts:
    total += result
    breakdown[result] = breakdown.get(result, 0) + 1

print(counts[len(counts) // 2])
print(total / len(counts))
print(len(counts))

for b in breakdown.keys():
    print(f'{b:3} {breakdown[b]}')

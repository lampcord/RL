import numpy as np
import time

loops = 1000000

before = time.time_ns()
data = []
for x in range(loops):
    data.clear()
    sum = 0
    for y in range(14):
        data.append(y)
    for v in data:
        sum += v
after = time.time_ns()
print(f"List time {float(after - before) / 1000000000.0}")

before = time.time_ns()
data = np.arange(14, dtype=int)
for x in range(loops):
    sum = 0
    for y in range(14):
        data[y] = y
    sum = np.sum(data)
after = time.time_ns()
print(f"Array time {float(after - before) / 1000000000.0}")


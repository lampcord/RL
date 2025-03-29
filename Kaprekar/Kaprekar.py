import sys

sizes = {}
counts = {}

def transform(num):
    num = 10000 + num
    strnum = list(str(num)[1:])
    strnum.sort(reverse=True)
    big = int("".join(strnum))
    strnum.sort()
    little = int("".join(strnum))
    return(big - little)
    
def reduce(x):
    count = 0
    start = x
    print('--------------------------------------')
    print(x)
    print('--------------------------------------')
    while (x != 0 and x != 6174):
        x = transform(x)
        c = counts.get(x, 0)
        c += 1  
        counts[x] = c
        print(x)
        count += 1
    print('--------------------------------------')
    l = sizes.get(count, [])
    l.append(start)
    sizes[count] = l

for x in range(10000):
    reduce(x)

for x in sizes.keys():
    print(x, '=>', sizes[x])

for x in counts.keys():
    print(x, '=>', counts[x])

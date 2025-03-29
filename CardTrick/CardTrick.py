import random

for loops in range(10000):
    if loops % 100 == 0:
        print('')
    print('.', end='')


    deck = list(range(1,53))
    #print(deck)

    split = random.randint(22, 30)
    # cut the cards
    s1 = deck[:split]
    s2 = deck[split:]
    #print(s1)
    #print(s2)

    # reverse one stack
    s2.reverse()
    #print(s2)

    # shuffle the stacks
    deck = []
    while len(s1) > 0 or len(s2) > 0:
        if len(s1) > 0 and random.randint(1,10) > 1:
            deck.append(s1[0])
            s1 = s1[1:]
        if len(s2) > 0 and random.randint(1,10) > 1:
            deck.append(s2[0])
            s2 = s2[1:]
    #print(deck)

    # deal out 2 stacks of 10
    s1 = []
    s2 = []
    for x in range(10):
        s1.append(deck[0])
        deck = deck[1:]
        s2.append(deck[0])
        deck = deck[1:]
    #print(s1)
    #print(s2)

    # verify
    for x in range(10):
        t = s1[x] + s2[x]
        if t % 2 == 0:
            print('ERROR!!!')
print('')
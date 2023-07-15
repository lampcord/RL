import random

from backgammon import Backgammon, WHITE, BLACK
from random import randint

game = Backgammon()

player = WHITE
winner = None
num_moves = 0
while not winner and num_moves < 100:
    # game.render()
    game.export()
    roll = randint(1, 6), randint(1, 6)
    if player == WHITE:
        roll = -roll[0], -roll[1]
    moves = list(game.get_valid_plays(player, roll))
    if len(moves) > 0:
        choice = random.choice(moves)
        game.execute_play(player, choice)
        print(f'{str(player):>3}{str(abs(roll[0])):>3}{str(abs(roll[1])):>3}', end='')
        for submove in choice:
            print(f'{submove[0]:>3}', end='')
            print(f'{submove[1]:>3}', end='')
        print()
        for move in moves:
            for submove in move:
                print(f'{submove[0]:>3}', end='')
                print(f'{submove[1]:>3}', end='')
            print()
    winner = game.get_winner()
    player = BLACK if player == WHITE else WHITE
    num_moves += 1
print (winner)
if __name__ == '__main__':
    pass

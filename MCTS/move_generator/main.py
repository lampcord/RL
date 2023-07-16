import random

from backgammon import Backgammon, WHITE, BLACK
from random import randint
from copy import deepcopy

def run_one_game(player):
    game = Backgammon()
    hold_game = Backgammon()
    render_game = Backgammon()

    winner = None
    num_moves = 0
    while not winner and num_moves < 200:
        # game.render()
        print('POS:', end='')
        game.export()
        hold_game = deepcopy(game)
        roll = randint(1, 6), randint(1, 6)
        # roll = 1, 3
        print(f'ROL:{str(abs(roll[0])):>3}{str(abs(roll[1])):>3}')
        if player == WHITE:
            roll = -roll[0], -roll[1]
        moves = list(game.get_valid_plays(player, roll))
        if len(moves) > 0:
            choice = random.choice(moves)
            game.execute_play(player, choice)
            print(f'PLY:{str(player):>3}')
            print('CHC:',end='')
            for submove in choice:
                print(f'{submove[0]:>3}', end='')
                print(f'{submove[1]:>3}', end='')
            print()
            for move in moves:
                print('MOV:',end='')
                for submove in move:
                    print(f'{submove[0]:>3}', end='')
                    print(f'{submove[1]:>3}', end='')
                print()
                print('RES:', end='')
                render_game = deepcopy(hold_game)
                render_game.execute_play(player, move)
                render_game.export()

        winner = game.get_winner()
        player = BLACK if player == WHITE else WHITE
        num_moves += 1
# print (winner)


if __name__ == '__main__':
    for x in range(5):
        run_one_game(WHITE)
        run_one_game(WHITE)

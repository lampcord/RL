import random

from mancalalib import game


def render(state_int, turn):
    state_list = game.decode_binary(state_int)
    possible_moves = game.possible_moves(state_int, turn)
    print(state_list)

    if turn == game.PLAYER_BLACK:
        print("     ", end='')
        ndx = game.BLACK_CASTOFF_BUCKET - 1
        move = 5
        while move >= 0:
            if move in possible_moves:
                print("{:>3} ".format(move), end='')
            else:
                print("  - ", end='')
            ndx -= 1
            move -= 1
        print("    Black's Turn")

    print("+---+---+---+---+---+---+---+---+")

    print("|   |", end='')
    ndx = game.BLACK_CASTOFF_BUCKET - 1
    for _ in range(6):
        print("{:>3}|".format(state_list[ndx]), end='')
        ndx -= 1
    print("   |")

    print("|{:>3}|".format(state_list[game.BLACK_CASTOFF_BUCKET]), end='')
    print("---+---+---+---+---+---", end='')
    print("|{:>3}|".format(state_list[game.WHITE_CASTOFF_BUCKET]))

    print("|   |", end='')
    ndx = game.WHITE_FIRST_BUCKET
    for _ in range(6):
        print("{:>3}|".format(state_list[ndx]), end='')
        ndx += 1
    print("   |")

    print("+---+---+---+---+---+---+---+---+")

    if turn == game.PLAYER_WHITE:
        print("     ", end='')
        ndx = game.WHITE_FIRST_BUCKET
        for move in range(6):
            if move in possible_moves:
                print("{:>3} ".format(move), end='')
            else:
                print("  - ", end='')
            ndx += 1
        print("    White's Turn")


if __name__ == "__main__":
    state_int = game.INITIAL_STATE
    # state_int = game.encode_lists([1, 2, 3, 4, 5, 6, 4, 1, 2, 3, 4, 5, 6, 2])
    done = False
    turn = game.PLAYER_WHITE
    while not done:
        print('')
        render(state_int, turn)
        possible_moves = game.possible_moves(state_int, turn)
        if len(possible_moves) == 0:
            print('No legal moves!')
            turn = game.get_opponent(turn)
            break
        if turn == game.PLAYER_WHITE:
            move = random.choice(possible_moves)
        else:
            move = int(input("Enter move:"))
        print(f"Move {move}")
        state_int, winner, swap_players = game.move(state_int, move, turn)
        if swap_players:
            turn = game.get_opponent(turn)
        if winner is not None:
            print("White " if winner == game.PLAYER_WHITE else "Black ", end='')
            print("wins!")
            render(state_int, turn)
            break

    # turn = game.PLAYER_BLACK
    # for _ in range(10):
    #     print('')
    #     state_int = game.encode_lists(game.generate_random_board())
    #     render(state_int,turn)
    #     turn = game.get_opponent(turn)
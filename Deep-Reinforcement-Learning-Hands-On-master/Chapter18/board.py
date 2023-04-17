import random

from mancalalib import game


def render(state_int, turn):
    state_list = game.decode_binary(state_int)
    possible_moves = game.possible_moves(state_int, turn)
    print('-' * 60)
    print(state_int)
    print('-' * 60)
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
    print('-' * 60)


# RULE1: if the last stone goes in your castoff bucket, you can keep going
def test_rule_1():
    state_int = game.encode_lists([6, 5, 4, 3, 2, 1, 3, 6, 5, 4, 3, 2, 1, 3])
    turn = game.PLAYER_WHITE
    render(state_int, turn)
    move = 5
    while move >= 0:
        possible_moves = game.possible_moves(state_int, turn)
        assert move in possible_moves
        state_int, winner, swap_players = game.move(state_int, move, turn)
        render(state_int, turn)
        assert not winner
        assert not swap_players
        move -= 1

    state_int, winner, swap_players = game.move(state_int, 1, turn)
    render(state_int, turn)
    assert not winner
    assert swap_players
    turn = game.get_opponent(turn)

    move = 5
    while move >= 0:
        possible_moves = game.possible_moves(state_int, turn)
        assert move in possible_moves
        state_int, winner, swap_players = game.move(state_int, move, turn)
        render(state_int, turn)
        assert not winner
        assert not swap_players
        move -= 1


# RULE2: if next player has no legal moves, all the stones remaining go into next player's opponent's castoff bucket
def test_rule_2():
    state_int = 148764069216649217
    turn = game.PLAYER_BLACK
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 5, turn)
    assert state_int == 4539628428650872833
    assert not swap_players
    render(state_int, turn)

    state_int = 148764069208260609
    turn = game.PLAYER_BLACK
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 5, turn)
    assert swap_players
    turn = game.get_opponent(turn)
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 0, turn)
    assert state_int == 4539628426520166401
    render(state_int, turn)


# RULE4: If the last piece you drop is in an empty hole on your side,
# you capture that piece and any pieces in the hole directly opposite.
def test_rule_4():
    state_int = 2311054832843284497
    turn = game.PLAYER_BLACK
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 2, turn)
    turn = game.get_opponent(turn)
    render(state_int, turn)
    assert state_int == 2313179504850174081
    assert swap_players

    turn = game.PLAYER_BLACK
    state_int = 148764067119728707
    render(state_int, turn)
    state_int, winner, swap_players = game.move(state_int, 0, turn)
    render(state_int, turn)
    assert swap_players
    assert state_int == 73201369230622977


def play_human_against_random():
    state_int = game.INITIAL_STATE
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

if __name__ == "__main__":
    # test_rule_1()
    # test_rule_2()
    test_rule_4()
    # play_human_against_random()
    # turn = game.PLAYER_BLACK
    # for _ in range(10):
    #     print('')
    #     state_int = game.encode_lists(game.generate_random_board())
    #     render(state_int,turn)
    #     turn = game.get_opponent(turn)
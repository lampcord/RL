
def get_position(xgid):
    clear_checkers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    sections = xgid.split(':')
    checkers = list(sections[0])
    dice = list(sections[4])

    has_rolled = True
    if sections[4] == '00':
        dice = ['1', '1']
        has_rolled = False

    for x in range(26):
        c = checkers[x]
        v = 0
        if 'a' <= c <= 'o':
            v = -1 * (ord(c) - ord('a') + 1)
        if 'A' <= c <= 'O':
            v = ord(c) - ord('A') + 1
        print (c, v)

        if x == 0:
            clear_checkers[25] = v
        elif x == 25:
            clear_checkers[24] = v
        else:
            clear_checkers[24 - x] = v

    cube = 0
    if sections[1] != '0':
        if sections[2] == '1':
            cube = int(sections[1])
        else:
            cube = -1 * int(sections[1])

    turn = 1
    if sections[3] == '1':
        turn = 0

    print(sections)
    print(checkers)
    print(dice)

    position = {}
    position["checkers"] = list(clear_checkers)
    position["turn"] = turn
    position["has_rolled"] = has_rolled
    position["dice"] = [int(dice[0]), int(dice[1])]
    position["cube"] = cube

    return position


if __name__ == '__main__':
    from bg_board import *

    board_image = pygame.Surface(WINDOW_SIZE)
    board_image.fill(BG_COLOR)
    #pos= 'XGID=ab----C-C---eE---c-d----BB:0:0:1:63:0:0:3:0:10'
    #pos= 'XGID=ab----C-C---eE---c-d----BB:0:0:-1:14:0:0:3:0:10'
    pos = 'XGID=-b----E-C---dEa--c-da---B-:0:0:1:43:0:0:3:0:10'
    position = get_position(pos.split('=')[1])
    print(position)
    draw_board(position, board_image)
    pygame.image.save(board_image, 'test.png')
    pygame.quit()


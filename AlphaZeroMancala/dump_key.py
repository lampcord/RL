from connect_4.c4_console_renderer import C4ConsoleRenderer

keys = (35734131496540, 35734131496541)
for key in keys:
    turn = key & 0x1
    position = key // 2
    renderer = C4ConsoleRenderer()
    renderer.render(position, turn)
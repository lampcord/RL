from connect_4.c4_console_renderer import C4ConsoleRenderer
import argparse

parser = argparse.ArgumentParser(description="Enter positions separated by spaces")
parser.add_argument('args', metavar='N', type=str, nargs='*', help="Variable length arguments")

args = parser.parse_args()

for arg in args.args:
    print(arg)

keys = (args.args)
for skey in keys:
    key = int(skey)
    turn = key & 0x1
    position = key // 2
    renderer = C4ConsoleRenderer()
    renderer.render(position, turn)
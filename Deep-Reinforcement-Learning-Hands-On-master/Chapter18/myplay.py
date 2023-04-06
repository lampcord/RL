#!/usr/bin/env python3
import numpy as np
from lib import game, model, mcts, board
import torch
import pygame

MCTS_SEARCHES = 1000
MCTS_BATCH_SIZE = 4
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600


class Session:
    BOT_PLAYER = game.PLAYER_BLACK
    USER_PLAYER = game.PLAYER_WHITE

    def __init__(self, model_file, player_moves_first, player_id):
        self.model_file = model_file
        self.model = model.Net(input_shape=model.OBS_SHAPE, actions_n=game.GAME_COLS)
        self.model.load_state_dict(torch.load(model_file, map_location=lambda storage, loc: storage))
        self.state = game.INITIAL_STATE
        self.value = None
        self.player_moves_first = player_moves_first
        self.player_id = player_id
        self.moves = []
        self.mcts_store = mcts.MCTS()

    def move_player(self, col):
        self.moves.append(col)
        self.state, won = game.move(self.state, col, self.USER_PLAYER)
        return won

    def move_bot(self):
        self.mcts_store.search_batch(MCTS_SEARCHES, MCTS_BATCH_SIZE, self.state, self.BOT_PLAYER, self.model)
        probs, values = self.mcts_store.get_policy_value(self.state, tau=0)
        print(f"P:{probs}")
        print(f"V:{values}")
        action = np.random.choice(game.GAME_COLS, p=probs)
        self.value = values[action]
        self.moves.append(action)
        self.state, won = game.move(self.state, action, self.BOT_PLAYER)
        return won

    def is_valid_move(self, move_col):
        return move_col in game.possible_moves(self.state)

    def is_draw(self):
        return len(game.possible_moves(self.state)) == 0

    def render(self):
        l = game.render(self.state)
        l = "\n".join(l)
        l = l.replace("0", 'O').replace("1", "X")
        board = "0123456\n-------\n" + l + "\n-------\n0123456"
        extra = ""
        if self.value is not None:
            extra = "Position evaluation: %.2f\n" % float(self.value)
        return extra + "%s" % board

    def gui_render(self, screen):
        state_list = game.decode_binary(self.state)
        board.draw_board(screen, state_list)
        pygame.display.update()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Connect 4")
human_is_current = True
session = Session('saves/Test1CPU/best_016_03500.dat', human_is_current, 'Mike')
if __name__ == "__main__":
    game_over = False
    while not game_over:
        print(session.render())
        session.gui_render(screen)
        print("===========================\n")
        if human_is_current:
            move = input('Enter move:')
            if move == 'q':
                break
            won = session.move_player(int(move))
        else:
            won = session.move_bot()
        if won:
            print(f"{session.player_id if human_is_current else 'Bot'} won!")
            game_over = True
        elif session.is_draw():
            print("Draw!")
            game_over = True
        human_is_current = not human_is_current
    print(session.render())
    session.gui_render(screen)

    # logging.basicConfig(format="%(asctime)-15s %(levelname)s %(message)s", level=logging.INFO)
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--config", default=CONFIG_DEFAULT,
    #                     help="Configuration file for the bot, default=" + CONFIG_DEFAULT)
    # parser.add_argument("-m", "--models", required=True, help="Directory name with models to serve")
    # parser.add_argument("-l", "--log", required=True, help="Log name to keep the games and leaderboard")
    # prog_args = parser.parse_args()

    # conf = configparser.ConfigParser()
    # if not conf.read(os.path.expanduser(prog_args.config)):
    #     log.error("Configuration file %s not found", prog_args.config)
    #     sys.exit()

    # player_bot = PlayerBot(prog_args.models, prog_args.log)
    #
    # updater = telegram.ext.Updater(conf['telegram']['api'])
    # updater.dispatcher.add_handler(telegram.ext.CommandHandler('help', player_bot.command_help))
    # updater.dispatcher.add_handler(telegram.ext.CommandHandler('list', player_bot.command_list))
    # updater.dispatcher.add_handler(telegram.ext.CommandHandler('top', player_bot.command_top))
    # updater.dispatcher.add_handler(telegram.ext.CommandHandler('play', player_bot.command_play, pass_args=True))
    # updater.dispatcher.add_handler(telegram.ext.CommandHandler('refresh', player_bot.command_refresh))
    # updater.dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, player_bot.text))
    # updater.dispatcher.add_error_handler(player_bot.error)
    #
    # log.info("Bot initialized, started serving")
    # updater.start_polling()
    # updater.idle()
    #
    # pass

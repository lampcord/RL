"""
TournamentDirector - The TournamentDirectory is in charge of managing games between agents. This includes prompting for moves, recording results and any other control or monitoring tasks that are outside of the domain of the game or agent.

Interface:
Init(GameRules, AgentList, NumberOfGames, <TimeLimit>)
AgentList is a list of previously instantiated players
NumberOfGames is the number of games between each player pairing.

Run()
Returns:
A list of all of the matchups and results including the total thinking time of each of the players.


"""
import game_rules
from lib.utils import rotate
import time


class TournamentDirector:
    def __init__(self, game_rules, agent_list, number_of_games, renderer, time_limit=None):
        self.game_rules = game_rules
        self.agent_list = agent_list
        self.number_of_games = number_of_games
        self.renderer = renderer
        self.time_limit = time_limit

    def build_tournament_set(self):
        '''
        tournment set is a collection of:
        game_number, [players in order of play], result, [time to move for each player]
        :return:
        '''
        tournament_set = []
        tournament_set_pairing = [x for x in range(len(self.agent_list))]
        blank_times = [0.0 for x in range(len(self.agent_list))]
        for game_number in range(self.number_of_games):
            tournament_set_entry = {
                'game_number': game_number + 1,
                'tournament_set_pairing': tournament_set_pairing,
                'result': None,
                'times': list(blank_times)
            }
            tournament_set_pairing = rotate(tournament_set_pairing, 1)
            tournament_set.append(tournament_set_entry)
        return tournament_set

    def print_tournament_set(self, tournament_set):
        sep = '---- '
        for player_number in range(len(self.agent_list)):
            sep += '------- '
        sep += '------ '
        for player_number in range(len(self.agent_list)):
            sep += '------- '
        print(sep)

        print('Game ', end='')
        for player_number in range(len(self.agent_list)):
            print(f'Turn {player_number:2} ', end='')
        print('Winner ', end='')
        for player_number in range(len(self.agent_list)):
            print(f'Time {player_number:2} ', end='')
        print()
        print(sep)

        wins_by_player = {}
        wins_by_turn = {}
        time_by_player = {}
        for player_number in range(len(self.agent_list)):
            wins_by_player[player_number] = 0.0
            wins_by_turn[player_number] = 0.0
            time_by_player[player_number] = 0.0

        for entry in tournament_set:
            game_number = entry['game_number']
            print(f'{game_number:4} ', end='')
            tournament_set_pairing = entry['tournament_set_pairing']
            for player_number in range(len(self.agent_list)):
                print(f'{tournament_set_pairing[player_number]:7} ', end='')

            result = entry['result']
            if result is not None:
                wins_by_player[result] += 1.0
                for turn in range(len(tournament_set_pairing)):
                    player_turn = tournament_set_pairing[turn]
                    if player_turn == result:
                        wins_by_turn[turn] += 1.0
            else:
                for player_number in range(len(self.agent_list)):
                    wins_by_player[player_number] += 0.5
                    wins_by_turn[player_number] += 0.5
            print(f'{str(result):>6} ', end='')

            times = entry['times']
            for player_number in range(len(self.agent_list)):
                time_by_player[player_number] += times[player_number]
                print(f'{times[player_number]:>7.2f} ', end='')
            print()

        print(sep)

        print(wins_by_player)
        print(wins_by_turn)
        print(time_by_player)

        print()
        print('------ ------- ----------')
        print('Player  Score  Total Time')
        print('------ ------- ----------')
        for player_number in range(len(self.agent_list)):
            print(f'{player_number:6} ', end='')
            print(f'{wins_by_player[player_number]:>7.1f} ', end='')
            print(f'{time_by_player[player_number]:>10.4f} ')
        print('------ ------- ----------')

        print()
        print('------ -------')
        print(' Turn   Score')
        print('------ -------')
        for turn_number in range(len(self.agent_list)):
            print(f'{turn_number:6} ', end='')
            print(f'{wins_by_turn[turn_number]:>7.1f} ')
        print('------ -------')

    def run(self):
        tournament_set = self.build_tournament_set()

        for ndx in range(len(tournament_set)):
            tournament_set_entry = tournament_set[ndx]
            game_number = tournament_set_entry['game_number']
            tournament_set_pairing = tournament_set_entry['tournament_set_pairing']

            state = self.game_rules.get_initial_position()
            result = game_rules.GameResult.CONTINUE
            info = {}
            turn = tournament_set_pairing[0]
            last_move_turn = turn

            if self.renderer:
                print('-' * 60)
                print(f'Starting game: {game_number}')
                print('-' * 60)
            while result == game_rules.GameResult.CONTINUE:
                agent = self.agent_list[turn]
                if self.renderer:
                    self.renderer.render(state, turn, info)
                last_move_turn = turn
                start_time = time.time_ns()
                state, turn, result, info = agent.move(state, turn)
                elapsed_time = time.time_ns() - start_time
                tournament_set_entry['times'][last_move_turn] += elapsed_time / 1000000000.0

            if self.renderer:
                self.renderer.render(state, turn, info)

            if result == game_rules.GameResult.WIN:
                tournament_set_entry['result'] = last_move_turn

            tournament_set[ndx] = tournament_set_entry

        self.print_tournament_set(tournament_set)

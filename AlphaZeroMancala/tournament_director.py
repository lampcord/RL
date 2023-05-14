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
from rich.console import Console
from rich.table import Table
from rich.progress import Progress


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

    def print_tournament_set(self, tournament_set, detail=False):
        console = Console()
        detail_table = Table(title="Tournament Details")
        detail_table.add_column('Game', justify="right", style="cyan")
        for player_number in range(len(self.agent_list)):
            detail_table.add_column(f'Turn {player_number}', justify="right", style="green3")
        detail_table.add_column('Winner', justify="right", style="bright_magenta")
        for player_number in range(len(self.agent_list)):
            detail_table.add_column(f'Time {player_number}', justify="right", style="red")

        wins_by_player = {}
        wins_by_turn = {}
        time_by_player = {}
        for player_number in range(len(self.agent_list)):
            wins_by_player[player_number] = 0.0
            wins_by_turn[player_number] = 0.0
            time_by_player[player_number] = 0.0

        for entry in tournament_set:
            row = []

            game_number = entry['game_number']
            row.append(str(game_number))

            tournament_set_pairing = entry['tournament_set_pairing']
            for player_number in range(len(self.agent_list)):
                row.append(f'{tournament_set_pairing[player_number]:7}')

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
            row.append(f'{str(result):>6}')

            times = entry['times']
            for player_number in range(len(self.agent_list)):
                time_by_player[player_number] += times[player_number]
                row.append(f'{times[player_number]:>7.4f}')

            detail_table.add_row(*row)
        if detail:
            console.print(detail_table)

        player_summary_table = Table(title='Player Summary')
        player_summary_table.add_column('Player', justify="right", style="cyan")
        player_summary_table.add_column('Score', justify="right", style="bright_magenta")
        player_summary_table.add_column('Time', justify="right", style="red")
        for player_number in range(len(self.agent_list)):
            player_summary_table.add_row(f'{player_number:6}', f'{wins_by_player[player_number]:>7.1f}', f'{time_by_player[player_number]:>10.4f}')

        turn_summary_table = Table(title='Turn Summary')
        turn_summary_table.add_column('Turn', justify="right", style="cyan")
        turn_summary_table.add_column('Score', justify="right", style="bright_magenta")
        for turn_number in range(len(self.agent_list)):
            turn_summary_table.add_row(f'{turn_number:6}', f'{wins_by_turn[turn_number]:>7.1f}')
        console.print(player_summary_table)
        console.print(turn_summary_table)

    def run(self):
        tournament_set = self.build_tournament_set()

        with Progress() as progress:
            task = progress.add_task("[green]Processing...", total=self.number_of_games)

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
                progress.update(task, advance=1)
        return tournament_set

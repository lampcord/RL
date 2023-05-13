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
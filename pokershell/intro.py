import prettytable

INTRO = """
Texas hold'em command line calculator and simulator.

Simulation command example:
JdJc 6 0.2; QdAc8h 4 1.0; Jh 1.5; 2h 3 3.2
"""

t = prettytable.PrettyTable(['Line Tokens', 'Explanation'])
t.max_width["Explanation"] = 70
t.hrules = prettytable.ALL
t.add_row(["'JdJc'",
           "Player's face-down cards. "
           "These cards need to be specified before any other cards "
           "on command line."])
t.add_row(["'5' '4' '2'",
           "Number of players in given stage. The number is decreasing "
           "as players fold."])
t.add_row(["'0.2' '1.0' '1.5' '3.2'",
           "Pot size in given stage. The number is increasing "
           "with continuous betting. The number must contain '.'"
           " to be distinguishable from number of players."])
t.add_row(["';'",
           "Separates game stages. The game stage means whenever game state "
           "changes with (new common card, pot increases by betting "
           "or some player folds). The user can go back in command line history "
           "with up arrow and continue on previous line by writing separator ';' "
           "and after separator writes only what changed since previous state."])
t.add_row(["'QdAc8h'", "Flop cards. Three common cards."])
t.add_row(["'Jh'", "Turn card. Fourth common card."])
t.add_row(["'2h'", "River card. Fifth common card."])
INTRO = '\n'.join((INTRO, str(t),))

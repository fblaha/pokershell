import argparse
import cmd
import collections
import enum
import time

import prettytable

import minsk.config as config
import minsk.eval.bet as bet
import minsk.eval.manager as manager
import minsk.eval.simulation as simulation
import minsk.model as model
import minsk.parser as parser


@enum.unique
class InputTableColumn(enum.Enum):
    HOLE = 'Hole'
    FLOP = 'Flop'
    TURN = 'Turn'
    RIVER = 'River'
    PLAYER_NUM = 'Player Num'
    FOLD_NUM = 'Fold Num'
    HAND = 'Hand'
    RANKS = 'Ranks'
    POT = 'Pot'
    POT_GROWTH = 'Pot Growth'


class MinskShell(cmd.Cmd):
    """Minsk shell"""
    prompt = '(minsk) '

    def __init__(self):
        super().__init__()
        self._sim_manager = simulation.SimulatorManager()

    def _parse_history(self, line):
        if parser.LineParser.validate_syntax(line):
            errors = parser.LineParser.validate_semantics(line)
            if errors:
                for err in errors:
                    print(err)
            else:
                return parser.LineParser.parse_history(line)
        else:
            print("Invalid syntax '%s'" % line)

    def do_brute_force(self, cards):
        """evaluate hand - brute force"""
        state = self._parse_history(cards)
        if state:
            simulator = simulation.BruteForceSimulator()
            self.simulate(state, simulator)

    def do_eval(self, cards):
        """evaluate hand"""
        state = self._parse_history(cards)
        if state:
            simulator = self._sim_manager.find_simulator(
                state.player_num or config.player_num, *state.cards)
            self.simulate(state, simulator)

    def default(self, line):
        if parser.LineParser.validate_syntax(line):
            self.do_eval(line)
        else:
            super().default(line)

    def do_monte_carlo(self, cards):
        """evaluate hand - monte carlo"""
        state = self._parse_history(cards)
        if state:
            simulator = simulation.MonteCarloSimulator(
                config.sim_cycle)
            self.simulate(state, simulator)

    def do_look_up(self, cards):
        """evaluate hand - loop up"""
        state = self._parse_history(cards)
        if state:
            simulator = simulation.LookUpSimulator()
            self.simulate(state, simulator)

    def do_set(self, line):
        """set configuration property"""
        key, val = line.split(maxsplit=2)
        properties = config.get_config_properties()
        if key in properties:
            converter = properties[key]
            # TODO handle conversion error
            setattr(config, key, converter(val))
        else:
            print("No such configuration property '%s'" % key)

    def simulate(self, state, simulator):
        print('\nConfiguration :')
        self._print_configuration(simulator)
        print('\nGame :')
        self._print_game(state)

        if not simulator:
            print('\nNo simulator found!\n')
            return
        player_num = state.player_num or config.player_num
        if player_num not in simulator.players_num:
            print("\nSimulator does not support '%d' players!\n" % player_num)
            return

        cards_num = len(state.cards)
        if cards_num not in simulator.cards_num:
            print("\nSimulator does not support '%d' cards!\n" % cards_num)
            return

        start = time.time()
        result = simulator.simulate(player_num, *state.cards)
        print('\nSimulation :')
        self._print_simulation(state, result)
        elapsed = time.time() - start
        print('\nSimulation finished in %.2f seconds\n' % elapsed)

    def _print_configuration(self, simulator):
        t = prettytable.PrettyTable(['key', 'value'])
        t.add_row(['sim_cycle', config.sim_cycle])
        if simulator:
            t.add_row(['simulator', simulator.name])
        print(t)

    def _print_simulation(self, state, sim_result):
        counts = (sim_result.win, sim_result.tie, sim_result.lose)
        header = ['Win', 'Tie', 'Loss']

        if isinstance(counts[0], int):
            pct = [count / sim_result.total * 100 for count in counts]
            row = ['%.2f%% (%d)' % (val, count) for val, count in zip(pct, counts)]
        else:
            pct = counts
            row = ['%.2f%%' % val for val in pct]

        if state.pot:
            win_chance = pct[0] / 100
            equity = bet.BetAdviser.get_equity(win_chance, state.pot)
            max_call = bet.BetAdviser.get_max_call(win_chance, state.pot)

            header.extend(['Equity', 'Max Call'])
            row.extend([str(round(equity, 2)), str(round(max_call, 2))])

        out_table = prettytable.PrettyTable(header)
        out_table.add_row(row)
        print(out_table)

        self._print_hand_stats(sim_result)

    def _print_hand_stats(self, sim_result):
        winning_hands = sim_result.sorted_winning_hands
        beating_hands = sim_result.sorted_beating_hands
        row_num = min(max(len(winning_hands), len(beating_hands)), config.hand_stats)
        if row_num:
            rows = [['-'] * 4 for _ in range(row_num)]
            self._fill_table(rows, winning_hands, row_num)
            self._fill_table(rows, beating_hands, row_num, 2)
            header = ['Winning Hand', 'Win Freq', 'Beating Hand', 'Beat Freq']
            stats_table = prettytable.PrettyTable(header)
            for row in rows:
                stats_table.add_row(row)
            print(stats_table)

    def _fill_table(self, rows, hands, row_num, offset=0):
        total = sum(count for _, count in hands)
        for i, (hand, count) in enumerate(hands[:row_num]):
            pct = count * 100 / total
            rows[i][offset] = hand.name
            rows[i][offset + 1] = '%.2f%%' % pct

    def _print_game(self, state):
        table = self._build_input_table(state)
        header, columns = [], []
        for col_name in InputTableColumn:
            col_data = table[col_name]
            if col_data:
                header.append(col_name.value)
                columns.append(col_data[::-1])

        input_table = prettytable.PrettyTable(header)
        for row in zip(*columns):
            input_table.add_row(row)
        print(input_table)

    def _build_input_table(self, state):
        table = collections.defaultdict(list)
        for state in state.history:
            cards = state.cards
            table[InputTableColumn.HOLE].append(' '.join(map(repr, cards[0:2])))
            if len(cards) >= 5:
                table[InputTableColumn.FLOP].append(' '.join(map(repr, cards[2:5])))
            if len(cards) >= 6:
                table[InputTableColumn.TURN].append(cards[5])
            if len(cards) == 7:
                table[InputTableColumn.RIVER].append(cards[6])

            player_num = state.player_num or config.player_num
            if player_num:
                if state.fold_num:
                    value = '%d(-%d)' % (player_num, state.fold_num)
                else:
                    value = '%d' % player_num
                table[InputTableColumn.PLAYER_NUM].append(value)

            if len(cards) >= 5:
                evaluator_manager = manager.EvaluatorManager()
                result = evaluator_manager.find_best_hand(cards)
                table[InputTableColumn.HAND].append(result.hand.name)

                table[InputTableColumn.RANKS].append(result.complement_ranks)

            if state.pot:
                table[InputTableColumn.POT].append(state.pot)
                if state.pot_growth:
                    pct_val = ((state.pot_growth - 1) * 100)
                    cell = '%.0f%%' % pct_val
                    table[InputTableColumn.POT_GROWTH].append(cell)

        row_num = max(len(col) for col in table.values())
        for col in table.values():
            if col:
                missing = row_num - len(col)
                if missing:
                    col.extend(['-'] * missing)
        return table

    def do_EOF(self, _):
        return True

    def emptyline(self):
        pass


def main():
    parser = argparse.ArgumentParser(description='Minsk Shell')
    parser.add_argument('-u', '--unicode', action='store_true', default=False)
    parser.add_argument('-t', '--sim-cycle', metavar='N', type=int,
                        default=config.sim_cycle)
    parser.add_argument('-x', '--hand-stats', metavar='N', type=int,
                        default=config.hand_stats)
    args = parser.parse_args()
    if args.unicode:
        model.enable_unicode = True
        config.sim_cycle = args.sim_cycle
    config.hand_stats = args.hand_stats

    MinskShell().cmdloop()


if __name__ == '__main__':
    main()

import argparse
import cmd
import enum
import time
import collections

import prettytable

import minsk.eval.bet as bet
import minsk.eval.manager as manager
import minsk.eval.simulation as simulation
import minsk.model as model
import minsk.parser as parser
import minsk.config as config


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
        if parser.LineParser.validate_line(line):
            try:
                return parser.LineParser.parse_history(line)
            except ValueError as e:
                print(str(e))
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
        if parser.LineParser.validate_line(line):
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

    def simulate(self, state, simulator):
        print('\nConfiguration :')
        self._print_configuration(simulator)
        print('\nGame :')
        self._print_game(state)

        if not simulator:
            print('\nNo simulator found!\n')
            return
        start = time.time()
        player_num = state.player_num or config.player_num
        result = simulator.simulate(player_num, *state.cards)
        print('\nSimulation :')
        self._print_simulation(state, result)
        elapsed = time.time() - start
        print('\nSimulation finished in %.2f seconds\n' % elapsed)

    def do_player_num(self, player_num):
        """set player number"""
        config.player_num = int(player_num)

    def do_sim_cycle(self, sim_cycle):
        """set simulation cycles number"""
        config.sim_cycle = float(sim_cycle)

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
        wining_hands = sim_result.get_wining_hands(3)
        beating_hands = sim_result.get_beating_hands(3)
        row_num = max(len(wining_hands), len(beating_hands))
        if row_num:
            rows = [['-'] * 4 for _ in range(row_num)]
            self._fill_table(rows, wining_hands)
            self._fill_table(rows, beating_hands, 2)
            header = ['Wining Hand', 'Win Freq', 'Beating Hand', 'Beat Freq']
            stats_table = prettytable.PrettyTable(header)
            for row in rows:
                stats_table.add_row(row)
            print(stats_table)

    def _fill_table(self, rows, hands, offset=0):
        total = sum(count for _, count in hands)
        for i, (hand, count) in enumerate(hands):
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

            if state.player_num:
                if state.fold_num:
                    value = '%d(-%d)' % (state.player_num, state.fold_num)
                else:
                    value = '%d' % state.player_num
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


def main():
    parser = argparse.ArgumentParser(description='Minsk Shell')
    parser.add_argument('-u', '--unicode', action='store_true', default=False)
    args = parser.parse_args()
    if args.unicode:
        model.enable_unicode = True
    MinskShell().cmdloop()


if __name__ == '__main__':
    main()

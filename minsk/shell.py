import argparse
import cmd
import enum
import time
import re
import collections

import prettytable

import minsk.eval.bet as bet
import minsk.eval.manager as manager
import minsk.eval.simulation as simulation
import minsk.eval.game as game
import minsk.model as model
import minsk.config as config


@enum.unique
class InputTableColumn(enum.Enum):
    HOLE = 'Hole'
    FLOP = 'Flop'
    TURN = 'Turn'
    RIVER = 'River'
    PLAYER_NUM = 'Player Num'
    HAND = 'Hand'
    RANKS = 'Ranks'
    POT = 'Pot'


NUM_RE = '\d+(\.(\d+)?)?'
CARD_RE = '([2-9tjqka][hscd])+'


class LineParser:
    @staticmethod
    def parse_state(line):
        tokens = line.split()
        cards = [token for token in tokens
                 if re.fullmatch(CARD_RE, token, re.IGNORECASE)]
        params = [token for token in tokens if re.fullmatch(NUM_RE, token)]
        joined = ''.join(cards)
        cards = zip(joined[::2], joined[1::2])
        pot, player_num = None, None
        for param in params:
            if '.' in param:
                pot = float(param)
            else:
                player_num = int(param)
                assert 2 <= player_num <= 10
        return game.GameState(model.Card.parse_cards(cards), player_num, pot)

    @classmethod
    def parse_history(cls, line):
        chunks = [token.strip() for token in line.split(';') if token.strip()]
        last_state = None
        for i in range(1, len(chunks) + 1):
            history_line = ' '.join(chunks[:i])
            state = cls.parse_state(history_line)
            if last_state:
                state.previous = last_state
            last_state = state
        return last_state

    @staticmethod
    def validate_line(line):
        line = line.replace(';', ' ')
        return all(re.fullmatch(NUM_RE, token) or
                   re.fullmatch(CARD_RE, token, re.IGNORECASE)
                   for token in line.split())


class MinskShell(cmd.Cmd):
    """Minsk shell"""
    prompt = '(minsk) '

    def __init__(self):
        super().__init__()
        self._sim_manager = simulation.SimulatorManager()

    def _parse_history(self, line):
        if LineParser.validate_line(line):
            try:
                return LineParser.parse_history(line)
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
        if LineParser.validate_line(line):
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
        self._print_configuration(simulator)
        self._print_input(state)

        if not simulator:
            print('\nNo simulator found!\n')
            return
        start = time.time()
        player_num = state.player_num or config.player_num
        result = simulator.simulate(player_num, *state.cards)
        self._print_output(state, result)
        elapsed = time.time() - start
        print('\nSimulation finished in %.2f seconds\n' % elapsed)

    def do_player_num(self, player_num):
        """set player number"""
        config.player_num = int(player_num)

    def do_sim_cycle(self, sim_cycle):
        """set simulation cycles number"""
        config.sim_cycle = float(sim_cycle)

    def _print_configuration(self, simulator):
        print('\nConfiguration :')
        t = prettytable.PrettyTable(['key', 'value'])
        t.add_row(['sim_cycle', config.sim_cycle])
        if simulator:
            t.add_row(['simulator', simulator.name])
        print(t)

    def _print_output(self, state, sim_result):
        print('\nOutput :')
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

    def _print_input(self, state):
        print('\nInput :')
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
                table[InputTableColumn.PLAYER_NUM].append(state.player_num)

            if len(cards) >= 5:
                evaluator_manager = manager.EvaluatorManager()
                result = evaluator_manager.find_best_hand(cards)
                table[InputTableColumn.HAND].append(result.hand.name)

                table[InputTableColumn.RANKS].append(result.complement_ranks)

            if state.pot:
                table[InputTableColumn.POT].append(state.pot)

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

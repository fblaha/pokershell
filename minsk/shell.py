import argparse
import cmd
import time
import re

import prettytable

import minsk.eval.bet as bet
import minsk.eval.manager as manager
import minsk.eval.simulation as simulation
import minsk.eval.game as game
import minsk.model as model
import minsk.config as config

NUM_RE = '\d+(\.(\d+)?)?'
CARD_RE = '([2-9tjqka][hscd])+'


class LineParser:
    @staticmethod
    def parse_state(line, default_player_num=None):
        tokens = line.split()
        cards = [token for token in tokens
                 if re.fullmatch(CARD_RE, token, re.IGNORECASE)]
        params = [token for token in tokens if re.fullmatch(NUM_RE, token)]
        joined = ''.join(cards)
        cards = zip(joined[::2], joined[1::2])
        pot = None
        player_num = default_player_num
        for param in params:
            if '.' in param:
                pot = float(param)
            else:
                player_num = int(param)
                assert 2 <= player_num <= 10
        return game.GameState(model.Card.parse_cards(cards), player_num, pot)

    @classmethod
    def parse_stack(cls, line, default_player_num=None):
        chunks = [token.strip() for token in line.split(';') if token.strip()]
        history = []
        for i in range(1, len(chunks) + 1):
            history_line = ' '.join(chunks[:i])
            state = cls.parse_state(history_line, default_player_num)
            history.append(state)
        game_stack = game.GameStack()
        for state in history:
            game_stack.add_state(state)
        return game_stack if game_stack.current else None

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

    def _parse_stack(self, line):
        if LineParser.validate_line(line):
            try:
                return LineParser.parse_stack(line, config.player_num)
            except ValueError as e:
                print(str(e))
        else:
            print("Invalid syntax '%s'" % line)

    def do_brute_force(self, cards):
        """evaluate hand - brute force"""
        stack = self._parse_stack(cards)
        if stack:
            simulator = simulation.BruteForceSimulator()
            self.simulate(stack, simulator)

    def do_eval(self, cards):
        """evaluate hand"""
        stack = self._parse_stack(cards)
        if stack:
            simulator = self._sim_manager.find_simulator(
                stack.current.player_num or config.player_num, *stack.current.cards)
            self.simulate(stack, simulator)

    def default(self, line):
        if LineParser.validate_line(line):
            self.do_eval(line)
        else:
            super().default(line)

    def do_monte_carlo(self, cards):
        """evaluate hand - monte carlo"""
        stack = self._parse_stack(cards)
        if stack:
            simulator = simulation.MonteCarloSimulator(
                config.sim_cycle)
            self.simulate(stack, simulator)

    def do_look_up(self, cards):
        """evaluate hand - loop up"""
        stack = self._parse_stack(cards)
        if stack:
            simulator = simulation.LookUpSimulator()
            self.simulate(stack, simulator)

    def simulate(self, stack, simulator):
        self._print_configuration(simulator)
        current = stack.current
        self._print_input(stack)

        if not simulator:
            print('\nNo simulator found!\n')
            return
        start = time.time()
        player_num = current.player_num or config.player_num
        result = simulator.simulate(player_num, *current.cards)
        self._print_output(current, result)
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
            pct = list(map(lambda x: x / sim_result.total * 100, counts))
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

    def _print_input(self, stack):
        current = stack.current
        cards = current.cards
        print('\nInput :')
        columns = ['Hole']
        row = [' '.join(map(repr, cards[0:2]))]
        if len(cards) >= 5:
            columns.append('Flop')
            row.append(' '.join(map(repr, cards[2:5])))
        if len(cards) >= 6:
            columns.append('Turn')
            row.append(cards[5])
        if len(cards) == 7:
            columns.append('River')
            row.append(cards[6])

        columns.append('Player Num')
        row.append(current.player_num or config.player_num)

        evaluator_manager = manager.EvaluatorManager()
        if len(cards) >= 5:
            result = evaluator_manager.find_best_hand(cards)
            columns.append('Hand')
            row.append(result.hand.name)

            columns.append('Ranks')
            row.append(' '.join(map(repr, result.complement_ranks)))

        if current.pot:
            columns.append('Pot')
            row.append(current.pot)

        input_table = prettytable.PrettyTable(columns)
        input_table.add_row(row)
        print(input_table)

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

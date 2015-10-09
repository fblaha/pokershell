import cmd
import time
import re
import collections

import prettytable

import minsk.eval.bet as bet
import minsk.eval.manager as manager
import minsk.eval.simulation as simulation
import minsk.model as model
import minsk.config as config

ParsedLine = collections.namedtuple('ParsedLine', 'cards player_num pot')

NUM_RE = '\d+(\.\d+)?'


class MinskShell(cmd.Cmd):
    """Minsk shell"""
    prompt = '(minsk) '

    def do_bf(self, cards):
        """evaluate hand - brute force"""
        parsed = self._parse_line(cards)
        simulator = simulation.BruteForceSimulator()
        self.simulate(parsed, simulator)

    def do_e(self, cards):
        """evaluate hand"""
        parsed = self._parse_line(cards)
        manager = simulation.SimulatorManager()
        with config.with_config(_player_num=parsed.player_num):
            simulator = manager.find_simulator(*parsed.cards)
            self.simulate(parsed, simulator)

    def _parse_line(self, line):
        tokens = line.split()
        player_num = config.player_num
        cards = [token for token in tokens if not re.fullmatch(NUM_RE, token)]
        params = [token for token in tokens if re.fullmatch(NUM_RE, token)]
        joined = ''.join(cards)
        cards = zip(joined[::2], joined[1::2])
        pot = None
        if params:
            player_num = int(params[0])
            if len(params) >= 2:
                pot = float(params[1])
        return ParsedLine(model.Card.parse_cards(cards), player_num, pot)

    def do_mc(self, cards):
        """evaluate hand - monte carlo"""
        parsed = self._parse_line(cards)
        with config.with_config(_player_num=parsed.player_num):
            simulator = simulation.MonteCarloSimulator(
                config.player_num, config.sim_cycles)
            self.simulate(parsed, simulator)

    def do_lu(self, cards):
        """evaluate hand - loop up"""
        parsed = self._parse_line(cards)
        with config.with_config(_player_num=parsed.player_num):
            simulator = simulation.LookUpSimulator(config.player_num)
            self.simulate(parsed, simulator)

    def simulate(self, parsed_line, simulator):
        self.print_configuration(simulator)
        self.print_input(parsed_line)
        if not simulator:
            print('\nNo simulator found!\n')
            return
        start = time.time()
        result = simulator.simulate(*parsed_line.cards)
        self.print_output(parsed_line, result)
        elapsed = time.time() - start
        print('\nSimulation finished in %.2f seconds\n' % elapsed)

    def do_player_num(self, player_num):
        """set player number"""
        config.player_num = int(player_num)

    def do_sim_cycles(self, sim_cycles):
        """set simulation cycles number"""
        config.sim_cycles = int(sim_cycles)

    def print_configuration(self, simulator):
        print('\nConfiguration :')
        t = prettytable.PrettyTable(['key', 'value'])
        for name in ('player_num', 'sim_cycles'):
            t.add_row([name, getattr(config, name)])
        if simulator:
            t.add_row(['simulator', simulator.name])
        print(t)

    def print_output(self, parsed_line, result):
        print('\nOutput :')
        pct_table = prettytable.PrettyTable(['Win', 'Tie', 'Loss'])

        if isinstance(result[0], int):
            total = sum(result)
            raw_pct = list(map(lambda x: x / total * 100, result))
            pct_table.add_row(result)
        else:
            raw_pct = result

        result_pct = list(map(lambda x: str(round(x, 2)) + '%', raw_pct))
        pct_table.add_row(result_pct)
        print(pct_table)
        if parsed_line.pot:
            bet_table = prettytable.PrettyTable(['Max Bet'])
            win_chance = raw_pct[0] / 100
            max_bet = bet.BetAdviser.get_max_bet(win_chance, parsed_line.pot,
                                                 len(parsed_line.cards))
            bet_table.add_row([str(round(max_bet, 2))])
            print(bet_table)

    def print_input(self, parsed_line):
        cards = parsed_line.cards
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
        evaluator_manager = manager.EvaluatorManager()
        if len(cards) >= 5:
            result = evaluator_manager.find_best_hand(cards)
            columns.append('Hand')
            row.append(result.hand.name)

            columns.append('Ranks')
            row.append(' '.join(map(repr, result.complement_ranks)))

        if parsed_line.pot:
            columns.append('Pot')
            row.append(parsed_line.pot)

        input_table = prettytable.PrettyTable(columns)
        input_table.add_row(row)
        print(input_table)

    def do_EOF(self, line):
        return True


def main():
    MinskShell().cmdloop()


if __name__ == '__main__':
    main()

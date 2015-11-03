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
        return game.GameState(model.Card.parse_cards(cards), player_num, pot)

    @classmethod
    def parse_history(cls, line, default_player_num=None):
        chunks = [token.strip() for token in line.split(';') if token.strip()]
        history = []
        for i in range(1, len(chunks) + 1):
            history_line = ' '.join(chunks[:i])
            state = cls.parse_state(history_line, default_player_num)
            history.append(state)
        return history

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
        self._game_stack = game.GameStack()

    def _parse_line(self, line):
        if LineParser.validate_line(line):
            try:
                return LineParser.parse_history(line, config.player_num)[-1]
            except ValueError as e:
                print(str(e))
        else:
            print("Invalid syntax '%s'" % line)

    def do_brute_force(self, cards):
        """evaluate hand - brute force"""
        parsed = self._parse_line(cards)
        if parsed:
            simulator = simulation.BruteForceSimulator()
            self.simulate(parsed, simulator)

    def do_eval(self, cards):
        """evaluate hand"""
        parsed = self._parse_line(cards)
        if parsed:
            with config.with_config(_player_num=parsed.player_num):
                simulator = self._sim_manager.find_simulator(*parsed.cards)
                self.simulate(parsed, simulator)

    def default(self, line):
        if LineParser.validate_line(line):
            self.do_eval(line)
        else:
            super().default(line)

    def do_monte_carlo(self, cards):
        """evaluate hand - monte carlo"""
        parsed = self._parse_line(cards)
        if parsed:
            with config.with_config(_player_num=parsed.player_num):
                simulator = simulation.MonteCarloSimulator(
                    config.player_num, config.sim_cycle)
                self.simulate(parsed, simulator)

    def do_look_up(self, cards):
        """evaluate hand - loop up"""
        parsed = self._parse_line(cards)
        if parsed:
            with config.with_config(_player_num=parsed.player_num):
                simulator = simulation.LookUpSimulator(config.player_num)
                self.simulate(parsed, simulator)

    def simulate(self, parsed_line, simulator):
        self.print_configuration(simulator)
        self.print_input(parsed_line)

        self._game_stack.add_state(parsed_line)

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

    def do_sim_cycle(self, sim_cycle):
        """set simulation cycles number"""
        config.sim_cycle = float(sim_cycle)

    def print_configuration(self, simulator):
        print('\nConfiguration :')
        t = prettytable.PrettyTable(['key', 'value'])
        for name in ('player_num', 'sim_cycle'):
            t.add_row([name, getattr(config, name)])
        if simulator:
            t.add_row(['simulator', simulator.name])
        print(t)

    def print_output(self, parsed_line, sim_result):
        print('\nOutput :')
        counts = (sim_result.win, sim_result.tie, sim_result.lose)
        pct_table = prettytable.PrettyTable(['Win', 'Tie', 'Loss'])

        if isinstance(counts[0], int):
            raw_pct = list(map(lambda x: x / sim_result.total * 100, counts))
            pct_table.add_row(counts)
        else:
            raw_pct = counts

        result_pct = list(map(lambda x: str(round(x, 2)) + '%', raw_pct))
        pct_table.add_row(result_pct)
        print(pct_table)
        if parsed_line.pot:
            win_chance = raw_pct[0] / 100
            max_bet = bet.BetAdviser.get_max_bet(win_chance, parsed_line.pot)
            bet_table = prettytable.PrettyTable(['Max Bet'])
            bet_table.add_row([str(round(max_bet, 2))])
            print(bet_table)

        wining_hands = sim_result.get_wining_hands(3)
        beating_hands = sim_result.get_beating_hands(3)
        self._print_hand_stats(wining_hands, 'Wining Hand')
        self._print_hand_stats(beating_hands, 'Beating Hand')

    def _print_hand_stats(self, hand_stats, label):
        if hand_stats:
            danger_table = prettytable.PrettyTable([label, 'Frequency'])
            total = sum(count for _, count in hand_stats)
            for hand, count in hand_stats:
                pct = count * 100 / total
                danger_table.add_row([hand.name, str(round(pct, 2)) + '%'])
            print(danger_table)

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

    def do_EOF(self, _):
        return True


def main():
    MinskShell().cmdloop()


if __name__ == '__main__':
    main()

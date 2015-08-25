import cmd

import prettytable

import minsk.eval.manager as manager
import minsk.eval.simulation as simulation
import minsk.model as model


class MinskShell(cmd.Cmd):
    """Minsk shell"""
    prompt = '(minsk) '

    def do_eval(self, cards):
        """evaluate hand"""
        simulator = simulation.BruteForceSimulator()
        cards = model.Card.parse_cards(cards)

        self.print_input(cards)
        result = simulator.simulate(*cards)
        self.print_output(result)

    def print_output(self, result):
        print('\nOutput :')
        total = sum(result)
        result_pct = list(map(lambda x: str(round(x / total * 100)) + '%', result))
        result_table = prettytable.PrettyTable(['Win', 'Tie', 'Loss'])
        result_table.add_row(result_pct)
        result_table.add_row(result)
        print(result_table)

    def print_input(self, cards):
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
        hand = evaluator_manager.find_best_hand(*cards)
        columns.append('Hand')
        row.append(hand[0].name)

        columns.append('Ranks')
        row.append(' '.join(map(repr, hand[1])))

        input_table = prettytable.PrettyTable(columns)
        input_table.add_row(row)
        print(input_table)

    def do_EOF(self, line):
        return True


def main():
    MinskShell().cmdloop()


if __name__ == '__main__':
    main()

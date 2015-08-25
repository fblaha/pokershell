import cmd

import prettytable

import minsk.eval.simulation as simulation
import minsk.model as model


class MinskShell(cmd.Cmd):
    """Minsk shell"""
    prompt = '(minsk) '

    def do_eval(self, cards):
        """evaluate hand"""
        simulator = simulation.BruteForceSimulator()
        cards = model.Card.parse_cards(cards)

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

        input_table = prettytable.PrettyTable(columns)
        input_table.add_row(row)
        print(input_table)

        print('\nOutput :')
        result = simulator.simulate(*cards)
        total = sum(result)
        result_pct = list(map(lambda x: str(round(x / total * 100)) + '%', result))

        result_table = prettytable.PrettyTable(["Win", "Tie", "Loss"])

        result_table.add_row(result_pct)
        result_table.add_row(result)
        print(result_table)

    def do_EOF(self, line):
        return True


def main():
    MinskShell().cmdloop()


if __name__ == '__main__':
    main()

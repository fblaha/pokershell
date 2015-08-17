import logging

from cliff.command import Command

from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator


class Hand(Command):
    "A simple command that prints a message."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Hand, self).get_parser(prog_name)
        parser.add_argument('first')
        parser.add_argument('second')
        return parser

    def take_action(self, parsed_args):
        hole = [Card(2, 1), Card(2, 2)]
        board = []
        score = HandEvaluator.evaluate_hand(hole, board)
        self.app.stdout.write(score)

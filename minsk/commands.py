import logging

from cliff.command import Command

from minsk.model import Card


class Hand(Command):
    """A simple command that prints a message."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Hand, self).get_parser(prog_name)
        parser.add_argument('first')
        parser.add_argument('second')
        return parser

    def take_action(self, parsed_args):
        card1 = Card.parse(parsed_args.first)
        card2 = Card.parse(parsed_args.second)
        self.app.stdout.write(card1)
        self.app.stdout.write(card2)

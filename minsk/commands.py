import logging

from cliff.command import Command


class Simple(Command):
    "A simple command that prints a message."

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        self.app.stdout.write('hi!\n')

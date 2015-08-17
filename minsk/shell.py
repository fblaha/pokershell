import sys

from cliff.app import App
from cliff.commandmanager import CommandManager


class MinksShell(App):
    NAME = 'minsk'

    def __init__(self):
        super(MinksShell, self).__init__(
            description='Minsk Shell',
            version='0.1',
            command_manager=CommandManager('minsk.commands'),
            deferred_help=True,
        )
        self.prompt = 'x'

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    return MinksShell().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

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


def main(argv=sys.argv[1:]):
    return MinksShell().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

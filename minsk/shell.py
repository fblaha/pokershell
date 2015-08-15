import cmd
import sys


class MinskShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.intro = 'Welcome to the Minsk shell.   Type help or ? to list commands.\n'
        self.prompt = '(minsk) '

    def do_hello(self, arg):
        """Just hello"""
        print("hello again", arg, "!")

    def do_quit(self, arg):
        """Quit shell"""
        sys.exit(1)

    # shortcuts
    do_q = do_quit


if __name__ == '__main__':
    MinskShell().cmdloop()

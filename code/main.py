"""

Allowed commands:

+   ``echo input_file output_file``

    Copies text from ``input_file`` to ``output_file``.
"""

import sys
import forwardchaining
import inspect


class Environment:
    """ Helper for writing LaTeX environment.
    """

    def __init__(self, name, *args):
        self.name = name
        self.content = []
        self.args = args

    def __str__(self):
        return '\\begin{{{0}}}{2}\n{1}\n\\end{{{0}}}'.format(
                self.name, ''.join(self.content),
                ''.join('{{{0}}}'.format(arg) for arg in self.args))

    def append(self, frmt, *args, **kwargs):
        """ Appends string to content.
        """
        if args or kwargs:
            self.content.append(frmt.format(*args, **kwargs))
        else:
            self.content.append(frmt)


def usage():
    """ Print usage message.
    """
    print(__doc__)


def echo(input_file, output_file):
    """ Copy text from input file to output.
    """
    print(input_file, 'to', output_file)
    with open(input_file) as fin:
        with open(output_file, 'w') as fout:
            env = Environment('verbatim')
            for i, line in enumerate(fin):
                env.append('{0:3}: {1}', i+1, line)
            fout.write(str(env))


def show_source(input_file, output_file):
    """ Shows information about object defined in input file.
    """
    expression = open(input_file).read().strip()
    env = Environment('minted', 'python')
    env.append(inspect.getsource(eval(expression)))
    with open(output_file, 'w') as fout:
        fout.write(str(env))


def forward_chaining(input_file, output_file):
    """ Tries to solve production system, by using forward chaining.
    """
    with open(input_file) as fin:
        with open(output_file, 'w') as fout:
            solver = forwardchaining.ForwardChaining(fin, fout)
            solver.print_input()
            solver.solve()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
    elif sys.argv[1] == 'echo':
        echo(*sys.argv[2:])
    elif sys.argv[1] == 'fc':
        forward_chaining(*sys.argv[2:])
    elif sys.argv[1] == 'source':
        show_source(*sys.argv[2:])

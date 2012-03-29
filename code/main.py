"""

Allowed commands:

+   ``echo input_file output_file``

    Copies text from ``input_file`` to ``output_file``.
"""

import sys
import forwardchaining
import backwardchaining
import inspect
import utils
import os


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
            env = utils.Environment('verbatim')
            for i, line in enumerate(fin):
                env.append('{0:3}: {1}', i+1, line)
            fout.write(str(env))


def graph(input_file, output_file, invoke_counter, label, caption):
    """ Generates image from dot file.
    """

    image_file = 'dist/document-graph-{0}.png'.format(invoke_counter)
    command = 'dot -q2 -Tpng -o "{0}" "{1}"'.format(
            image_file, input_file)
    os.system(command)
    with open(output_file, 'w') as fout:
        env = utils.Environment('figure', ('H', True))
        env.append('\\centering\n')
        env.append('\\includegraphics[scale=0.7]{{{0}}}\n', image_file)
        env.append('\\caption{{{0}}}\n'.format(caption))
        env.append('\\label{{{0}}}\n'.format(label))
        fout.write(str(env))


def show_source(input_file, output_file):
    """ Shows information about object defined in input file.
    """
    expression = open(input_file).read().strip()
    env = utils.MintedEnvironment('python')
    env.append(inspect.getsource(eval(expression)))
    with open(output_file, 'w') as fout:
        fout.write('Objekto \\verb|{0}| kodas:'.format(expression))
        fout.write(str(env))


def show_structure(input_file, output_file):
    """ Shows program structure.
    """

    env = utils.EnumerateEnvironment()
    modules = [utils, forwardchaining, backwardchaining]
    for module in modules:
        innerenv = utils.EnumerateEnvironment()
        for name, cls in inspect.getmembers(module, inspect.isclass):
            innerenv.append(
                    '\\verb|{0}|\n\n{1}\n', name, inspect.getdoc(cls))
        env.append('Modulyje \\verb|{0}| apibrėžtos klasės:\n{1}',
                module.__name__, innerenv)

    with open(output_file, 'w') as fp:
        fp.write(str(env))


def solve(input_file, fout, solver, invoke_counter):
    """ Tries to solve production system, by using solver.
    """

    env = utils.MintedEnvironment('text')
    env.append(open(input_file).read())
    fout.write('\n\n\\subsubsection{{Pradinių duomenų failo turinys}}\n\n')
    fout.write(str(env))
    fout.write('\n\n')

    fout.write('\n\n\\subsubsection{{Programos pradinių '
               'duomenų interpretacija}}\n\n')
    solver.print_input()
    solver.save_raw_input('dist/input.{0}.txt'.format(invoke_counter))

    fout.write('\n\n\\subsubsection{{Programos išvestis}}\n\n')
    solver.solve()
    solver.print_graph(invoke_counter)


def forward_chaining(input_file, output_file, invoke_counter):
    """ Tries to solve production system, by using forward chaining.
    """
    with open(input_file) as fin:
        with open(output_file, 'w') as fout:
            solver = forwardchaining.ForwardChaining(fin, fout)
            solve(input_file, fout, solver, invoke_counter)


def backward_chaining(fin, fout, input_file, output_file, invoke_counter):
    """ Tries to solve production system, by using backward chaining.
    """
    with open(input_file) as fin:
        with open(output_file, 'w') as fout:
            solver = backwardchaining.BackwardChaining(fin, fout)
            solve(input_file, fout, solver, invoke_counter)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
    else:
        args = sys.argv[1]
        if '|' in args:
            args = args.split('|')
            program = args[0]
        else:
            program = args
            args = [args]

        if program == 'echo':
            echo(*sys.argv[2:4])
        elif program == 'graph':
            graph(*(sys.argv[2:5] + args[1:]))
        elif program == 'fc':
            forward_chaining(*sys.argv[2:5])
        elif program == 'bc':
            backward_chaining(*sys.argv[2:5])
        elif program == 'source':
            show_source(*sys.argv[2:4])
        elif program == 'structure':
            show_structure(*sys.argv[2:4])

def math(string):
    """ Returns string converted into math mode.
    """
    return '${0}$'.format(string)


def uncomment(string):
    """ Removes comment.
    """
    string = ''.join(string.split())
    comment = string.find('#')
    if comment == -1:
        return string
    else:
        return string[:comment]


class Environment:
    """ Pagalbinė klasė LaTeX aplinkų kūrimui.
    """

    def __init__(self, name, *args):
        self.name = name
        self.content = []
        self.args = args

    def __str__(self):
        return '\\begin{{{0}}}{2}\n{1}\n\\end{{{0}}}'.format(
                self.name, ''.join(self.content),
                ''.join(
                    ('[{0}]' if angle_bracket else '{{{0}}}').format(arg)
                    for arg, angle_bracket in self.args))

    def append(self, frmt, *args, **kwargs):
        """ Appends string to content.
        """
        if args or kwargs:
            self.content.append(frmt.format(*args, **kwargs))
        else:
            self.content.append(frmt)


class EnumerateEnvironment(Environment):
    """ Pagalbinė klasė LaTeX enumerate aplinkų kūrimui.
    """

    def __init__(self):
        super(EnumerateEnvironment, self).__init__('enumerate')

    def append(self, frmt, *args, **kwargs):
        """ Appends string to content.
        """
        super(EnumerateEnvironment, self).append(
                '\n\n\\item ' + frmt, *args, **kwargs)

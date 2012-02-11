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


class Rule:
    """ Išvedimo taisyklė.
    """

    def __init__(self, result, data, index=None):
        self.result = result
        self.data = set(data)
        self.index = index

    def __str__(self):
        if self.index is None:
            return math('{0} \\to {1}'.format(
                ','.join(self.data), self.result))
        else:
            return math('{2}: {0} \\to {1}'.format(
                ','.join(self.data), self.result, self.index))

    @classmethod
    def from_string(self, string):
        """ Sukuria taisyklės objektą iš simbolių eilutės.
        """
        string = uncomment(string)
        if len(string) < 2:
            return None
        else:
            return Rule(string[-1], string[0:-1])


class ProductionSystem:
    """ Produkcijų sistema.
    """

    def __init__(self, rules, facts, goal):
        self.rules = rules
        self.facts = facts
        self.goal = goal

    @classmethod
    def from_file(self, file):
        """ Sukuria produkcijų sistemos objektą iš failo tipo objekto.
        """
        lines = iter(file)

        rules = []
        for line in lines:
            rule = Rule.from_string(line)
            if rule is None:
                if rules:
                    break
            else:
                rules.append(rule)
                rule.index = 'R{0}'.format(len(rules))
        else:
            raise Exception('Nepavyko nuskaityti duomenų: failo pabaiga.')

        for line in lines:
            facts = uncomment(line)
            if facts:
                break
        else:
            raise Exception('Nepavyko nuskaityti duomenų: failo pabaiga.')

        for line in lines:
            goal = uncomment(line)
            if goal:
                if len(goal) == 1:
                    break
                else:
                    raise Exception(
                            'Nepavyko nuskaityti duomenų: blogas tikslas.')
        else:
            raise Exception('Nepavyko nuskaityti duomenų: failo pabaiga.')

        return ProductionSystem(rules, set(facts), goal)

    def __str__(self):
        content = ['Taisyklės:']
        for rule in self.rules:
            content.append(str(rule))
        content.append('Faktai: {0}.'.format(', '.join(self.facts)))
        content.append('Tikslas: {0}.'.format(self.goal))
        return '\n\n'.join(content)


class ForwardChaining:
    """ Klasė, kuri išveda produkcijas pasinaudodama tiesinio išvedimo
    metodu.
    """

    def __init__(self, fin, fout):
        self.production_system = ProductionSystem.from_file(fin)
        self.file = fout
        self.solution = []

    def print_input(self):
        """ Į rezultatų failą išveda gautus pradinius duomenis.
        """
        self.file.write(str(self.production_system))
        self.file.write('\n')

    def drop_improper(self, rules, facts):
        """ Išmeta taisykles, kurių rezultatas jau yra tarp faktų.
        """
        drop = []
        for i, rule in enumerate(rules):
            if rule.result in facts:
                drop.append(i)
        for index in reversed(drop):
            del rules[index]

    def recursion(self, rules, facts, goal):
        """ Sprendžia rekursyviai.
        """
        if goal in facts:
            return True
        self.drop_improper(rules, facts)
        for i, rule in enumerate(rules):
            if rule.data.issubset(facts):
                facts.add(rule.result)
                self.solution.append(rule)
                del rules[i]
                return self.recursion(rules, facts, goal)
        return False

    def solve(self):
        """ Bando surasti tikslą naudodama tiesioginį išvedimą.
        """

        if self.recursion(
                self.production_system.rules,
                self.production_system.facts,
                self.production_system.goal,):
            self.file.write('\nAtsakymas: ')
            if self.solution:
                self.file.write(math(
                    ', '.join(rule.index for rule in self.solution)
                    ))
            else:
                self.file.write(math('\\emptyset'))
        else:
            self.file.write('\nIšvedimas neegzistuoja.')
        self.file.write('\n')
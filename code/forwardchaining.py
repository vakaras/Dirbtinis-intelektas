import utils


class Rule:
    """ Išvedimo taisyklė.
    """

    def __init__(self, result, premises, index=None):
        self.result = result
        self.premises = set(premises)
        self.index = index

    def __str__(self):
        if self.index is None:
            return utils.math('{0} \\to {1}'.format(
                ','.join(self.premises), self.result))
        else:
            return utils.math('{2}: {0} \\to {1}'.format(
                ','.join(self.premises), self.result, self.index))

    @classmethod
    def from_string(self, string):
        """ Sukuria taisyklės objektą iš simbolių eilutės.
        """
        string = utils.uncomment(string)
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
                rule.index = 'R_{0}'.format(len(rules))
        else:
            raise Exception('Nepavyko nuskaityti duomenų: failo pabaiga.')

        for line in lines:
            facts = utils.uncomment(line)
            if facts:
                break
        else:
            raise Exception('Nepavyko nuskaityti duomenų: failo pabaiga.')

        for line in lines:
            goal = utils.uncomment(line)
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

    def print_graph(self, title='Semantinis grafas'):
        """ Į rezultatų failą išveda gautą grafą.
        """
        env = utils.Environment('dot2tex', ('mathmode', True))
        env.append('digraph G {\n')
        rules = set()
        facts = set()
        def add_rule(rule):
            if rule.index not in rules:
                env.append('node [shape="circle"]; {0};\n', rule.index)
                rules.add(rule.index)
        def add_fact(fact):
            if fact not in facts:
                env.append('node [shape="box"]; {0};\n', fact)
                facts.add(fact)
        for fact in self.production_system.facts:
            add_fact(fact)
        for rule in self.solution:
            add_rule(rule)
            add_fact(rule.result)
            for fact in rule.premises:
                env.append('{0} -> {1};\n', fact, rule.index)
            env.append('{0} -> {1};\n', rule.index, rule.result)
        env.append('}\n')
        self.file.write('\n\n{0}:\n'.format(title))
        self.file.write(str(env))

    def drop_improper(self, rules, premises):
        """ Išmeta taisykles, kurių rezultatas jau yra tarp faktų.
        """
        drop = []
        for i, rule in enumerate(rules):
            if rule.result in premises:
                drop.append(i)
        for index in reversed(drop):
            del rules[index]

    def recursion(self, rules, premises, goal):
        """ Sprendžia rekursyviai.
        """
        self.print_graph(
                'Grafas po {0} iteracijų'.format(len(self.solution)))
        if goal in premises:
            return True
        self.drop_improper(rules, premises)
        for i, rule in enumerate(rules):
            if rule.premises.issubset(premises):
                premises.add(rule.result)
                self.solution.append(rule)
                del rules[i]
                return self.recursion(rules, premises, goal)
        return False

    def solve(self):
        """ Bando surasti tikslą naudodama tiesioginį išvedimą.
        """

        if self.recursion(
                self.production_system.rules[:],
                self.production_system.facts.copy(),
                self.production_system.goal,):
            self.file.write('\n\nAtsakymas: ')
            if self.solution:
                self.file.write(utils.math(
                    ', '.join(rule.index for rule in self.solution)
                    ))
            else:
                self.file.write(utils.math('\\emptyset'))
        else:
            self.file.write('\n\nIšvedimas neegzistuoja.')
        self.file.write('\n')

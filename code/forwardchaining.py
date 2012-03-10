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

        rules = set()
        for line in lines:
            rule = Rule.from_string(line)
            if rule is None:
                if rules:
                    break
            else:
                rules.add(rule)
                rule.index = 'R{0}'.format(len(rules))
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
        env = utils.Environment('pythonaienv', ('graph', True))
        env.append('digraph G {\n')
        env.append('node [fixedsize="true", fontsize=11, '
                   'width="0.3cm", height="0.3cm"];\n')
        env.append('edge [arrowsize="1.5"];\n')
        node = 'node [shape="{0}"]; {1}; \n'
        rules = set()
        facts = set()
        def add_rule(rule):
            if rule.index not in rules:
                env.append(node, 'circle', rule.index)
                rules.add(rule.index)
        def add_fact(fact):
            if fact not in facts:
                env.append(node, 'box', fact)
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

    def recursion(self, rules, facts, goal):
        """ Sprendžia rekursyviai.
        """
        if goal in facts:               # \ref{fc:pseudo:while_condition}
            self.trace.append('Rąstas tikslas.')
            return True
        for rule in rules:
                                        # \ref{fc:pseudo:while_condition}
                                        # \ref{fc:pseudo:next_rule}
            if (rule.premises.issubset(facts) and
                    rule.result not in facts):
                                        # \ref{fc:pseudo:if_condition}
                facts.add(rule.result)  # \ref{fc:pseudo:add_fact}
                self.trace.append(
                        'Pritaikome taisyklę: {0}. '
                        'Faktų aibė po pritaikymo: $\\{{{1}\\}}$.',
                        rule, ', '.join(facts))
                self.solution.append(rule)
                                        # \ref{fc:pseudo:add_rule}
                return self.recursion(rules - {rule}, facts, goal)
                                        # \ref{fc:pseudo:start}
        return False

    def solve(self):
        """ Bando surasti tikslą naudodama tiesioginį išvedimą.
        """

        self.trace = utils.EnumerateEnvironment()
        if self.recursion(
                self.production_system.rules,
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
        self.file.write('\n\nAtliktų veiksmų seka:')
        self.file.write(str(self.trace))

import utils


class Rule:
    """ Išvedimo taisyklė.
    """

    def __init__(self, result, premises, index=None):
        self.result = result
        self.premises = list(premises)
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

    @classmethod
    def from_string_new(self, string):
        """ Sukuria taisyklės objektą iš simbolių eilutės.
        """
        for i in range(1, 4):
            if string.startswith('{0}. '.format(i)):
                return None
        string = utils.uncomment(string)
        if len(string) < 2:
            return None
        else:
            return Rule(string[0], string[1:])

class ProductionSystem:
    """ Produkcijų sistema. (Trejetas <R, F, G>.)
    """

    def __init__(self, rules, facts, goal):
        self.rules = rules
        self.facts = facts
        self.goal = goal

    @classmethod
    def from_file(self, file):
        """ Sukuria produkcijų sistemos objektą iš failo tipo objekto.
        """
        file.readline()                 # Skip empty line.
        if file.readline().startswith('# Vytauto Astrausko failas.'):
            return self.from_file_new(file)
        else:
            return self.from_file_old(file)

    @classmethod
    def from_file_new(self, file):
        """ Sukuria produkcijų sistemos objektą iš failo tipo objekto.
        """
        lines = iter(file)

        rules = list()
        for line in lines:
            rule = Rule.from_string_new(line)
            if rule is None:
                if rules:
                    break
            else:
                rules.append(rule)
                rule.index = 'R{0}'.format(len(rules))
        else:
            raise Exception('Nepavyko nuskaityti duomenų: failo pabaiga.')

        for line in lines:
            if line.startswith('2. '):
                continue
            facts = utils.uncomment(line)
            if facts:
                break
        else:
            raise Exception('Nepavyko nuskaityti duomenų: failo pabaiga.')

        for line in lines:
            if line.startswith('3. '):
                continue
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

    @classmethod
    def from_file_old(self, file):
        """ Sukuria produkcijų sistemos objektą iš failo tipo objekto.
        """
        lines = iter(file)

        rules = list()
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


class Solver:
    """ Bazinė klasė atsakinga už produkcijų išvedimą.
    """

    def __init__(self, fin, fout, invoke_counter):
        self.production_system = ProductionSystem.from_file(fin)
        self.file = fout
        self.solution = []
        self.invoke_counter = invoke_counter

    def print_input(self):
        """ Į rezultatų failą išveda gautus pradinius duomenis.
        """
        self.file.write(str(self.production_system))
        self.file.write('\n')

    def save_raw_input(self, filename):
        """ Sukuria pradinių duomenų failą.
        """
        with open(filename, 'w') as fout:
            def write(template='', *args):
                template += '\n'
                fout.write(template.format(*args))
            write('# Vytauto Astrausko failas.')
            write('1. Taisyklės.')
            for rule in self.production_system.rules:
                write('{0}{1:<39}# {2}: {3} → {4}',
                      rule.result, ''.join(rule.premises),
                      rule.index, ', '.join(rule.premises), rule.result)
            write()
            write('2. Faktai.')
            write(''.join(self.production_system.facts))
            write()
            write('3. Tikslas.')
            write(self.production_system.goal)

    def print_graph(self, invoke_counter):
        """ Į rezultatų failą išveda gautą grafą.
        """
        label = 'graph:{0}'.format(invoke_counter)
        env = utils.Environment('pythonaienv',
                ('graph|{0}|Semantinis grafas.'.format(label), True))
        env.append(
                'digraph G {{ // graph-invoke-print-graph: {0} \n',
                self.invoke_counter)
        env.append('node [fixedsize="true", fontsize=11, '
                   'width="0.3cm", height="0.3cm"];\n')
        env.append('edge [arrowsize="1.5"];\n')
        node = 'node [shape="{0}"]; {1}; \n'
        rules = set()
        facts = set()
        edges = set()
        def add_rule(rule):
            if rule.index not in rules:
                env.append(node, 'circle', rule.index)
                rules.add(rule.index)
        def add_fact(fact):
            if fact not in facts:
                env.append(node, 'box', fact)
                facts.add(fact)
        def add_edge(a, b):
            if (a, b) not in edges:
                env.append('{0} -> {1};\n', a, b)
                edges.add((a, b))
        for fact in self.production_system.facts:
            add_fact(fact)
        for rule in self.solution:
            add_rule(rule)
            add_fact(rule.result)
            for fact in rule.premises:
                add_edge(fact, rule.index)
                #env.append('{0} -> {1};\n', fact, rule.index)
            add_edge(rule.index, rule.result)
            #env.append('{0} -> {1};\n', rule.index, rule.result)
        env.append('}\n')
        self.file.write((
            '\n\nSemantinis grafas pateiktas \\ref{{{0}}} '
            'paveikslėlyje.\n').format(label))
        self.file.write(str(env))

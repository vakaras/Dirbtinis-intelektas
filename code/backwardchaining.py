import utils

from common import Rule, ProductionSystem, Solver


class BackwardChaining(Solver):
    """ Klasė, kurios objektai išveda produkcijas pasinaudodami
    atbulinio išvedimo metodu.
    """

    def recursion(self, rules, goal, goals):
        """ Sprendžia rekursyviai.
        """
        goal_id = self.last_fact_id
        space = '→' * len(goals)
        if goal in self.facts:
                                        # \ref{bc:pseudo:goal_in_facts}
            self.trace.append('{1} Tikslas {0} yra faktas. (Duota.)',
                    goal, space)
            self.add_text("duota")
            self.add_edge(self.last_text_id, goal_id)
            return []                   # \ref{bc:pseudo:emptyset}
        if goal in self.new_facts:
                                        # \ref{bc:pseudo:goal_in_facts}
            self.add_text("naujas")
            self.add_edge(self.last_text_id, goal_id)
            self.trace.append('{1} Tikslas {0} yra faktas. (Naujas.)',
                    goal, space)
            return []                   # \ref{bc:pseudo:emptyset}
        tried = False
        for i, rule in enumerate(rules):
                                        # \ref{bc:pseudo:rule_iter}
            if (rule.result == goal and
                all(premise not in goals for premise in rule.premises)):
                                        # \ref{bc:pseudo:rule_iter}
                tried = True
                self.trace.append(
                        '{3} Tikslas {0}. Randame: {1}. '
                        'Nauji tikslai: \\{{{2}\\}}.',
                        goal, rule, ', '.join(rule.premises), space)
                self.add_rule(rule)
                rule_id = self.last_rule_id
                self.add_edge(rule_id, goal_id)
                solution = []           # \ref{bc:pseudo:initial_Q}
                for premise in rule.premises:
                                        # \ref{bc:pseudo:premise_iter}
                    self.add_fact(premise)
                    self.add_edge(self.last_fact_id, rule_id)
                    rules_copy = rules[:]
                    del rules_copy[i]
                    path = self.recursion(
                            rules_copy, premise,
                            goals | {premise})
                                        # \ref{bc:pseudo:recursion}
                    if path is None:    # \ref{bc:pseudo:rule:fail}
                        break
                    else:               # \ref{bc:pseudo:rule:success}
                        solution += path
                else:                   # \ref{bc:pseudo:success}
                    self.trace.append(
                            '{1} Tikslas {0} yra faktas. (Išvestas.)',
                            goal, space)
                    solution.append(rule)
                    self.new_facts.add(goal)
                                        # \ref{bc:pseudo:add_fact}
                    return solution     # \ref{bc:pseudo:return_succ}
        self.trace.append(
                '{1} Tikslas {0}. Tikslo išvesti neįmanoma.', goal, space)
        if not tried:
            self.add_text("neišvedamas")
            self.add_edge(self.last_text_id, goal_id)
        return                          # \ref{bc:pseudo:failure}

    def add_text(self, text):
        """ Prideda tekstą į grafą.
        """
        self.graph.append(
                'node [shape="box", label="{1}", fixedsize="false", '
                'fontsize=10]; '
                'text{0}\n',
                self.text_counter, text)
        self.text_counter += 1

    @property
    def last_text_id(self):
        return 'text{0}'.format(self.text_counter - 1)

    def add_fact(self, fact):
        """ Prideda faktą į grafą.
        """
        self.graph.append(
                'node [shape="box", label="{1}", fixedsize="true", '
                'fontsize=11, width="0.3cm", height="0.3cm"]; '
                'fact{0}\n',
                self.fact_counter, fact)
        self.fact_counter += 1

    @property
    def last_fact_id(self):
        return 'fact{0}'.format(self.fact_counter - 1)

    def add_rule(self, rule):
        """ Prideda taisyklę į grafą.
        """
        self.graph.append(
                'node [shape="circle", label="{1}", fixedsize="true", '
                'fontsize=11, width="0.3cm", height="0.3cm"]; '
                'rule{0}\n',
                self.rule_counter, rule.index)
        self.rule_counter += 1

    @property
    def last_rule_id(self):
        return 'rule{0}'.format(self.rule_counter - 1)

    def add_edge(self, from_id, to_id):
        """ Prideda briauną į grafą.
        """
        self.graph.append('{0} -> {1};\n', from_id, to_id)

    def solve(self):
        """ Bando surasti tikslą naudodama atbulinį išvedimą.
        """
        self.fact_counter = 0
        self.rule_counter = 0
        self.text_counter = 0

        self.counter = 0
        label = 'graph:{0}'.format(int(self.invoke_counter) + 100)
        env = utils.Environment('pythonaienv',
                ('graph|{0}|Semantinis grafas.'.format(label), True))
        self.graph = env
        env.append(
                'digraph G {{ // graph-invoke-bc-solve-1: {0} \n',
                self.invoke_counter)
        env.append('edge [arrowsize="1.5"];\n')

        self.trace = utils.EnumerateEnvironment()
        self.facts = self.production_system.facts
        self.new_facts = set()
        self.add_fact(self.production_system.goal)
        self.solution = self.recursion(
                self.production_system.rules,
                self.production_system.goal,
                {self.production_system.goal},)
        if self.solution is not None:
            self.file.write('\n\nAtsakymas: ')
            if self.solution:
                self.file.write(
                    ', '.join(
                        utils.math(rule.index)
                        for rule in self.solution))
            else:
                self.file.write(utils.math('\\emptyset'))
        else:
            self.file.write('\n\nIšvedimas neegzistuoja.')
            self.solution = ()
        self.file.write('\n\nAtliktų veiksmų seka:')
        self.file.write(str(self.trace))
        env.append('}\n')
        self.file.write((
            '\n\nSemantinis grafas pateiktas \\ref{{{0}}} '
            'paveikslėlyje.\n').format(label))
        self.file.write(str(env) + '\n\n')

        return
        if int(self.invoke_counter) == 26:
            return
        label = 'graph:{0}'.format(int(self.invoke_counter) + 200)
        env = utils.Environment('pythonaienv',
                ('graph|{0}|Grafas.'.format(label), True))
        env.append(
                'digraph G {{ // graph-invoke-bc-solve-2: {0} \n',
                self.invoke_counter)
        env.append('node [fixedsize="true", fontsize=8, '
                   'width="0.2cm", height="0.2cm"];\n')
        env.append('edge [arrowsize="1.5", fontsize=8];\n')
        node = 'node [shape="{0}"]; {1}; \n'
        edge = 'edge [arrowsize="0.7", label="{0}"]; {1} -> {2}; \n'
        edge_solution = (
            'edge [arrowsize="1.5", label="{0}"]; {1} -> {2}; \n')
        rules = set()
        facts = set()
        edges = set()
        def add_fact(fact):
            if fact not in facts:
                env.append(node, 'box', fact)
                facts.add(fact)
        def add_edge(a, b, rule):
            if (a, b) not in edges:
                if rule in self.solution:
                    env.append(edge_solution, rule.index, a, b)
                else:
                    env.append(edge, rule.index, a, b)
                edges.add((a, b))
        for fact in self.production_system.facts:
            add_fact(fact)
        for rule in self.production_system.rules:
            for fact in rule.premises:
                add_fact(fact)
                add_edge(fact, rule.result, rule)
        env.append('}\n')
        self.file.write(str(env))

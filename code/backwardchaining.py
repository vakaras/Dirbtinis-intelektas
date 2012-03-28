import utils

from common import Rule, ProductionSystem, Solver


class BackwardChaining(Solver):
    """ Klasė, kurios objektai išveda produkcijas pasinaudodami
    atbulinio išvedimo metodu.
    """

    def recursion(self, rules, goal, goals):
        """ Sprendžia rekursyviai.
        """
        space = '→' * len(goals)
        if goal in self.facts:
                                        # \ref{bc:pseudo:goal_in_facts}
            self.trace.append('{1} Tikslas {0} yra faktas. (Duota.)',
                    goal, space)
            return []                   # \ref{bc:pseudo:emptyset}
        if goal in self.new_facts:
                                        # \ref{bc:pseudo:goal_in_facts}
            self.trace.append('{1} Tikslas {0} yra faktas. (Naujas.)',
                    goal, space)
            return []                   # \ref{bc:pseudo:emptyset}
        for i, rule in enumerate(rules):
                                        # \ref{bc:pseudo:rule_iter}
            if (rule.result == goal and
                all(premise not in goals for premise in rule.premises)):
                                        # \ref{bc:pseudo:rule_iter}
                self.trace.append(
                        '{3} Tikslas {0}. Randame: {1}. '
                        'Nauji tikslai: \\{{{2}\\}}.',
                        goal, rule, ', '.join(rule.premises), space)
                solution = []           # \ref{bc:pseudo:initial_Q}
                for premise in rule.premises:
                                        # \ref{bc:pseudo:premise_iter}
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
                '{1} Tikslas {0}. Fakto išvesti neįmanoma.', goal, space)
        return                          # \ref{bc:pseudo:failure}


    def solve(self):
        """ Bando surasti tikslą naudodama atbulinį išvedimą.
        """
        self.trace = utils.EnumerateEnvironment()
        self.facts = self.production_system.facts
        self.new_facts = set()
        self.solution = self.recursion(
                self.production_system.rules,
                self.production_system.goal,
                {self.production_system.goal},)
        if self.solution is not None:
            self.file.write('\n\nAtsakymas: ')
            if self.solution:
                self.file.write(utils.math(
                    ', '.join(rule.index for rule in self.solution)
                    ))
            else:
                self.file.write(utils.math('\\emptyset'))
        else:
            self.file.write('\n\nIšvedimas neegzistuoja.')
            self.solution = ()
        self.file.write('\n\nAtliktų veiksmų seka:')
        self.file.write(str(self.trace))

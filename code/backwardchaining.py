import utils

from common import Rule, ProductionSystem, Solver


class BackwardChaining(Solver):
    """ Klasė, kurios objektai išveda produkcijas pasinaudodami
    atbulinio išvedimo metodu.
    """

    def recursion(self, rules, facts, goal, goals):
        """ Sprendžia rekursyviai.
        """
        if goal in facts:               # \ref{bc:pseudo:goal_in_facts}
            self.trace.append('Tikslas {0} yra faktas. (Duota.)', goal)
            return []                   # \ref{bc:pseudo:emptyset}
        for rule in rules:
                                        # \ref{bc:pseudo:rule_iter}
            if (rule.result == goal and
                all(premise not in goals for premise in rule.premises)):
                                        # \ref{bc:pseudo:rule_iter}
                self.trace.append(
                        'Tikslas {0}. Randame: {1}. '
                        'Nauji tikslai: \\{{{2}\\}}.',
                        goal, rule, ', '.join(rule.premises))
                solution = []           # \ref{bc:pseudo:initial_Q}
                for premise in rule.premises:
                                        # \ref{bc:pseudo:premise_iter}
                    path = self.recursion(
                            rules - {rule}, facts, premise,
                            goals | {premise})
                                        # \ref{bc:pseudo:recursion}
                    if path is None:    # \ref{bc:pseudo:rule:fail}
                        break
                    else:               # \ref{bc:pseudo:rule:success}
                        solution += path
                else:                   # \ref{bc:pseudo:success}
                    self.trace.append(
                            'Tikslas {0} yra faktas. (Išvestas.)', goal)
                    solution.append(rule)
                    return solution     # \ref{bc:pseudo:return_succ}
        self.trace.append(
                'Tikslas {0}. Fakto išvesti neįmanoma.', goal)
        return                          # \ref{bc:pseudo:failure}


    def solve(self):
        """ Bando surasti tikslą naudodama atbulinį išvedimą.
        """
        self.trace = utils.EnumerateEnvironment()
        self.solution = self.recursion(
                self.production_system.rules,
                self.production_system.facts,
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

import utils

from common import Rule, ProductionSystem, Solver


class BackwardChaining(Solver):
    """ Klasė, kurios objektai išveda produkcijas pasinaudodami
    atbulinio išvedimo metodu.
    """

    def recursion(self, rules, facts, goal, goals):
        """ Sprendžia rekursyviai.
        """
        if goal in facts:
            self.trace.append('Tikslas {0} yra faktas. (Duota.)', goal)
            return []
        for rule in rules:
            if (rule.result == goal and
                all(premise not in goals for premise in rule.premises)):
                self.trace.append(
                        'Tikslas {0}. Randame: {1}. '
                        'Nauji tikslai: \\{{{2}\\}}.',
                        goal, rule, ', '.join(rule.premises))
                solution = []
                for premise in rule.premises:
                    path = self.recursion(
                            rules - {rule}, facts, premise,
                            goals | {premise})
                    if path is None:
                        break
                    else:
                        solution += path
                else:
                    self.trace.append(
                            'Tikslas {0} yra faktas. (Išvestas.)', goal)
                    solution.append(rule)
                    return solution
        self.trace.append(
                'Tikslas {0}. Fakto išvesti neįmanoma.', goal)


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
        self.file.write('\n\nAtliktų veiksmų seka:')
        self.file.write(str(self.trace))

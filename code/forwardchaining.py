import utils

from common import Rule, ProductionSystem, Solver


class ForwardChaining(Solver):
    """ Klasė, kurios objektai išveda produkcijas pasinaudodami
    tiesinio išvedimo metodu.
    """

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

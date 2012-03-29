import utils

from common import Rule, ProductionSystem, Solver


class ForwardChaining(Solver):
    """ Klasė, kurios objektai išveda produkcijas pasinaudodami
    tiesinio išvedimo metodu.
    """

    def run(self, rules, facts, goal):
        """ Ieško tikslo naudodama tiesioginį išvedimą.
        """
        were_used = True
        while were_used:                # \ref{fc:pseudo:while_condition}
            were_used = False
            for rule in rules:          # \ref{fc:pseudo:next_rule}
                if hasattr(rule, 'used'):
                    continue
                if (all(premise in facts for premise in rule.premises) and
                        rule.result not in facts):
                                        # \ref{fc:pseudo:if_condition}
                    facts.add(rule.result)
                                        # \ref{fc:pseudo:add_fact}
                    self.trace.append(
                            'Pritaikome taisyklę: {0}. '
                            'Faktų aibė po pritaikymo: '
                            '$\\{{${1}$\\}}$',
                            rule,
                            ', '.join(utils.math(fact) for fact in facts))
                    self.solution.append(rule)
                                        # \ref{fc:pseudo:add_rule}
                    rule.used = True
                    were_used = True

                    if goal in facts:   # \ref{fc:pseudo:while_condition}
                        self.trace.append('Rąstas tikslas.')
                        return True

    def solve(self):
        """ Bando surasti tikslą naudodama tiesioginį išvedimą.
        """

        self.trace = utils.EnumerateEnvironment()
        if self.run(
                self.production_system.rules[:],
                self.production_system.facts.copy(),
                self.production_system.goal,):
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
        self.file.write('\n\nAtliktų veiksmų seka:')
        self.file.write(str(self.trace))

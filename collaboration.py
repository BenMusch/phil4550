import credit_game
import random

MAX_COLLABORATORS = 3
ASK_STRATEGIES = [credit_game.LOW, credit_game.MED, credit_game.HIGH]

class AskStrategy:
    def __init__(self, same_group_ask, diff_group_ask):
        self.same_group_ask = same_group_ask
        self.diff_group_ask = diff_group_ask


class Collaborator:
    """Represents a single collaborator in a network"""
    def __init__(self, strategy_set, group):
        self.collaborations = set()
        self.strategy_set = strategy_set
        self.cur_strategy = random.sample(self.strategy_set)
        self.group = group
        self.last_collaboration_attempt = None

    def ask_for(self, other):
        return self._ask_for(self, other, self.cur_strategy)

    def collaboration_with(self, other):
        my_ask, their_ask = self.ask_for(other), other.ask_for(self)
        return Collaboration(self, other, my_ask, their_ask)

    def should_collaborate_with(self, other):
        our_collab_credit = self.collaboration_with(other).credit_for(self)
        return our_collab_credit > 0 and \
                (self.worst_collaboration().credit_for(self) < our_collab_credit or \
                 len(self.collaborations) < MAX_COLLABORATORS)

    def worst_collaboration(self):
        return min(self.collaborations, key=lambda c: c.credit_for(self))

    def enforce_max_collaborations(self):
        if len(self.collaborations) <= MAX_COLLABOTORS: return
        self.worst_collaboration().end()

    def total_credit(self):
        return sum(map(lambda c: c.credit_for(self), self.collaborations))

    def update_strategies(self):
        if not self.last_collaboration_attempt: return
        other = self.last_collaboration_attempt.collaborator_for(self)
        max_payoff = self.last_collaboration_attempt.credit_for(self)

        their_ask = None
        if self.last_collaboration_attempt.collab_a == self:
            their_ask = self.last_collaboration_attempt.b_ask
        else:
            their_ask = self.last_collaboration_attempt.a_ask

        # shuffle strategies to avoid this affecting stuff
        for strategy in random.shuffle(self.strategy_set):
            potential_collaboration = Collaboration(
                    self, other, self._ask_for(self, other, strategy), their_ask)
            new_payoff = potential_collaboration.credit_for(self)
            if new_payoff > max_payoff:
                max_payoff = new_payoff
                self.cur_strategy = strategy

    def _ask_for(self, other, strategy)
        if other.group == self.group: return strategy.same_group_ask
        else:                         return strategy.diff_group_ask


class Collaboration:
    def __init__(self, collab_a, collab_b, a_ask, b_ask):
        self.collab_a = collab_a
        self.collab_b = collab_b
        self.a_ask = a_ask
        self.b_ask = b_ask

    def collaborator_for(self, collaborator):
        if collaborator == self.collab_a:
            return self.collab_b
        elif collaborator == self.collab_b:
            return self.collab_a
        else:
            raise ValueError('%s is not a part of this collaboration' % collaborator)

    def credit_for(self, collaborator):
        a_credit, b_credit = credit_game.get_payoffs(self.a_ask, self.b_ask)
        if collaborator == self.collab_a:
            return a_credit
        elif collaborator == self.collab_b:
            return b_credit
        else:
            raise ValueError('%s is not a part of this collaboration' % collaborator)

    def is_fair(self):
        return self.a_ask == self.b_ask

    def is_diverse(self):
        return self.collab_a.group != self.collab_b.group

    def start(self):
        self.collab_a.collaborations.add(self)
        self.collab_b.collaborations.add(self)
        self.collab_a.enforce_max_collaborations()
        self.collab_b.enforce_max_collaborations()

    def end(self):
        self.collab_a.collaborations.remove(self)
        self.collab_b.collaborations.remove(self)

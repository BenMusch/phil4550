import credit_game
import random

MAX_COLLABORATORS = 3

class AskStrategy:
    def __init__(self, same_group_ask, diff_group_ask):
        self.same_group_ask = same_group_ask
        self.diff_group_ask = diff_group_ask

    def __repr__(self):
        return '<same={} diff={}>'.format(self.same_group_ask, self.diff_group_ask)


class Collaborator:
    """Represents a single collaborator in a network"""
    def __init__(self, strategy_set, group):
        self.collaborations = set()
        self.strategy_set = strategy_set
        self.cur_strategy = random.sample(self.strategy_set, 1)[0]
        self.group = group
        self.last_collaboration_attempt = None

    def ask_for(self, other):
        return self._ask_for(other, self.cur_strategy)

    def collaboration_with(self, other):
        my_ask, their_ask = self.ask_for(other), other.ask_for(self)
        return Collaboration(self, other)

    def should_collaborate_with(self, other):
        our_collab_credit = self.collaboration_with(other).credit_for(self)
        return our_collab_credit > 0 and \
                (not self.collaborations or \
                 self.worst_collaboration().credit_for(self) < our_collab_credit or \
                 len(self.collaborations) < MAX_COLLABORATORS)

    def worst_collaboration(self):
        if not self.collaborations:
            return None
        return min(self.collaborations, key=lambda c: c.credit_for(self))

    def enforce_max_collaborations(self):
        if len(self.collaborations) <= MAX_COLLABORATORS: return
        self.worst_collaboration().end()

    def total_credit(self):
        return sum(map(lambda c: c.credit_for(self), self.collaborations))

    def update_strategy(self):
        if not self.collaborations: return
        max_payoff = -1
        #print(self)
        #print(self.collaborations)
        for strategy in self.strategy_set:
            payoff = 0
            for c in self.collaborations:
                them = c.collaborator_for(self)
                their_ask = them.ask_for(self)
                my_ask = self._ask_for(them, strategy)
                payoff += credit_game.get_payoffs(my_ask, their_ask)[0]
            #print("Payoff of %s is %s" % (strategy, payoff))
            if payoff > max_payoff:
                max_payoff = payoff
                self.cur_strategy = strategy
        #print(self)

    def _ask_for(self, other, strategy):
        if other.group == self.group: return strategy.same_group_ask
        else:                         return strategy.diff_group_ask

    def __repr__(self):
        return "<group={} strat={}>".format(self.group, self.cur_strategy)


class Collaboration:
    def __init__(self, collab_a, collab_b):
        self.collab_a = collab_a
        self.collab_b = collab_b

    def collaborator_for(self, collaborator):
        if collaborator == self.collab_a:
            return self.collab_b
        elif collaborator == self.collab_b:
            return self.collab_a
        else:
            raise ValueError('%s is not a part of this collaboration' % collaborator)

    def credit_for(self, collaborator):
        a_ask, b_ask = self.collab_a.ask_for(self.collab_b), self.collab_b.ask_for(self.collab_a)
        a_credit, b_credit = credit_game.get_payoffs(a_ask, b_ask)
        if collaborator == self.collab_a:
            return a_credit
        elif collaborator == self.collab_b:
            return b_credit
        else:
            raise ValueError('%s is not a part of this collaboration' % collaborator)

    def is_fair(self):
        return self.collab_a.ask_for(self.collab_b) == self.collab_b.ask_for(self.collab_a)

    def benefitting_group(self):
        if self.is_fair() or (not self.is_diverse()):
            return "NONE"
        elif self.collab_a.ask_for(self.collab_b) > self.collab_b.ask_for(self.collab_a):
            return self.collab_a.group
        else:
            return self.collab_b.group

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

    def __repr__(self):
        return "<a={} b={}>".format(self.collab_a, self.collab_b)

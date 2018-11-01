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
    def __init__(self, strategy_set, group, strategy_number):
        self.collaborations = set()
        self.strategy_set = strategy_set
        self.cur_strategy = random.sample(self.strategy_set, 1)[0]
        self.group = group
        self.last_collaboration_attempt = None
        updates = [
                None,
                self.update_strategy_1,
                self.update_strategy_2,
                self.update_strategy_3,
                self.update_strategy_4]
        self.update_strategy = updates[strategy_number]

    def ask_for(self, other):
        return self._ask_for(other, self.cur_strategy)

    def collaboration_with(self, other):
        my_ask, their_ask = self.ask_for(other), other.ask_for(self)
        return Collaboration(self, other, my_ask, their_ask)

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

    def update_strategy_1(self):
        """
        update_strategy implementation 1:
         - Updates assuming re-negotatiation will all collaborators
         - Ignores any request made in the last round
         - Uses the current ask of the current collaborators, rather than the
           ask at the time of the collaboration
        """
        if not self.collaborations: return
        max_payoff = -1
        for strategy in self.strategy_set:
            payoff = 0
            for c in self.collaborations:
                them = c.collaborator_for(self)
                their_ask = them.ask_for(self)
                my_ask = self._ask_for(them, strategy)
                payoff += credit_game.get_payoffs(my_ask, their_ask)[0]
            if payoff > max_payoff:
                max_payoff = payoff
                self.cur_strategy = strategy

    def update_strategy_2(self):
        """
        update_strategy implementation 2:
         - Updates assuming re-negotatiation will all collaborators
         - Ignores any request made in the last round
         - Uses the ask at the time of collaboration, rather than the
           current strategy of the collaborator
        """
        if not self.collaborations: return
        max_payoff = -1
        for strategy in self.strategy_set:
            payoff = 0
            for c in self.collaborations:
                them = c.collaborator_for(self)
                their_ask = c.ask_from(them)
                my_ask = self._ask_for(them, strategy)
                payoff += credit_game.get_payoffs(my_ask, their_ask)[0]
            if payoff > max_payoff:
                max_payoff = payoff
                self.cur_strategy = strategy

    def update_strategy_3(self):
        """
        update_strategy implementation 3:
         - Updates assuming re-negotatiation will all collaborators
         - Takes into account the request made during the round
         - Uses the ask at the time of collaboration, rather than the
           current strategy of the collaborator
        """
        max_payoff = -1
        for strategy in self.strategy_set:
            payoffs = []
            collaborations_to_consider = self.collaborations.copy()
            if self.last_collaboration_attempt:
                collaborations_to_consider.add(self.last_collaboration_attempt)
            for c in collaborations_to_consider:
                them = c.collaborator_for(self)
                their_ask = c.ask_from(them)
                my_ask = self._ask_for(them, strategy)
                payoffs.append(credit_game.get_payoffs(my_ask, their_ask)[0])

            payoffs = sorted(payoffs, reverse=True)[:MAX_COLLABORATORS]

            payoff = sum(payoffs)
            if payoff > max_payoff:
                max_payoff = payoff
                self.cur_strategy = strategy

    def update_strategy_4(self):
        """
        update_strategy implementation 4:
         - Ignores "renegotiation" with current collaborators
         - Takes into account the request made during the round
         - Uses the ask at the time of collaboration, rather than the
           current strategy of the collaborator
        """
        if not self.last_collaboration_attempt: return
        c = self.last_collaboration_attempt

        them = c.collaborator_for(self)
        their_ask = c.ask_from(them)

        max_payoff = -1
        strategies_by_payoff = {}
        for strategy in self.strategy_set:
            my_ask = self._ask_for(them, strategy)
            payoff = credit_game.get_payoffs(my_ask, their_ask)[0]
            if payoff not in strategies_by_payoff: strategies_by_payoff[payoff] = []
            strategies_by_payoff[payoff].append(strategy)
            max_payoff = max(max_payoff, payoff)

        best_options = strategies_by_payoff[max_payoff]
        if self.cur_strategy in best_options: return

        # the new strategy should have one of the two factors in-common
        # with the old one, since we are only updating based on 1 request
        for strategy in best_options:
            if self.cur_strategy.same_group_ask == strategy.same_group_ask or \
                    self.cur_strategy.diff_group_ask == strategy.diff_group_ask:
                self.cur_strategy = strategy
                return
        raise ValueError('Couldn\'t find new strategy')


    def _ask_for(self, other, strategy):
        if other.group == self.group: return strategy.same_group_ask
        else:                         return strategy.diff_group_ask

    def __repr__(self):
        return "<group={} strat={}>".format(self.group, self.cur_strategy)


class Collaboration:
    def __init__(self, collab_a, collab_b, a_ask, b_ask):
        self.collab_a = collab_a
        self.collab_b = collab_b
        self.a_ask = a_ask
        self.b_ask = b_ask

    def ask_from(self, collaborator):
        return self._return_if(collaborator, self.a_ask, self.b_ask)

    def collaborator_for(self, collaborator):
        return self._return_if(collaborator, self.collab_b, self.collab_a)

    def credit_for(self, collaborator):
        a_credit, b_credit = credit_game.get_payoffs(self.a_ask, self.b_ask)
        return self._return_if(collaborator, a_credit, b_credit)

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

    def _return_if(self, collaborator, if_a, if_b):
        if collaborator == self.collab_a:
            return if_a
        elif collaborator == self.collab_b:
            return if_b
        else:
            raise ValueError('%s is not a part of this collaboration' % collaborator)

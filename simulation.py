from multiprocessing import Process
import sys
import random

from collaboration import *
import credit_game

################################################################################
# CONFIGURATION ################################################################
################################################################################

MAJORITY = "MAJORITY"
MINORITY = "MINORITY"

MAJORITY_SIZE = 50
MINORITY_SIZE = 50

NUM_ALLIES = 0

ROUNDS = 20000

UPDATE_STRATEGY = 4
ACTIONS_PER_ROUND = (MAJORITY_SIZE + MINORITY_SIZE) / 10

ASK_STRATEGIES = [credit_game.LOW, credit_game.MED, credit_game.HIGH]

def generate_strat_set():
    strat_set = []
    for same_group_ask in ASK_STRATEGIES:
        for diff_group_ask in ASK_STRATEGIES:
            strat_set.append(AskStrategy(same_group_ask, diff_group_ask))
    return strat_set

class Simulation:
    def __init__(self):
        self.minorities = [ Collaborator(generate_strat_set(), MINORITY, UPDATE_STRATEGY, False) for _ in range(MINORITY_SIZE) ]
        self.majorities = [ Collaborator(generate_strat_set(), MAJORITY, UPDATE_STRATEGY, False) for _ in range(MAJORITY_SIZE - NUM_ALLIES) ]
        self.majorities += [ Collaborator(generate_strat_set(), MAJORITY, UPDATE_STRATEGY, True) for _ in range(NUM_ALLIES) ]
        self.all_collaborators = self.minorities + self.majorities

    def do_ask(self, askers):
        for asker in askers:
            askee = random.sample(self.all_collaborators, 1)[0]
            while askee == asker or asker.collaborates_with(askee):
                askee = random.sample(self.all_collaborators, 1)[0]
            potential_collaboration = asker.collaboration_with(askee)
            askee.last_collaboration_attempt = potential_collaboration
            asker.last_collaboration_attempt = potential_collaboration
            if asker.should_collaborate_with(askee) and askee.should_collaborate_with(asker):
                potential_collaboration.start()

    def do_update(self, collaborators):
        for collaborator in collaborators:
            collaborator.update_strategy()

    def run(self):
        for i in range(ROUNDS):
            if i % (ROUNDS / 10) == 0:
                print("%s percent done" % (100.0 * float(i) / float(ROUNDS)))
            sample = random.sample(self.all_collaborators, ACTIONS_PER_ROUND)
            split_index = len(sample) / 5
            self.do_ask(sample[:split_index])
            self.do_update(sample[split_index:])
        stats = self.get_stats()
        print(stats)
        return stats

    def get_stats(self):
        maj_same_group, maj_diff_group = get_stats_for(self.majorities)
        min_same_group, min_diff_group = get_stats_for(self.minorities)
        maj_high = len((filter(lambda c: c.cur_strategy.diff_group_ask == credit_game.HIGH, self.majorities)))
        min_high = len((filter(lambda c: c.cur_strategy.diff_group_ask == credit_game.HIGH, self.minorities)))
        maj_low = len((filter(lambda c: c.cur_strategy.diff_group_ask == credit_game.LOW, self.majorities)))
        min_low = len((filter(lambda c: c.cur_strategy.diff_group_ask == credit_game.LOW, self.minorities)))
        to_print = (maj_same_group, maj_diff_group, min_same_group, min_diff_group)


        total = 0.0
        fair = 0.0
        diverse = 0.0
        winning = { MAJORITY: 0.0, MINORITY: 0.0, "NONE": 0.0 }
        # Hacky: Add .5 since there's 1 collaboration instance for each collaborator
        for collaborator in self.all_collaborators:
            for collaboration in collaborator.collaborations:
                total += 0.5
                winning[collaboration.benefitting_group()] += 0.5
                if collaboration.is_diverse(): diverse += 0.5
                if collaboration.is_fair(): fair += 0.5


        return {
                "maj_high": float(maj_high) / (float(len(self.majorities))),
                "min_high": float(min_high) / (float(len(self.minorities))),
                "maj_low": float(maj_low) / (float(len(self.majorities))),
                "min_low": float(min_low) / (float(len(self.minorities))),
#            "maj->maj avg. strategy": maj_same_group,
#            "maj->min avg. strategy": maj_diff_group,
#            "min->min avg. strategy": min_same_group,
#            "min->maj avg. strategy": min_diff_group,
#            "total collaborations": total,
#            "diverse collaborations": diverse,
#            "fair collaborations": fair,
#            "minority favorable unfair collaborations": winning[MINORITY],
#            "majorify favorable unfair collaborations": winning[MAJORITY],
#            "total minorities": len(self.minorities),
#            "total majorities": len(self.majorities),
#            "total allies": NUM_ALLIES,
        }

################################################################################
# ANALYSIS #####################################################################
################################################################################

def get_stats_for(collaborators):
    same_group = [ float(c.cur_strategy.same_group_ask) for c in collaborators ]
    diff_group = [ float(c.cur_strategy.diff_group_ask) for c in collaborators ]
    return avg(same_group), avg(diff_group)


def avg(sample):
    return float(sum(sample)) / float(len(sample))

################################################################################
# MAIN #########################################################################
################################################################################

def run_simul():
    sim = Simulation()
    return sim.run()

ps = [ Process(target=run_simul, args=()) for _ in range(10) ]
[ p.start() for p in ps ]
[ p.join() for p in ps ]

import sys
import random

from collaboration import *
import credit_game

MAJORITY_SIZE = 80
MINORITY_SIZE = 20

ASK_STRATEGIES = [credit_game.LOW, credit_game.MED, credit_game.HIGH]

def generate_strat_set():
    strat_set = []
    for same_group_ask in ASK_STRATEGIES:
        for diff_group_ask in ASK_STRATEGIES:
            strat_set.append(AskStrategy(same_group_ask, diff_group_ask))
    return strat_set

minorities = [ Collaborator(generate_strat_set(), "MINORITY") for _ in range(MINORITY_SIZE) ]
majorities = [ Collaborator(generate_strat_set(), "MAJORITY") for _ in range(MAJORITY_SIZE) ]
all_collaborators = minorities + majorities

def do_ask():
    asker, askee = random.sample(all_collaborators, 2)
    potential_collaboration = asker.collaboration_with(askee)
    askee.last_collaboration_attempt = potential_collaboration
    asker.last_collaboration_attempt = potential_collaboration
    if asker.should_collaborate_with(askee) and askee.should_collaborate_with(asker):
        potential_collaboration.start()

def do_update():
    random.sample(all_collaborators, 1)[0].update_strategy()

def get_stats(collaborators):
    same_group = [ float(c.cur_strategy.same_group_ask) for c in collaborators ]
    diff_group = [ float(c.cur_strategy.diff_group_ask) for c in collaborators ]

    return avg(same_group), avg(diff_group)

def print_stats():
    maj_same_group, maj_diff_group = get_stats(majorities)
    min_same_group, min_diff_group = get_stats(minorities)
    to_print = (maj_same_group, maj_diff_group, min_same_group, min_diff_group)
    print('maj->maj=%s maj->min=%s min->min min->maj' % maj_same_group)

def avg(sample):
    return float(sum(sample)) / float(len(sample))

for i in range(10000000):
    if i % 10000 == 0:
        print_stats()
    do_ask()
    do_update()
print('')
print('FINAL')
print_stats()

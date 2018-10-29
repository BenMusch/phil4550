import credit_game

MAX_COLLABORATORS = 5

class Collaborator:
    """Represents a single collaborator in a network"""
    def __init__(self, same_group_ask, diff_group_ask, group):
        self.collaborators = []
        self.same_group_ask = same_group_ask
        self.diff_group_ask = diff_group_ask
        self.group = group

    def ask_for(self, other):
        if other.group == self.group: return self.same_group_ask
        else: return self.diff_group_ask

LOW = 0
MED = 1
HIGH = 2

__payoffs = [4, 5, 6]

def get_payoffs(p1_ask, p2_ask):
    """Represents the bargaining game"""
    if p1_ask + p2_ask >= MED + HIGH: return (0, 0)
    return __payoffs[p1_ask], __payoffs[p2_ask]

assert get_payoffs(LOW, LOW)   == (4, 4)
assert get_payoffs(LOW, MED)   == (4, 5)
assert get_payoffs(LOW, HIGH)  == (4, 6)
assert get_payoffs(MED, LOW)   == (5, 4)
assert get_payoffs(MED, MED)   == (5, 5)
assert get_payoffs(MED, HIGH)  == (0, 0)
assert get_payoffs(HIGH, LOW)  == (6, 4)
assert get_payoffs(HIGH, MED)  == (0, 0)
assert get_payoffs(HIGH, HIGH) == (0, 0)

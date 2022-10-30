import math


def redistribute_wealth(model):
    total_wealth = sum([h.wealth for h in model.households.values()])
    new_wealth = math.floor(total_wealth / len(model.households))

    for household in model.households.values():
        household.wealth = new_wealth

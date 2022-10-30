import math


def redistribute_income(model):
    total_income = sum([h.income for h in model.households.values()])
    new_income = math.floor(total_income / len(model.households))

    for household in model.households.values():
        household.wealth = new_income

import collections

from model.agents.house import RentalHouse
from model.constants import ESSENTIAL_COSTS, MONTHS
from model.util.contracts import BuyingContract
from model.util.injector import inject

SPLIT_RATIO = 0.75
SPLIT_COST = 50_000

PretendHouse = collections.namedtuple('PretendHouse', ['size', 'quality'])

COUNTER = { 'prev_number_of_split_houses': 0}


@inject("households", "houses", "rules")
def set_new_tax_rate_splitting(self, households, houses, rules):
    total_rent_allowance_per_month = sum([self.determine_rent_allowance(h, h.contract.get_costs(), h.contract.house)
                                              for h in households.values()])
    total_income_per_month = sum([h.income for h in households.values() if h.income > 0])
    max_splitting_bonus_per_month = (houses.split_count - COUNTER['prev_number_of_split_houses']) * rules.split_bonus\
                                    / len(MONTHS)

    self.tax_rate = (total_rent_allowance_per_month + max_splitting_bonus_per_month) / total_income_per_month

    COUNTER['prev_number_of_split_houses'] = houses.split_count


def decide_to_split(model):
    actual_split_costs = SPLIT_COST - model.rules.split_bonus
    for household in model.households.values():
        if isinstance(household.contract, BuyingContract) and household.wealth >= actual_split_costs:
            current_utility = household.current_utility()

            house = household.contract.house

            new_house_size = round(house.size * SPLIT_RATIO)
            rent_part_size = house.size - new_house_size

            expected_rent = model.rental_market._get_market_prices([[rent_part_size, house.quality]])[0]
            rent_out_multiplier = len(model.households) / len(model.houses)

            expected_cost = max(household.contract.get_costs()
                                + actual_split_costs / len(MONTHS)
                                - rent_out_multiplier * expected_rent
                                , 0)

            splitting_utility = household.utility(PretendHouse(new_house_size, house.quality), expected_cost)

            if splitting_utility >= current_utility:
                house.size = new_house_size

                rental_part = RentalHouse(rent_part_size, house.quality)
                model.houses.add(rental_part)
                model.houses.split_count += 1
                rental_part.list()

                household.wealth -= actual_split_costs
                if hasattr(household, 'owns'):
                    household.owns.append(rental_part)
                else:
                    household.owns = [rental_part]


@inject("rules", "government")
def left_over_money_under_splitting(self, housing_costs, house, rules, government):
    rent_income = 0
    bonus = 0
    if hasattr(self, 'owns'):
        for house in self.owns:
            if house.renter is not None:
                rent_income += house.renter.contract.get_costs()
                bonus += rules.split_bonus

    allowance = government.determine_rent_allowance(self, housing_costs, house)
    tax = self.income * government.tax_rate if self.income > 0 else 0
    left_over = self.income + bonus + rent_income - ESSENTIAL_COSTS - housing_costs + allowance - tax

    if left_over > 0:
        spend = round(2 * left_over ** 0.75)
        return left_over - spend

    return left_over

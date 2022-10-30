from model.agents.government import Government
from model.constants import ESSENTIAL_COSTS
from model.util.injector import inject


def household_size_helper(household):
    if hasattr(household, 'size_of_sharing_household'):
        return household.size + household.size_of_sharing_household()

    return household.size


@inject("rules", "government")
def left_over_money_with_m2_per_person_tax(self, housing_costs, house, rules, government):
    m2_per_person = house.size / household_size_helper(self)

    allowance = government.determine_rent_allowance(self, housing_costs, house)
    tax = self.income * government.tax_rate if self.income > 0 else 0
    left_over = self.income - ESSENTIAL_COSTS - housing_costs - rules.m2_tax(m2_per_person) + allowance - tax

    if left_over > 0:
        spend = round(2 * left_over ** 0.75)
        return left_over - spend

    return left_over


class M2TaxGovernment(Government):
    def update(self):
        super().update()
        self.distribute_m2_taxes()

    @inject("households", "rules")
    def distribute_m2_taxes(self, households, rules):
        total_tax = 0
        for household in households.values():
            m2_per_person = household.contract.house.size / household_size_helper(household)
            total_tax += rules.m2_tax(m2_per_person)

        bonus_per_household = total_tax / len(households)

        for household in households.values():
            household.income += bonus_per_household



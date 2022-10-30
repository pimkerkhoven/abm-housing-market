import random

from model.agents.household import Household
from model.constants import MONTHS
from model.factories.household_factory import get_money
from model.util.injector import inject


@inject("rules")
def update_incomes_basic_income(self, year, households, rules):
    income_data = self._income_data(year)

    for household in households.values():
        new_income = round(get_money(household.age, household.income_percentile, income_data) / len(MONTHS))
        new_income = new_income + rules.basic_income_amount
        household.income = new_income


@inject("rules")
def _create_household_basic_income(self, min_age, max_age, size, year, rules):
    age = random.randint(min_age, max_age - 1)
    percentile = random.random()

    income = round(get_money(age, percentile, self._income_data(year)) / len(MONTHS))
    income = income + rules.basic_income_amount
    wealth = get_money(age, percentile, self._wealth_data(year))
    return Household(age, size, percentile, income, wealth)


@inject("households", "rules")
def set_new_tax_rate_basic_income(self, households, rules):
    total_rent_allowance_per_month = sum([self.determine_rent_allowance(h, h.contract.get_costs(), h.contract.house)
                                              for h in households.values()])
    total_income_per_month = sum([h.income for h in households.values() if h.income > 0])

    total_basic_income_amount_per_month = len(households) * rules.basic_income_amount

    self.tax_rate = (total_rent_allowance_per_month + total_basic_income_amount_per_month) / total_income_per_month
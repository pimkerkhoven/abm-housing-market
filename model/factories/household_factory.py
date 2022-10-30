import math
import random

from model.agents.household import Household, new_timeline_entry
from model.constants import MONTHS, MIN_AGE, MAX_AGE, MIN_HOUSEHOLD_SIZE, MAX_HOUSEHOLD_SIZE
from model.containers.households import Households
from model.data_loader.load_household_data import load_household_data
from model.data_loader.load_money_data import load_money_data
from model.util.skewed_distribution import skewed_distribution

LAST_YEAR_WITH_INCOME_DATA = 2020


def age_to_bottom_of_age_group(age):
    min_age = 5 * math.floor(age / 5)

    if min_age >= 85:
        return 85

    if min_age % 10 == 0:
        return min_age - 5

    return min_age


def get_money(age, percentile, data):
    min_age = age_to_bottom_of_age_group(age)
    max_age = 100 if min_age == 85 else min_age + 10

    total_percentile = 0
    for group_percentile, mean_val, median in data[(min_age, max_age)]:
        if percentile <= total_percentile + group_percentile:
            return round(skewed_distribution(
                mean_val * 1000, median * 1000))

        total_percentile += group_percentile

    _, mean_val, median = data[(min_age, max_age)][-1]
    return round(skewed_distribution(mean_val * 1000, median * 1000))


class HouseholdFactory:
    def __init__(self):
        self.household_data = load_household_data("data/household_age_size.csv")
        self.__income_data = load_money_data("data/household_income.csv")
        self.__wealth_data = load_money_data("data/household_wealth.csv")

    def create_households(self, year, scale_factor=1):
        households = Households()

        rest_households = 0

        for (min_age, max_age) in self.household_data[year]:
            for size in self.household_data[year][(min_age, max_age)]:
                scaled_count = self.household_data[year][(min_age, max_age)][size] / scale_factor
                rounded_scaled_count = round(scaled_count)

                if rounded_scaled_count == 0:
                    rest_households += scaled_count

                for _ in range(rounded_scaled_count):
                    household = self._create_household(min_age, max_age, size, year)

                    households.add(household)

        for _ in range(round(rest_households)):
            size = random.randint(MIN_HOUSEHOLD_SIZE, MAX_HOUSEHOLD_SIZE)
            household = self._create_household(MIN_AGE, MAX_AGE, size, year)

            households.add(household)

        return households

    def balance_households(self, model):
        # rest = immigration
        rest_households = 0

        for (min_age, max_age) in self.household_data[model.year]:
            to_die = []
            to_create = []

            for size in self.household_data[model.year][(min_age, max_age)]:
                expected_count = self.household_data[model.year][(min_age, max_age)][size]

                households_in_group = list(filter(
                    lambda h: min_age <= h.age < max_age and
                              h.size == size,
                    model.households.values()))

                current_number_of_households_in_group = len(households_in_group) * model.run_settings.scale_factor
                difference = expected_count - current_number_of_households_in_group
                scaled_difference = difference / model.run_settings.scale_factor

                if round(scaled_difference) == 0:
                    rest_households += scaled_difference

                scaled_difference = round(scaled_difference)

                if scaled_difference < 0:
                    to_die_households = random.sample(households_in_group, abs(scaled_difference))
                    to_die.extend(to_die_households)

                    # model.households.remove_all(died_households)
                elif scaled_difference > 0:
                    to_create.append((size, scaled_difference))
                    # for _ in range(scaled_difference):
                    #     model.households.add(self._create_household(min_age, max_age, size, model.year))

            for new_size, amount in to_create:
                while amount > 0:
                    if len(to_die) > 0:
                        household = to_die.pop()

                        before_utility = household.current_utility()
                        # TODO: Check if size is updated in model.households
                        household.size = new_size
                        after_utility = household.current_utility()

                        if after_utility < before_utility:
                            household.contract.want_to_move = True

                        size_info = {'type': 'SIZE_CHANGE', 'size': household.size,
                                     'age': household.age,
                                     'want_to_move': household.contract.want_to_move}
                        household.timeline.append(new_timeline_entry(size_info))
                    else:
                        model.households.add(self._create_household(min_age, max_age, new_size, model.year))

                    amount -= 1

            model.households.remove_all(to_die)

        rest_households = round(rest_households)
        if rest_households < 0:
            existing_households = [h for h in model.households.values() if h.contract is not None]

            died_households = random.sample(existing_households, abs(rest_households))
            model.households.remove_all(died_households)
        elif rest_households > 0:
            for _ in range(rest_households):
                size = random.randint(MIN_HOUSEHOLD_SIZE, MAX_HOUSEHOLD_SIZE)
                household = self._create_household(MIN_AGE, MAX_AGE, size, model.year)
                model.households.add(household)

    def update_incomes(self, year, households):
        income_data = self._income_data(year)

        for household in households.values():
            new_income = round(get_money(household.age, household.income_percentile, income_data) / len(MONTHS))
            household.income = new_income

    def _create_household(self, min_age, max_age, size, year):
        age = random.randint(min_age, max_age - 1)
        percentile = random.random()

        income = round(get_money(age, percentile, self._income_data(year)) / len(MONTHS))
        wealth = get_money(age, percentile, self._wealth_data(year))

        return Household(age, size, percentile, income, wealth)

    def _income_data(self, year):
        if year <= LAST_YEAR_WITH_INCOME_DATA:
            return self.__income_data[year]

        return self.__income_data[LAST_YEAR_WITH_INCOME_DATA]

    def _wealth_data(self, year):
        if year <= LAST_YEAR_WITH_INCOME_DATA:
            return self.__wealth_data[year]

        return self.__wealth_data[LAST_YEAR_WITH_INCOME_DATA]

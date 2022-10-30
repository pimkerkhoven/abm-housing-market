import collections

from model.agents.agent import Agent
from model.agents.house import BuyHouse, RentalHouse, SocialHouse
from model.constants import RENT_ALLOWANCE_WEALTH_LIMIT_ONE_PERSON, RENT_ALLOWANCE_WEALTH_LIMIT_MULTI_PERSON, MONTHS, PENSION_AGE
from model.defaults import DEFAULT_LIBERALISATION_THRESHOLD
from model.util.injector import inject

BasicRentParameters = collections.namedtuple('BasicRentParameters', ['a', 'b', 'min_income_limit',
                                                                     'target_amount', 'min_basic_rent'])


def _get_basic_rent_parameters(household):
    if household.size == 1 and household.age < PENSION_AGE:
        return BasicRentParameters(0.000000623385, 0.002453085056, 16_950, 16.94, 237.62)
    if household.size > 1 and household.age < PENSION_AGE:
        return BasicRentParameters(0.000000361614, 0.002075390738, 22_000, 16.94, 237.62)
    if household.size == 1 and household.age >= PENSION_AGE:
        return BasicRentParameters(0.000000840817, -0.004129343663, 18_775, 16.94, 235.80)
    if household.size > 1 and household.age >= PENSION_AGE:
        return BasicRentParameters(0.000000519036, -0.004315550434, 25_025, 16.94, 233.99)


class Government(Agent):
    def __init__(self, initial_tax_rate=0, liberalisation_threshold=DEFAULT_LIBERALISATION_THRESHOLD):
        super().__init__()
        self.tax_rate = initial_tax_rate
        self.liberalisation_threshold = liberalisation_threshold

    def update(self):
        self.set_new_tax_rate()
        self.set_liberalisation_threshold()

    @inject("houses")
    def set_liberalisation_threshold(self, houses):
        rental_houses = len([h for h in houses.values() if isinstance(h, RentalHouse)])
        social_houses = len([h for h in houses.values() if isinstance(h, SocialHouse)])

        percentage_social = social_houses / (rental_houses + social_houses)

        if percentage_social < 0.5:
            self.liberalisation_threshold *= 1.05
        elif percentage_social > 0.75:
            self.liberalisation_threshold *= 0.95

    @inject("households")
    def set_new_tax_rate(self, households):
        total_rent_allowance_per_month = sum([self.determine_rent_allowance(h, h.contract.get_costs(), h.contract.house)
                                              for h in households.values()])
        total_income_per_month = sum([h.income for h in households.values() if h.income > 0])

        self.tax_rate = total_rent_allowance_per_month / total_income_per_month

    def determine_rent_allowance(self, household, rent, house):
        if isinstance(house, BuyHouse):
            return 0

        if (household.wealth > RENT_ALLOWANCE_WEALTH_LIMIT_ONE_PERSON and household.size == 1) or \
                (household.wealth > RENT_ALLOWANCE_WEALTH_LIMIT_MULTI_PERSON and household.size > 1):
            return 0

        quality_discount_limit = 0.58 * self.liberalisation_threshold
        max_rent_limit = quality_discount_limit if household.age < 23 else self.liberalisation_threshold

        if rent > max_rent_limit:
            return 0

        calculation_income = max(0, household.income * len(MONTHS))

        brp = _get_basic_rent_parameters(household)

        if calculation_income <= brp.min_income_limit:
            basic_rent = brp.min_basic_rent
        else:
            basic_rent = brp.a * calculation_income ** 2 + brp.b * calculation_income + brp.target_amount

        capping_limit = 0.84 * self.liberalisation_threshold if household.size <= 2 else 0.9 * self.liberalisation_threshold

        part_a = max(0, min(rent, quality_discount_limit) - basic_rent)
        part_b = max(0, min(rent, capping_limit) - max(basic_rent, quality_discount_limit)) * 0.65
        part_c = max(0, rent - max(basic_rent, capping_limit)) * 0.40

        return part_a + part_b + part_c


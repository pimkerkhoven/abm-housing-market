from model.agents.agent import Agent
from model.constants import MORTGAGE_DURATION, MORTGAGE_INTEREST_RATE, MONTHS, LIVING_QUOTE_TABLE, \
    ANNUITY_TABLE, WEALTH_BIDDING_PORTION


class Bank(Agent):
    def __init__(self):
        super().__init__()
        self.mortgage_duration = MORTGAGE_DURATION
        self.interest_rate = MORTGAGE_INTEREST_RATE

    def max_bid(self, household):
        max_mortgage = self._max_mortgage(household.income)
        max_house_value_for_mortgage = (1 - self.interest_rate) * max_mortgage

        if household.wealth >= 0:
            return max_house_value_for_mortgage + WEALTH_BIDDING_PORTION * household.wealth

        return max_house_value_for_mortgage

    def value_to_monthly_payment(self, value, household, buying=False):
        need_mortgage_for = value - round(WEALTH_BIDDING_PORTION * household.wealth) if household.wealth > 0 else value

        if need_mortgage_for <= 0:
            return 0, 0

        total_mortgage = need_mortgage_for * (1 + self.interest_rate)

        return round(total_mortgage), round(total_mortgage / (self.mortgage_duration * len(MONTHS)))

    def _max_mortgage(self, income):
        test_income = income * len(MONTHS)
        maximal_living_cost = test_income * LIVING_QUOTE_TABLE[self.interest_rate]

        return round(maximal_living_cost / ANNUITY_TABLE[(self.mortgage_duration, self.interest_rate)])

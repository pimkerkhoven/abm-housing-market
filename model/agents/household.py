import collections
import random

from model.agents.agent import Agent
from model.agents.house import SocialHouse, BuyHouse
from model.constants import ESSENTIAL_COSTS, MIN_AGE
from model.util.contracts import Homeless, THE_NO_HOUSE
from model.util.injector import inject

TimeLineEntry = collections.namedtuple('TimeLineEntry', ('year', 'month', 'record'))

@inject("year", "month")
def new_timeline_entry(info, year, month):
    return TimeLineEntry(year, month, info)

class Household(Agent):
    def __init__(self, age, size, income_percentile, income, wealth, contract=None):
        super().__init__()
        self.age = age
        self.size = size
        self.income_percentile = income_percentile
        self.income = income
        self.wealth = wealth
        self._contract = contract
        self.history = []
        self.wait_list_time = age - MIN_AGE if random.random() < 0.75 else 0

        born_info = {'type': 'BORN', 'id': self.id, 'age': self.age, 'size': self.size,
                     'income_percentile': self.income_percentile}
        self.timeline = [new_timeline_entry(born_info)]

    @inject("year")
    def set_contract(self, contract, year):
        if year is not None:
            contract_info = {'type': 'CONTRACT_CHANGE', 'house_id': contract.house.id, 'house_size': contract.house.size,
                         'house_quality': contract.house.quality, 'cost': contract.get_costs(),
                         'house_type': type(contract.house).__name__}
            self.timeline.append(new_timeline_entry(contract_info))

        self.history.append(contract.to_record())
        self._contract = contract

    @property
    def contract(self):
        return self._contract

    @inject("government")
    def left_over_money(self, housing_costs, house, government):
        allowance = government.determine_rent_allowance(self, housing_costs, house)
        tax = self.income * government.tax_rate if self.income > 0 else 0

        essential_costs_by_household_size = (0.9 + 0.05 * self.size) * ESSENTIAL_COSTS
        left_over = self.income - essential_costs_by_household_size - housing_costs + allowance - tax

        if left_over > 0:
            spend = round(2 * left_over ** 0.75)
            return left_over - spend

        return left_over

    def current_utility(self):
        return self.utility(self._contract.house, self._contract.get_costs())

    @inject("parameters")
    def utility(self, house, cost, parameters):
        return parameters.utility(self, house, cost)

    def gain_wealth(self):
        left_over_money = self.left_over_money(self._contract.get_costs(), self._contract.house)

        if left_over_money >= 0 or self.wealth + left_over_money >= 0:
            self.wealth += left_over_money
        else:
            self._contract.house.move_out(THE_NO_HOUSE, self)

    def update_contract(self):
        self._contract.update()

    def sell(self, value):
        winnings_from_selling = value - self._contract.mortgage_remaining
        self.wealth += winnings_from_selling
        self.assign_homelessness()

    def assign_homelessness(self):
        self._contract = Homeless()

    def remove(self):
        if hasattr(self._contract.house, 'owner'):
            self._contract.house.owner = None

        self._contract.house.move_out(None, self)

    @inject("rental_market", "buying_market", "bank")
    def act(self, best_option, rental_market, buying_market, bank):
        current_utility = self.current_utility()

        if current_utility >= best_option.utility:
            return

        if isinstance(best_option.house, SocialHouse) and not isinstance(self.contract.house, BuyHouse):
            best_option.house.show_interest(self)
        else:
            self.contract.house.move_out(best_option.house, self)

    @inject("buying_market", "rental_market")
    def look_at_markets(self, buying_market, rental_market):
        best_buying_option = buying_market.get_best_option_from_market(self)
        best_rental_option = rental_market.get_best_option_from_market(self)

        return max(best_buying_option, best_rental_option, key=lambda option: option.utility)

    def __repr__(self):
        return "Household({}, {}, {}, {:.2f}, {}, {})".format(self.id, self.age, self.size,
                                                              self.income_percentile,
                                                              self.income, self.wealth)

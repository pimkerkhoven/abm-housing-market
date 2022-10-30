import collections

import numpy as np

from model.agents.bank import Bank
from model.agents.government import Government
from model.agents.household import new_timeline_entry
from model.agents.market import SocialMarket, BuyingMarket
from model.constants import MONTHS, MIN_BUYING_PRICE, MIN_RENTAL_PRICE
from model.util.injector import Injector

State = collections.namedtuple('State', ["year", "month", "households", "houses", "buy_listings",
                                         "rent_listings", "buying_transactions", "rental_transactions"])

Hooks = collections.namedtuple('Hooks', ['post_init', 'end_of_year', 'post_create_houses'], defaults=[[], [], []])


class Model:
    def __init__(self, run_settings, parameters, rules, household_factory, house_factory, data_collectors=None,
                 collector_groups=None, individual_collectors=None, hooks=Hooks()):
        Injector.set_model(self)

        self.run_settings = run_settings
        self.parameters = parameters
        self.rules = rules

        self.year = None
        self.month = None

        self.household_factory = household_factory
        self.house_factory = house_factory

        self.bank = Bank()
        self.government = Government()

        self.buying_market = BuyingMarket(*self.parameters.buy_market_price_params,
                                          min_price=MIN_BUYING_PRICE, max_price=rules.max_buy_price)
        self.rental_market = SocialMarket(*self.parameters.rent_market_price_params,
                                          min_price=MIN_RENTAL_PRICE, max_price=rules.max_rent_price)

        self.history = []

        self.hooks = hooks
        for hook in self.hooks.post_init:
            hook(self)

        self.data_collectors = data_collectors if data_collectors is not None else []
        self.collector_groups = collector_groups if collector_groups is not None else []

        self.individual_collectors = individual_collectors if individual_collectors is not None else []

        self.data = {}
        self.tracked_individuals = {}

        for group_name, _ in self.collector_groups:
            self.data[group_name] = {}
            for data_collector in self.data_collectors:
                self.data[group_name][data_collector.__name__] = []

    def run(self):
        self._initialize()
        self._calibrate()

        print("Calibration Done")
        print("Tax rate is: {}".format(self.government.tax_rate))

        for year in range(self.run_settings.start_year, self.run_settings.end_year):
            self.year = year

            for month in MONTHS:
                self.month = month
                self._tick()

                # TODO: check months we want to track this
                for household_id in self.tracked_individuals:
                    if household_id in self.households._agents:
                        h = self.households[household_id]
                        for collector in self.individual_collectors:
                            self.tracked_individuals[h.id][collector.__name__].append(collector(h))
                    else:
                        for collector in self.individual_collectors:
                            self.tracked_individuals[household_id][collector.__name__].append(np.nan)

            for group_name, group_filter in self.collector_groups:
                for data_collector in self.data_collectors:
                    self.data[group_name][data_collector.__name__].append(data_collector(group_filter, self))


            if self.year < self.run_settings.end_year - 1:
                self._update_households()
                self.households.assign_homelessness()

                self.government.update()

                for hook in self.hooks.end_of_year:
                    hook(self)

                self.houses.construct()

        for household_id in self.tracked_individuals:
            if household_id in self.households._agents:
                h = self.households[household_id]
                self.tracked_individuals[household_id]['timeline'] = h.timeline

    def _initialize(self):
        self.households = self.household_factory.create_households(self.run_settings.start_year,
                                                                   self.run_settings.scale_factor)
        self.houses = self.house_factory.create_houses(self.run_settings.start_year,
                                                       self.rules.initial_portion_houses_for_rent,
                                                       self.run_settings.scale_factor)

        for household in self.households.values():
            if 20 <= household.age <= 30 and household.size == 2:
                self.tracked_individuals[household.id] = {}

                for collector in self.individual_collectors:
                    self.tracked_individuals[household.id][collector.__name__] = []

        for hook in self.hooks.post_create_houses:
            hook(self)

        self._list_houses()
        self.buying_market.update()
        self.rental_market.update()
        self.households.assign_homelessness()

    def _calibrate(self):
        for i in range(self.run_settings.calibration_length):
            self._tick(calibrate=True)
            self.government.set_new_tax_rate()

        # contracts = [h.contract for h in self.households.values()]
        # pprint(contracts)
        # pprint(mean([c.run_time for c in contracts]))
        for household_id in self.tracked_individuals:
            if household_id in self.households._agents:
                h = self.households[household_id]

                start_house_info = {'type': 'START_HOUSE', 'house_id': h.contract.house.id,
                                    'house_size': h.contract.house.size,
                                    'house_quality': h.contract.house.quality, 'cost': h.contract.get_costs(),
                                    'house_type': type(h.contract.house).__name__}
                h.timeline.append(new_timeline_entry(start_house_info))

    def _tick(self, calibrate=False):
        self.buying_market.fit_market_price_parameters()
        self.rental_market.fit_market_price_parameters()

        self.households.tick(calibrate)

        self.buying_market.update()
        self.rental_market.update()

        self.households.assign_homelessness()

    def _update_households(self):
        self.households.age_one_year()
        self.household_factory.balance_households(self)
        self.household_factory.update_incomes(self.year, self.households)

    def _list_houses(self):
        for house in self.houses.values():
            house.list()

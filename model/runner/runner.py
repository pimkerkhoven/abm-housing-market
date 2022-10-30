import collections
import json
import math

import numpy as np

from model.agents.agent import Agent
from model.defaults import DEFAULT_CONSTRUCTION_RULES, DEFAULT_LIBERALISATION_THRESHOLD, \
    DEFAULT_MAX_INCOME_ONE_PERSON_HOUSEHOLD, DEFAULT_MAX_INCOME_MULTI_PERSON_HOUSEHOLD
from model.factories.house_factory import HouseFactory
from model.factories.household_factory import HouseholdFactory
from model.model import Model, Hooks

RunSettings = collections.namedtuple('RunSettings', ['start_year', 'end_year', 'scale_factor',
                                                     'calibration_length', 'number_of_runs'])

Parameters = collections.namedtuple('Parameters', ["utility", "buy_market_price_params",
                                                   "rent_market_price_params"])

Rules = collections.namedtuple('Rules', ["construction",
                                         "buy_bonus",
                                         "max_income_one_person_household",
                                         "max_income_multi_person_household",
                                         "m2_per_person_limit",
                                         "m2_tax",
                                         "share_bonus",
                                         "split_bonus",
                                         "initial_portion_houses_for_rent",
                                         "max_buy_price",
                                         "max_rent_price",
                                         "constant_price",
                                         "basic_income_amount"],
                               defaults=[DEFAULT_CONSTRUCTION_RULES,
                                         None,
                                         DEFAULT_MAX_INCOME_ONE_PERSON_HOUSEHOLD,
                                         DEFAULT_MAX_INCOME_MULTI_PERSON_HOUSEHOLD,
                                         None,
                                         None,
                                         0,
                                         0,
                                         None,
                                         math.inf,
                                         math.inf,
                                         None,
                                         None])


class Runner:
    def __init__(self, run_settings, parameters, rules, data_collectors=None,
                 collector_groups=None, individual_collectors=None, hooks=Hooks(),
                 model_name=""):
        self.run_settings = run_settings
        self.parameters = parameters
        self.rules = rules
        self.hooks = hooks
        self.data_collectors = data_collectors
        self.collector_groups = collector_groups
        self.individual_collectors = individual_collectors
        self.model_name = model_name

        self.runs = []

    def run(self):
        for run_number in range(self.run_settings.number_of_runs):
            print("Run {}".format(run_number + 1))
            Agent.reset_id_iter()
            model = Model(self.run_settings, self.parameters, self.rules, HouseholdFactory(), HouseFactory(),
                          data_collectors=self.data_collectors, collector_groups=self.collector_groups,
                          individual_collectors=self.individual_collectors, hooks=self.hooks)

            model.run()

            with open('output_data/one_run_data/{}-individuals.json'.format(self.model_name), 'w') as file:
                json.dump(model.tracked_individuals, file)

            self.runs.append(model.data)

    # def average_over_runs(self, data_collector, by_year=False, take="mean"):
    #     step = 12 if by_year else 1
    #
    #     result = []
    #     for run in self.runs:
    #         run_result = []
    #         for index in range(0, len(run[data_collector.__name__]), step):
    #             if take == "sum":
    #                 run_result.append(np.nansum(run[data_collector.__name__][index:index + step]))
    #             elif take == "mean":
    #                 run_result.append(np.nanmean(run[data_collector.__name__][index:index + step]))
    #             elif take == "first":
    #                 run_result.append(run[data_collector.__name__][index])
    #             else:
    #                 raise RuntimeError("Unsupported take method")
    #
    #         result.append(run_result)
    #
    #     return np.nanmean(result, axis=0)

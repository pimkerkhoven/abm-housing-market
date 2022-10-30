import json
import os

from extensions.fixed_construction import construct_fixed_total
from extensions.house_splitting import left_over_money_under_splitting, decide_to_split, \
    set_new_tax_rate_splitting
from model.agents.government import Government
from model.agents.household import Household
from model.containers.houses import Houses
from model.model import Hooks
from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.utility_functions import default_utility_function
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors, \
    collector_groups

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])

Household.left_over_money = left_over_money_under_splitting
Houses.construct = construct_fixed_total
Government.set_new_tax_rate = set_new_tax_rate_splitting


def add_split_count_to_houses(m):
    m.houses.split_count = 0


hooks = Hooks(
    post_create_houses=[add_split_count_to_houses],
    end_of_year=[decide_to_split]
)

rewards = [5_000, 10_000, 20_000, 30_000]

file_name = os.path.basename(__file__)
first_part_model_name, _ = os.path.splitext(file_name)

if __name__ == '__main__':
    for reward in rewards:
        model = Runner(run_settings, parameters, Rules(split_bonus=reward), data_collectors=data_collectors,
                       collector_groups=collector_groups, hooks=hooks)

        model.run()
        model_name = "{}-reward={}".format(first_part_model_name, reward)

        with open('output_data/hypothesis1/{}.json'.format(model_name), 'w') as file:
            json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

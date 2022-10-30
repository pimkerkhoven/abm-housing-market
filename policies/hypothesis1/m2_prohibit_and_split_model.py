import json
import os

from extensions.fixed_construction import construct_fixed_total
from extensions.prohibit_too_high_m2_per_person import get_best_option_from_market_with_m2_prohibition, \
    get_best_social_rent_option_with_m2_prohibition, get_best_non_social_rent_option_with_m2_prohibition
from extensions.split_unused_houses import split_houses_hook, set_new_tax_rate_splitting
from model.agents.government import Government
from model.agents.market import BuyingMarket, SocialMarket
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

BuyingMarket.get_best_option_from_market = get_best_option_from_market_with_m2_prohibition
SocialMarket.get_best_social_rent_option = get_best_social_rent_option_with_m2_prohibition
SocialMarket.get_best_non_social_rent_option = get_best_non_social_rent_option_with_m2_prohibition
Houses.construct = construct_fixed_total
Government.set_new_tax_rate = set_new_tax_rate_splitting


m2_limits = [30, 55, 80, 105]

file_name = os.path.basename(__file__)
first_part_model_name, _ = os.path.splitext(file_name)

hooks = Hooks(
    end_of_year=[split_houses_hook]
)

if __name__ == '__main__':
    for m2_limit in m2_limits:
        model = Runner(run_settings, parameters, Rules(m2_per_person_limit=m2_limit),
                       data_collectors=data_collectors, collector_groups=collector_groups, hooks=hooks)

        model.run()
        model_name = "{}-m2_limit={}".format(first_part_model_name, m2_limit)

        with open('output_data/hypothesis1/{}.json'.format(model_name), 'w') as file:
            json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

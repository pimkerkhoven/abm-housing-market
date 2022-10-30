import json
import math
import os

from extensions.constant_price_prediction import _get_market_prices_constant
from model.agents.market import SocialMarket
from model.constants import NEW_LIST_PRICE_FACTOR
from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.utility_functions import default_utility_function
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])

SocialMarket._get_market_prices = _get_market_prices_constant

prices = [500, 750, 1000]

file_name = os.path.basename(__file__)
first_part_model_name, _ = os.path.splitext(file_name)

if __name__ == '__main__':
    for price in prices:
        rules = Rules(constant_price=(price / NEW_LIST_PRICE_FACTOR), liberalisation_threshold=math.inf,
                      max_income_one_person_household=math.inf, max_income_multi_person_household=math.inf)
        model = Runner(run_settings, parameters, rules, data_collectors=data_collectors)

        model.run()

        model_name = "{}-price={}".format(first_part_model_name, price)

        with open('output_data/hypothesis3/{}.json'.format(model_name), 'w') as file:
            json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

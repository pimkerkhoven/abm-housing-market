import json
import os

from extensions.basic_income import update_incomes_basic_income, _create_household_basic_income, \
    set_new_tax_rate_basic_income
from model.agents.government import Government
from model.factories.household_factory import HouseholdFactory
from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.utility_functions import default_utility_function
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])

HouseholdFactory.update_incomes = update_incomes_basic_income
HouseholdFactory._create_household = _create_household_basic_income
Government.set_new_tax_rate = set_new_tax_rate_basic_income

thresholds = [0, 750]

file_name = os.path.basename(__file__)
first_part_model_name, _ = os.path.splitext(file_name)

if __name__ == '__main__':
    for threshold in thresholds:
        rules = Rules(liberalisation_threshold=threshold, basic_income_amount=1000)

        model = Runner(run_settings, parameters, rules, data_collectors=data_collectors)
        model.run()

        model_name = "{}-lib_threshold={}".format(first_part_model_name, threshold)

        with open('output_data/hypothesis2/{}.json'.format(model_name), 'w') as file:
            json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

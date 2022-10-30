import json
import os

from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.utility_functions import default_utility_function
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])

income_limit_rules = [
    Rules(max_income_one_person_household=20_000, max_income_multi_person_household=22_500),
    Rules(max_income_one_person_household=60_000, max_income_multi_person_household=67_500)]

file_name = os.path.basename(__file__)
first_part_model_name, _ = os.path.splitext(file_name)

if __name__ == '__main__':
    for rules in income_limit_rules:
        model = Runner(run_settings, parameters, rules, data_collectors=data_collectors)
        model.run()

        model_name = "{}-max_income={}".format(first_part_model_name, rules.max_income_one_person_household)

        with open('output_data/misc/{}.json'.format(model_name), 'w') as file:
            json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

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

# -1 = 0
percentages = [-1, 0.25, 0.5, 0.75, 1]

file_name = os.path.basename(__file__)
first_part_model_name, _ = os.path.splitext(file_name)

if __name__ == '__main__':
    for percentage in percentages:
        rules = Rules(construction={"percentage_for_rent": percentage,
                                    "target_shortage": 0.02,
                                    "max_build_limit": 150_000})

        model = Runner(run_settings, parameters, rules, data_collectors=data_collectors)
        model.run()

        model_name = "{}-percentage={}".format(first_part_model_name, percentage)

        with open('output_data/hypothesis4/{}.json'.format(model_name), 'w') as file:
            json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

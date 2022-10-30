import json
import math
import os

from extensions.fixed_construction import construct_fixed_total
from model.containers.houses import Houses
from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.utility_functions import default_utility_function
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors, \
    collector_groups

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])

# Houses.construct = construct_fixed_total

model = Runner(run_settings, parameters, Rules(construction={
    "percentage_for_rent": 0.45,
    "target_shortage": 0,
    "max_build_limit": math.inf}), data_collectors=data_collectors, collector_groups=collector_groups)


if __name__ == '__main__':
    print("TODO: reset number of runs!!!!")

    file_name = os.path.basename(__file__)
    model_name, _ = os.path.splitext(file_name)

    model.run()

    with open('output_data/hypothesis1/{}.json'.format(model_name), 'w') as file:
        json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

import json
import os

import numpy as np

from model.constants import MIN_HOUSE_SIZE, MAX_HOUSE_SIZE, MIN_HOUSE_QUALITY, MAX_HOUSE_QUALITY
from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.utility_functions import default_utility_function
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])


def size_distribution():
    return min(max(np.random.normal(70, 30), MIN_HOUSE_SIZE), MAX_HOUSE_SIZE)


def quality_distribution():
    return min(max(np.random.normal(3, 2), MIN_HOUSE_QUALITY), MAX_HOUSE_QUALITY)


rules = Rules(construction={"percentage_for_rent": 0.45,
                            "target_shortage": 0.02,
                            "max_build_limit": 150_000,
                            "size_distribution": size_distribution,
                            "quality_distribution": quality_distribution})

model = Runner(run_settings, parameters, rules, data_collectors=data_collectors)

if __name__ == '__main__':
    file_name = os.path.basename(__file__)
    model_name, _ = os.path.splitext(file_name)

    model.run()

    with open('output_data/construction_exploration/{}.json'.format(model_name), 'w') as file:
        json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

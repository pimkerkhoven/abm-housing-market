import json
import os

from extensions.buyer_bonus import BonusBank, BonusGovernment
from model.model import Hooks
from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.utility_functions import default_utility_function
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])


def deserve_bonus(household):
    return household.contract.want_to_move_time > 8


def make_bank_bonus_bank(m):
    m.bank = BonusBank()
    m.government = BonusGovernment()


hooks = Hooks(
    post_init=[make_bank_bonus_bank],
    end_of_year=[]
)

rules = Rules(buy_bonus={"value": 50_000, "deserve?": deserve_bonus})
model = Runner(run_settings, parameters, rules, data_collectors=data_collectors, hooks=hooks)

if __name__ == '__main__':
    file_name = os.path.basename(__file__)
    model_name, _ = os.path.splitext(file_name)

    model.run()

    with open('output_data/hypothesis2/{}.json'.format(model_name), 'w') as file:
        json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

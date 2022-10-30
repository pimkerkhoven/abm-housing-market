import json
import os

from extensions.fixed_construction import construct_fixed_total
from extensions.tax_m2_per_person import left_over_money_with_m2_per_person_tax, M2TaxGovernment
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

Household.left_over_money = left_over_money_with_m2_per_person_tax
Houses.construct = construct_fixed_total


def linear_tax(m2_per_person):
    return m2_per_person


def linear_tax_2(m2_per_person):
    return 2 * m2_per_person


def quadratic_tax(m2_per_person):
    return 0.075 * (m2_per_person - 30) ** 2


def minimal_required_space(m2_per_person):
    if m2_per_person < 30:
        return 0

    return 0.075 * (m2_per_person - 30) ** 2


def minimal_required_space1(m2_per_person):
    if m2_per_person < 30:
        return 0

    return 0.5 * (m2_per_person - 30) ** 2


def minimal_required_space2(m2_per_person):
    if m2_per_person < 30:
        return 0

    return (m2_per_person - 30) ** 2


taxation_policies = [linear_tax_2, quadratic_tax, minimal_required_space]

file_name = os.path.basename(__file__)
first_part_model_name, _ = os.path.splitext(file_name)


def setup_government(m):
    m.government = M2TaxGovernment()


hooks = Hooks(
    post_init=[setup_government],
    end_of_year=[]
)

if __name__ == '__main__':
    for policy in taxation_policies:
        model = Runner(run_settings, parameters, Rules(m2_tax=policy),
                       data_collectors=data_collectors, collector_groups=collector_groups, hooks=hooks)

        model.run()
        model_name = "{}-policy={}".format(first_part_model_name, policy.__name__)

        with open('output_data/hypothesis1/{}.json'.format(model_name), 'w') as file:
            json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

import json
import os

from extensions.fixed_construction import construct_fixed_total
from extensions.house_sharing import ShareMarket, count_houses_under_sharing, current_share_utility, share_utility, \
    calculate_sharing_utility, decide_to_share, set_new_tax_rate_sharing, size_of_sharing_household
from extensions.tax_m2_per_person import left_over_money_with_m2_per_person_tax, M2TaxGovernment
from model.agents.government import Government
from model.agents.household import Household
from model.constants import MIN_RENTAL_PRICE
from model.containers.houses import Houses
from model.model import Hooks
from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.utility_functions import default_utility_function, MultiplyQualityRootSizeUtility
from policies.hypothesis1.m2_tax_model import minimal_required_space
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors, \
    collector_groups

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])


def make_rental_market_share_market(m):
    m.rental_market = ShareMarket(*parameters.rent_market_price_params, min_price=MIN_RENTAL_PRICE)


Household.left_over_money = left_over_money_with_m2_per_person_tax

Houses.count_houses = count_houses_under_sharing
Houses.construct = construct_fixed_total
Household.current_utility = current_share_utility
Household.utility = share_utility
Household.size_of_sharing_household = size_of_sharing_household
MultiplyQualityRootSizeUtility.__call__ = calculate_sharing_utility
M2TaxGovernment.set_new_tax_rate = set_new_tax_rate_sharing


def setup_government(m):
    m.government = M2TaxGovernment()


hooks = Hooks(
    post_init=[make_rental_market_share_market, setup_government],
    end_of_year=[decide_to_share]
)


model = Runner(run_settings, parameters, Rules(m2_tax=minimal_required_space),
               data_collectors=data_collectors, collector_groups=collector_groups, hooks=hooks)

if __name__ == '__main__':
    file_name = os.path.basename(__file__)
    model_name, _ = os.path.splitext(file_name)

    model.run()

    with open('output_data/hypothesis1/{}.json'.format(model_name), 'w') as file:
        json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

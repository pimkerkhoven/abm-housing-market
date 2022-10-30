import json
import os

from extensions.fixed_construction import construct_fixed_total
from extensions.house_splitting import decide_to_split, set_new_tax_rate_splitting
from extensions.tax_m2_per_person import M2TaxGovernment
from model.agents.government import Government
from model.agents.household import Household
from model.constants import ESSENTIAL_COSTS
from model.containers.houses import Houses
from model.model import Hooks
from model.runner.runner import RunSettings, Parameters, Runner, Rules
from model.util.injector import inject
from model.utility_functions import default_utility_function
from policies.hypothesis1.m2_tax_model import minimal_required_space
from policies.run_settings import START_YEAR, END_YEAR, SCALE_FACTOR, CALIBRATION_LENGTH, NUMBER_OF_RUNS, data_collectors, \
    collector_groups

run_settings = RunSettings(start_year=START_YEAR, end_year=END_YEAR, scale_factor=SCALE_FACTOR,
                           calibration_length=CALIBRATION_LENGTH, number_of_runs=NUMBER_OF_RUNS)

# TODO: want to move penalty should be function that takes a household?
parameters = Parameters(default_utility_function, buy_market_price_params=[250, 1500, 180000],
                        rent_market_price_params=[4, 8, 150])


@inject("rules", "government")
def left_over_money_under_splitting_and_m2_tax(self, housing_costs, house, rules, government):
    rent_income = 0
    bonus = 0
    if hasattr(self, 'owns'):
        for house in self.owns:
            if house.renter is not None:
                rent_income += house.renter.contract.get_costs()
                bonus += rules.split_bonus

    m2_per_person = house.size / self.size

    allowance = government.determine_rent_allowance(self, housing_costs, house)
    tax = self.income * government.tax_rate if self.income > 0 else 0
    left_over = self.income + bonus + rent_income - rules.m2_tax(m2_per_person) - ESSENTIAL_COSTS - housing_costs \
                + allowance - tax

    if left_over > 0:
        spend = round(2 * left_over ** 0.75)
        return left_over - spend

    return left_over


Household.left_over_money = left_over_money_under_splitting_and_m2_tax
Houses.construct = construct_fixed_total
M2TaxGovernment.set_new_tax_rate = set_new_tax_rate_splitting


def add_split_count_to_houses(m):
    m.houses.split_count = 0


def setup_government(m):
    m.government = M2TaxGovernment()


hooks = Hooks(
    post_create_houses=[add_split_count_to_houses, setup_government],
    end_of_year=[decide_to_split]
)

model = Runner(run_settings, parameters, Rules(m2_tax=minimal_required_space), data_collectors=data_collectors,
               collector_groups=collector_groups, hooks=hooks)

if __name__ == '__main__':
    file_name = os.path.basename(__file__)
    model_name, _ = os.path.splitext(file_name)

    model.run()

    with open('output_data/hypothesis1/{}.json'.format(model_name), 'w') as file:
        json.dump(model.runs, file)

# Store output_data in file!!
# for each data collector store output_data in file

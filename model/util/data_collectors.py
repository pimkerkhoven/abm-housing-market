import math
from statistics import mean

import numpy as np

from extensions.house_sharing import ShareHouse
from model.agents.house import SocialHouse, RentalHouse, BuyHouse
from model.util.contracts import Homeless, BuyingContract


def _mean_calc_helper(data):
    if len(data) > 0:
        return mean(data)

    return np.nan


def _get_buy_transactions(model):
    result = []
    if model.year in model.buying_market.transaction_log:
        for month in model.buying_market.transaction_log[model.year]:
            result += model.buying_market.transaction_log[model.year][month]

    return result


def _get_rental_transactions(model):
    result = []
    if model.year in model.rental_market.transaction_log:
        for month in model.rental_market.transaction_log[model.year]:
            result += model.rental_market.transaction_log[model.year][month]

    return result


def mean_buy_transaction_value(group_filter, model):
    transactions = _get_buy_transactions(model)
    filtered_transactions = [t for t in transactions if group_filter(model.households[t.by])]

    return _mean_calc_helper([t.value for t in filtered_transactions])


mean_buy_transaction_value.__title__ = "Average transaction value"
mean_buy_transaction_value.__chart_type__ = "line"
mean_buy_transaction_value.__ylabel__ = "Price in euros"


def count_buy_transactions(group_filter, model):
    transactions = _get_buy_transactions(model)
    filtered_transactions = [t for t in transactions if group_filter(model.households[t.by])]

    return len(filtered_transactions)


count_buy_transactions.__title__ = "Number of buying transactions"
count_buy_transactions.__chart_type__ = "line"
count_buy_transactions.__ylabel__ = "Number of transactions"


def mean_rental_transaction_value(group_filter, model):
    transactions = _get_rental_transactions(model)
    filtered_transactions = [t for t in transactions if group_filter(model.households[t.by])]

    return _mean_calc_helper([t.value for t in filtered_transactions])


mean_rental_transaction_value.__title__ = "Average price of rental transactions"
mean_rental_transaction_value.__chart_type__ = "line"
mean_rental_transaction_value.__ylabel__ = "Price in euros"


def count_rental_transactions(group_filter, model):
    transactions = _get_rental_transactions(model)
    filtered_transactions = [t for t in transactions if group_filter(model.households[t.by])]

    return len(filtered_transactions)


count_rental_transactions.__title__ = "Number of rental transactions"
count_rental_transactions.__chart_type__ = "line"
count_rental_transactions.__ylabel__ = "Number of transactions"


def count_households(group_filter, model):
    return len([h for h in model.households.values() if group_filter(h)])


count_households.__title__ = "Number of households"
count_households.__chart_type__ = "line"
count_households.__ylabel__ = "Number of households"


def count_houses(_group_filter, model):
    return model.houses.count_houses()


count_houses.__title__ = "Number of houses"
count_houses.__chart_type__ = "line"
count_houses.__ylabel__ = "Number of houses"


def housing_shortage(_group_filter, model):
    return model.houses.calculate_housing_shortage()


housing_shortage.__title__ = "Housing shortage"
housing_shortage.__chart_type__ = "line"
housing_shortage.__multiplier__ = 100
housing_shortage.__ylabel__ = "Shortage percentage"


def household_size_helper(household):
    if hasattr(household, 'size_of_sharing_household'):
        return household.size + household.size_of_sharing_household()

    return household.size


def mean_m2_per_person(group_filter, model):
    return _mean_calc_helper([h.contract.house.size / household_size_helper(h)
                              for h in model.households.values() if group_filter(h)])


mean_m2_per_person.__title__ = "Average $m^2$ per person"
mean_m2_per_person.__chart_type__ = "line"
mean_m2_per_person.__ylabel__ = "$m^2$ per person"


def mean_utility(group_filter, model):
    return _mean_calc_helper([h.current_utility() for h in model.households.values() if group_filter(h)])


mean_utility.__title__ = "Average utility"
mean_utility.__chart_type__ = "line"
mean_utility.__ylabel__ = "Utility"


def count_want_to_move(group_filter, model):
    return len([h for h in model.households.values() if h.contract.want_to_move if group_filter(h)])


count_want_to_move.__title__ = "Number of households that want to move"
count_want_to_move.__chart_type__ = "line"
count_want_to_move.__ylabel__ = "Number of households"


def mean_want_to_move_time(group_filter, model):
    return _mean_calc_helper(
        [h.contract.want_to_move_time for h in model.households.values() if group_filter(h)])


mean_want_to_move_time.__title__ = "Average want to move time"
mean_want_to_move_time.__chart_type__ = "line"
mean_want_to_move_time.__ylabel__ = "Months"

def average_number_of_moves(group_filter, model):
    return _mean_calc_helper([len(h.history) for h in model.households.values() if group_filter(h)])


average_number_of_moves.__title__ = "Average times a household moves"
average_number_of_moves.__chart_type__ = "line"
average_number_of_moves.__ylabel__ = "Number of moves"

def calculate_cost_of_living(group_filter, model):
    return _mean_calc_helper([h.contract.get_costs() for h in model.households.values() if group_filter(h)])


calculate_cost_of_living.__title__ = "Average cost of living"
calculate_cost_of_living.__chart_type__ = "line"
calculate_cost_of_living.__ylabel__ = "Cost in euros"


def calculate_cost_of_living_buying(group_filter, model):
    return _mean_calc_helper([h.contract.get_costs() for h in model.households.values()
                              if isinstance(h.contract, BuyingContract) and group_filter(h)])


calculate_cost_of_living_buying.__title__ = "Average mortgage cost"
calculate_cost_of_living_buying.__chart_type__ = "line"
calculate_cost_of_living_buying.__ylabel__ = "Cost in euros"


def calculate_cost_of_living_rental(group_filter, model):
    return _mean_calc_helper([h.contract.get_costs() for h in model.households.values()
                              if group_filter(h) and not isinstance(h.contract, BuyingContract)
                              and not isinstance(h.contract, Homeless)])


calculate_cost_of_living_rental.__title__ = "Average rent"
calculate_cost_of_living_rental.__chart_type__ = "line"
calculate_cost_of_living_rental.__ylabel__ = "Cost in euros"

def mean_age_home_owners(group_filter, model):
    return _mean_calc_helper([h.age for h in model.households.values()
                              if group_filter(h) and isinstance(h.contract, BuyingContract)])


mean_age_home_owners.__title__ = "Average age of homeowners"
mean_age_home_owners.__chart_type__ = "line"
mean_age_home_owners.__ylabel__ = "Years"


def count_social_houses(_group_filter, model):
    return len([h for h in model.houses.values() if isinstance(h, SocialHouse)])


count_social_houses.__title__ = "Number of social houses"
count_social_houses.__chart_type__ = "line"
count_social_houses.__ylabel__ = "Number of houses"


def count_home_owners(group_filter, model):
    return len([h for h in model.households.values() if group_filter(h) and isinstance(h.contract, BuyingContract)])


count_home_owners.__title__ = "Number of home owners"
count_home_owners.__chart_type__ = "line"
count_home_owners.__ylabel__ = "Number of households"


def mean_income_percentile_owners(group_filter, model):
    return _mean_calc_helper(
        [h.income_percentile for h in model.households.values()
         if group_filter(h) and isinstance(h.contract, BuyingContract)])


mean_income_percentile_owners.__title__ = "Average income percentile of owners"
mean_income_percentile_owners.__chart_type__ = "line"
mean_income_percentile_owners.__ylabel__ = "Income percentile"


def count_shared_houses(_group_filter, model):
    return len([h for h in model.houses.values() if isinstance(h, ShareHouse)])


count_shared_houses.__title__ = "Number of shared houses"
count_shared_houses.__chart_type__ = "line"
count_shared_houses.__ylabel__ = "Number of houses"


def count_homeless(group_filter, model):
    return len([h for h in model.households.values() if group_filter(h) and isinstance(h.contract, Homeless)])


count_homeless.__title__ = "Number of homeless households"
count_homeless.__chart_type__ = "line"
count_homeless.__ylabel__ = "Number of households"


def count_split_houses(_group_filter, model):
    if hasattr(model.houses, 'split_count'):
        return model.houses.split_count

    return 0


count_split_houses.__title__ = "Number of split houses"
count_split_houses.__chart_type__ = "line"
count_split_houses.__ylabel__ = "Number of houses"

# def mean_utility_in_social_housing(model):
#     return _mean_calc_helper(
#         [h.current_utility() for h in model.households.values() if isinstance(h.contract.house, SocialHouse)])
#
#
# mean_utility_in_social_housing.__title__ = "Average utility in social housing"
# mean_utility_in_social_housing.__chart_type__ = "line"


def tax_rate(_group_filter, model):
    return model.government.tax_rate


tax_rate.__title__ = "Tax rate"
tax_rate.__chart_type__ = "line"
tax_rate.__ylabel__ = "Rate"


def mean_private_sector_rent(group_filter, model):
    return _mean_calc_helper([h.contract.get_costs() for h in model.households.values()
                              if group_filter(h) and isinstance(h.contract.house, RentalHouse)])


mean_private_sector_rent.__title__ = "Rent private sector"
mean_private_sector_rent.__chart_type__ = "line"
mean_private_sector_rent.__ylabel__ = "Rent in euros"


def mean_social_sector_rent(group_filter, model):
    return _mean_calc_helper([h.contract.get_costs() for h in model.households.values()
                              if group_filter(h) and isinstance(h.contract.house, SocialHouse)])


mean_social_sector_rent.__title__ = "Rent social sector"
mean_social_sector_rent.__chart_type__ = "line"
mean_social_sector_rent.__ylabel__ = "Rent in euros"


def mean_left_over_money(group_filter, model):
    return _mean_calc_helper([h.left_over_money(h.contract.get_costs(), h.contract.house)
                              for h in model.households.values() if group_filter(h)])


mean_left_over_money.__title__ = "Average saved money"
mean_left_over_money.__chart_type__ = "line"
mean_left_over_money.__ylabel__ = "Money in euros"


def count_unused_houses(_group_filter, model):
    return [len(model.buying_market.listings), len(model.rental_market.listings)]


count_unused_houses.__title__ = "Number of unused houses"
count_unused_houses.__chart_type__ = "bar"
count_unused_houses.bar_labels = ["buy", "rent"]
count_unused_houses.__ylabel__ = "Number of houses"


def average_size_of_unused_houses(_group_filter, model):
    buying_sizes = [l.house.size for l in model.buying_market.listings.values()]
    rental_sizes = [l.house.size for l in model.rental_market.listings.values()]

    return _mean_calc_helper([*buying_sizes, *rental_sizes])


average_size_of_unused_houses.__title__ = "Average size of unused houses"
average_size_of_unused_houses.__chart_type__ = "line"
average_size_of_unused_houses.__ylabel__ = "Size in $m^2$"


def count_houses_by_type(_group_filter, model):
    buy_houses = 0
    private_rental_houses = 0
    social_rental_houses = 0
    shared_houses = 0

    for house in model.houses.values():
        if isinstance(house, BuyHouse):
            buy_houses += 1
        elif isinstance(house, RentalHouse):
            private_rental_houses += 1
        elif isinstance(house, SocialHouse):
            social_rental_houses += 1
        elif isinstance(house, ShareHouse):
            shared_houses += 1

    return [buy_houses, private_rental_houses, social_rental_houses, shared_houses]


count_houses_by_type.__title__ = "Number of houses by type"
count_houses_by_type.__chart_type__ = "bar"
count_houses_by_type.bar_labels = ["buy", "private rent", "social rent", "shared"]
count_houses_by_type.__ylabel__ = "Number of houses"


def liberalisation_threshold(_group_filter, model):
    return model.government.liberalisation_threshold


liberalisation_threshold.__title__ = "Liberalisation threshold"
liberalisation_threshold.__chart_type__ = "line"
liberalisation_threshold.__ylabel__ = "Threshold in euros"

year_for_size_pp_histogram = 2060


def size_per_person_distribution(group_filter, model):
    if model.year == year_for_size_pp_histogram:
        return [h.contract.house.size / household_size_helper(h)
                for h in model.households.values() if group_filter(h)]


size_per_person_distribution.__title__ = "Size per person distribution"
size_per_person_distribution.__chart_type__ = "hist"
size_per_person_distribution.__year__ = year_for_size_pp_histogram
size_per_person_distribution.__bins__ = [x * 25 for x in range(21)] # [0, 10, 25, 50, 75, 100, 150, 250, 500]
size_per_person_distribution.__xlabel__ = "Size per person"
size_per_person_distribution.__ylabel__ = "Number of households"


def house_score(house, sharing=False):
    if sharing:
        return math.sqrt(house.size / 2) * house.quality

    return math.sqrt(house.size) * house.quality


def fairness_score(group_filter, model):
    high_income_median_house_score = np.median([house_score(h.contract.house) for h in
                                                model.households.values() if
                                                group_filter(h) and h.income_percentile > 0.66])

    low_income_median_house_score = np.median([house_score(h.contract.house) for h in
                                               model.households.values() if
                                               group_filter(h) and h.income_percentile <= 0.33])

    if low_income_median_house_score > 0:
        return high_income_median_house_score / low_income_median_house_score

    return np.nan


fairness_score.__title__ = "Fairness score"
fairness_score.__chart_type__ = "line"
fairness_score.__ylabel__ = "Score"


def mean_want_to_move_time_wanting_to_move(group_filter, model):
    return _mean_calc_helper(
        [h.contract.want_to_move_time for h in model.households.values() if
         group_filter(h) and h.contract.want_to_move])


mean_want_to_move_time_wanting_to_move.__title__ = "Average want to move time of wanting to move"
mean_want_to_move_time_wanting_to_move.__chart_type__ = "line"
mean_want_to_move_time_wanting_to_move.__ylabel__ = "Months"


def actual_wait_time(group_filter, model):
    buy_transactions = _get_buy_transactions(model)
    filtered_buy_transactions = [t for t in buy_transactions if group_filter(model.households[t.by])]
    rental_transactions = _get_rental_transactions(model)
    filtered_rental_transactions = [t for t in rental_transactions if group_filter(model.households[t.by])]

    buy_wait_times = [t.wait_time for t in filtered_buy_transactions if t.wait_time >= 0]
    rent_wait_times = [t.wait_time for t in filtered_rental_transactions if t.wait_time >= 0]
    active_wait_times = [h.contract.want_to_move_time for h in model.households.values()
                         if group_filter(h) and h.contract.want_to_move]

    wait_times = [*buy_wait_times, *rent_wait_times, *active_wait_times]

    return _mean_calc_helper(wait_times)


actual_wait_time.__title__ = "Average want to move time"
actual_wait_time.__chart_type__ = "line"
actual_wait_time.__ylabel__ = "Months"


def buy_price_prediction(_group_filter, model):
    price = model.buying_market._get_market_prices([[120, 5]])[0]

    return price


buy_price_prediction.__title__ = "Market buying price of reference house"
buy_price_prediction.__chart_type__ = "line"
buy_price_prediction.__ylabel__ = "Price in euros"
buy_price_prediction.__figsize__ = (10.5, 7.5)


def house_score_distribution(_group_filter, model):
    if model.year == year_for_size_pp_histogram:
        # TODO: account for share houses
        non_sharing_houses = [house_score(h) for h in model.houses.values() if not isinstance(h, ShareHouse)]
        sharing_houses = [house_score(h, sharing=True) for h in model.houses.values() if isinstance(h, ShareHouse)] * 2

        return non_sharing_houses + sharing_houses


house_score_distribution.__title__ = "House score distribution"
house_score_distribution.__chart_type__ = "hist"
house_score_distribution.__year__ = year_for_size_pp_histogram
house_score_distribution.__bins__ = 20  # [0, 50, 100, 150, 200, 250, 300]
house_score_distribution.__xlabel__ = "Score"
house_score_distribution.__ylabel__ = "Number of houses"


def house_size_distribution(_group_filter, model):
    if model.year == year_for_size_pp_histogram:
        # TODO: account for share houses
        non_sharing_houses = [h.size for h in model.houses.values() if not isinstance(h, ShareHouse)]
        sharing_houses = [h.size / 2 for h in model.houses.values() if isinstance(h, ShareHouse)] * 2

        return non_sharing_houses + sharing_houses


house_size_distribution.__title__ = "House size distribution"
house_size_distribution.__chart_type__ = "hist"
house_size_distribution.__year__ = year_for_size_pp_histogram
house_size_distribution.__bins__ = 20 #[0, 50, 100, 150, 200, 250, 300, 800]
house_size_distribution.__xlabel__ = "House size in $m^2$"
house_size_distribution.__ylabel__ = "Number of houses"


def buy_house_size_distribution(_group_filter, model):
    if model.year == year_for_size_pp_histogram:
        return [h.size for h in model.houses.values() if isinstance(h, BuyHouse)]


buy_house_size_distribution.__title__ = "Buy House size distribution"
buy_house_size_distribution.__chart_type__ = "hist"
buy_house_size_distribution.__year__ = year_for_size_pp_histogram
buy_house_size_distribution.__bins__ = 20 # [0, 50, 100, 150, 200, 250, 300, 800]
buy_house_size_distribution.__xlabel__ = "House size in $m^2$"
buy_house_size_distribution.__ylabel__ = "Number of houses"

# bins in data [0,15,50,75,100,150,250,500,10_000]


def rental_house_size_distribution(_group_filter, model):
    if model.year == year_for_size_pp_histogram:
        # TODO: account for share houses
        non_sharing_houses = [h.size for h in model.houses.values() if
                              isinstance(h, SocialHouse) or isinstance(h, RentalHouse)]
        sharing_houses = [h.size / 2 for h in model.houses.values() if isinstance(h, ShareHouse)] * 2

        return non_sharing_houses + sharing_houses


rental_house_size_distribution.__title__ = "Rental House size distribution"
rental_house_size_distribution.__chart_type__ = "hist"
rental_house_size_distribution.__year__ = year_for_size_pp_histogram
rental_house_size_distribution.__bins__ = 20
rental_house_size_distribution.__xlabel__ = "House size in $m^2$"
rental_house_size_distribution.__ylabel__ = "Number of houses"


def total_unused_space(_group_filter, model):
    total = 0
    for listing in model.buying_market.listings.values():
        total += listing.house.size

    for listing in model.rental_market.listings.values():
        if not isinstance(listing.house, ShareHouse):
            total += listing.house.size

    return total


total_unused_space.__title__ = "Total unused space"
total_unused_space.__chart_type__ = "line"
total_unused_space.__ylabel__ = "Space in $m^2$"

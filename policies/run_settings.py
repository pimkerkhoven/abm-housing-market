import model.util.data_collectors as dc
import model.util.individual_collectors as ic

START_YEAR = 2012
END_YEAR = 2061
CALIBRATION_LENGTH = 100
SCALE_FACTOR = 12_500
NUMBER_OF_RUNS = 50

collector_groups = [
    ('all', lambda h: True),
    # ('poor_young_family', lambda h: h.size > 2 and h.income_percentile <= 0.33 and h.age < 50),
    # ('rich_young_family', lambda h: h.size > 2 and h.income_percentile >= 0.66 and h.age < 50),
    # ('rich_single', lambda h: h.size == 1 and h.income_percentile >= 0.8),
    # ('elderly_couple', lambda h: h.size == 2 and h.age >= 50),
    # ('starters', lambda h: h.age <= 35),
    # ('pensioners', lambda h: h.age >= 60),
    # ('super_poor', lambda h: h.income_percentile <= 0.2),
    # ('poor', lambda h: 0.2 < h.income_percentile <= 0.4),
    # ('middle', lambda h: 0.4 < h.income_percentile <= 0.6),
    # ('rich', lambda h: 0.6 < h.income_percentile <= 0.8),
    # ('super_rich', lambda h: 0.8 < h.income_percentile <= 1.0),
]

data_collectors = [
    dc.mean_buy_transaction_value,
    dc.count_buy_transactions,
    dc.mean_rental_transaction_value,
    dc.count_rental_transactions,
    dc.count_households,
    dc.count_houses,
    dc.housing_shortage,
    dc.mean_m2_per_person,
    dc.mean_utility,
    dc.count_want_to_move,
    # dc.mean_want_to_move_time,
    # dc.average_number_of_moves,
    dc.calculate_cost_of_living,
    dc.calculate_cost_of_living_buying,
    dc.calculate_cost_of_living_rental,
    # dc.mean_age_home_owners,
    # dc.count_social_houses,
    # dc.count_home_owners,
    # dc.mean_income_percentile_owners,
    dc.count_shared_houses,
    dc.count_homeless,
    dc.count_split_houses,
    # dc.tax_rate,
    # dc.mean_private_sector_rent,
    # dc.mean_social_sector_rent,
    dc.mean_left_over_money,
    dc.count_unused_houses,
    dc.average_size_of_unused_houses,
    dc.count_houses_by_type,
    # dc.liberalisation_threshold,
    dc.size_per_person_distribution,
    # dc.mean_want_to_move_time_wanting_to_move,
    dc.actual_wait_time,
    dc.buy_price_prediction,
    dc.house_size_distribution,
    # dc.house_score_distribution,
    dc.buy_house_size_distribution,
    dc.rental_house_size_distribution,
    dc.total_unused_space
]

individual_collectors = [
    ic.size,
    ic.age,
    ic.income,
    ic.house_size,
    ic.utility,
    ic.house_quality,
    ic.wealth,
    ic.size_per_person,
    ic.contract_cost
]
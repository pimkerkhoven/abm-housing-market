import random
from statistics import mean

from model.agents.house import RentalHouse, SocialHouse, BuyHouse
from model.constants import MONTHS
from model.util.injector import inject

SPLIT_COST = 50_000

COUNTER = {'split_houses_cost_current_year': 0}


@inject("households")
def set_new_tax_rate_splitting(self, households):
    total_rent_allowance_per_month = sum([self.determine_rent_allowance(h, h.contract.get_costs(), h.contract.house)
                                              for h in households.values()])
    total_income_per_month = sum([h.income for h in households.values() if h.income > 0])
    max_splitting_bonus_per_month = (COUNTER['split_houses_cost_current_year']) / len(MONTHS)

    self.tax_rate = (total_rent_allowance_per_month + max_splitting_bonus_per_month) / total_income_per_month

    COUNTER['split_houses_cost_current_year'] = 0


def split_houses_on_buying_market(model, average_household_size):
    for listing in list([l for l in model.buying_market.listings.values()
                         if l.house.size / average_household_size > model.rules.m2_per_person_limit]):
        house = listing.house
        COUNTER['split_houses_cost_current_year'] += SPLIT_COST

        if house.owner:
            house.owner.sell(listing.value)
            house.owner = None
            COUNTER['split_houses_cost_current_year'] += listing.value

        model.buying_market.listings.pop(house.id)

        split_ratio = max(0.15, min(0.85, random.random()))
        old_size = house.size
        new_size = round(house.size * split_ratio)

        house.size = new_size

        other_part = BuyHouse(old_size - new_size, house.quality)
        model.houses.add(other_part)

        model.buying_market.list(house)
        model.buying_market.list(other_part)


def split_houses_on_rental_market(model, average_household_size):
    for listing in list([l for l in model.rental_market.listings.values()
                         if l.house.size / average_household_size > model.rules.m2_per_person_limit]):
        house = listing.house
        COUNTER['split_houses_cost_current_year'] += SPLIT_COST

        model.rental_market.listings.pop(house.id)

        split_ratio = max(0.15, min(0.85, random.random()))
        old_size = house.size
        new_size = round(house.size * split_ratio)

        if isinstance(house, SocialHouse):
            house = RentalHouse(new_size, house.quality)
            house.id = house.id
            model.houses.update(house)
        else:
            house.size = new_size

        other_part = RentalHouse(old_size - new_size, house.quality)
        model.houses.add(other_part)

        model.rental_market.list(house)
        model.rental_market.list(other_part)


def split_houses_hook(model):
    average_household_size = mean([h.size for h in model.households.values()])

    split_houses_on_buying_market(model, average_household_size)
    split_houses_on_rental_market(model, average_household_size)

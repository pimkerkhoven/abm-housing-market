import math

from model.agents.market import Option
from model.constants import MONTHS
from model.util.injector import inject


@inject("bank", "rules")
def get_best_option_from_market_with_m2_prohibition(self, household, bank, rules):
    max_bid = bank.max_bid(household)
    brochure = self.get_brochure(max_bid)
    best_option = Option(None, -math.inf)

    for listing in brochure:
        m2_per_person = listing.house.size / household.size

        if m2_per_person > rules.m2_per_person_limit:
            continue

        _, monthly_payment = bank.value_to_monthly_payment(listing.value, household)

        listing_utility = household.utility(listing.house, monthly_payment)
        if listing_utility > best_option.utility:
            best_option = Option(listing.house, listing_utility)

    return best_option


@inject("rules")
def get_best_non_social_rent_option_with_m2_prohibition(self, household, rules):
    brochure = self.get_brochure()
    best_option = Option(None, -math.inf)

    for listing in brochure:
        m2_per_person = listing.house.size / household.size

        if m2_per_person > rules.m2_per_person_limit:
            continue

        listing_utility = household.utility(listing.house, listing.value)
        if listing_utility > best_option.utility:
            best_option = Option(listing.house, listing_utility)

    return best_option


@inject("rules")
def get_best_social_rent_option_with_m2_prohibition(self, household, rules):
    brochure = self.get_social_brochure(household.income * len(MONTHS), household.size)
    best_option = Option(None, -math.inf)

    for listing in brochure:
        m2_per_person = listing.house.size / household.size

        if m2_per_person > rules.m2_per_person_limit:
            continue

        listing_utility = household.utility(listing.house, listing.value)
        if listing_utility > best_option.utility:
            best_option = Option(listing.house, listing_utility)

    return best_option

import collections
import math
import random

import numpy as np
from sklearn.linear_model import LinearRegression

from model.agents.house import SocialHouse, RentalHouse
from model.constants import BROCHURE_SIZE, N_LAST_TRANSACTIONS, NEW_LIST_PRICE_FACTOR, \
    LIST_PRICE_UPDATE_FACTOR, MONTHS
from model.util.injector import inject

Listing = collections.namedtuple('Listing', ['house', 'value'])
Transaction = collections.namedtuple('Transaction', ['house_id', 'size', 'quality', 'value', 'wait_time', 'by', 'sector'])
Option = collections.namedtuple('Option', ['house', 'utility'])


class SocialListing:
    def __init__(self, house, value):
        self.house = house
        self.value = value
        self.no_income_limit = random.random() < 0.15


class Market:
    def __init__(self, size_weight, quality_weight, intercept=0, min_price=0, max_price=math.inf):
        self.listings = {}

        self.new_houses_for_listings = []
        self.min_price = min_price
        self.max_price = max_price

        self.market_price_regression_model = LinearRegression()
        self.market_price_regression_model.coef_ = np.array([size_weight, quality_weight])
        self.market_price_regression_model.intercept_ = intercept

        self.transaction_log = {}

    def fit_market_price_parameters(self):
        if len(self.transaction_log) == 0:
            return

        transactions_to_fit_on = self._get_last_transactions(N_LAST_TRANSACTIONS)
        input_data = [[t.size, t.quality] for t in transactions_to_fit_on]
        output_data = [t.value for t in transactions_to_fit_on]

        self.market_price_regression_model.fit(input_data, output_data)

    def list(self, house):
        if house.id in self.listings:
            return

        self.new_houses_for_listings.append(house)

    def update(self):
        self._update_prices()
        self._process_new_listings()

    def transact(self, house_id, by, wait_time, log_transaction=True):
        listing = self.listings.pop(house_id)

        if log_transaction:
            self._add_transaction_to_log(Transaction(house_id=listing.house.id, size=listing.house.size,
                                                     quality=listing.house.quality, value=listing.value,
                                                     sector=type(listing.house).__name__,
                                                     wait_time=wait_time,
                                                     by=by))

    @inject("year", "month")
    def _add_transaction_to_log(self, transaction, year, month):
        if year not in self.transaction_log:
            self.transaction_log[year] = {}
        if month not in self.transaction_log[year]:
            self.transaction_log[year][month] = []

        self.transaction_log[year][month].append(transaction)

    def _get_last_transactions(self, number_of_transactions):
        result = []

        for year_log in self.transaction_log.values():
            for month_log in year_log.values():
                result += month_log

        return result[-number_of_transactions:]

    def _get_market_prices(self, data):
        if len(data) == 0:
            return []

        prices = self.market_price_regression_model.predict(data)
        return list(map(lambda price: round(min(self.max_price, max(self.min_price, price))), prices))

    def _process_new_listings(self):
        house_data = [[house.size, house.quality] for house in self.new_houses_for_listings]
        market_prices = self._get_market_prices(house_data)

        for index, house in enumerate(self.new_houses_for_listings):
            value = max(self.min_price, round(market_prices[index] * NEW_LIST_PRICE_FACTOR))
            self.listings[house.id] = Listing(house, value)

        self.new_houses_for_listings = []

    def _update_prices(self):
        for house_id in self.listings:
            listing = self.listings[house_id]
            new_value = round(LIST_PRICE_UPDATE_FACTOR * listing.value)
            self.listings[house_id] = listing._replace(value=new_value)


class BuyingMarket(Market):
    @inject("bank")
    def get_best_option_from_market(self, household, bank):
        max_bid = bank.max_bid(household)
        brochure = self.get_brochure(max_bid)
        best_option = Option(None, -math.inf)

        for listing in brochure:
            _, monthly_payment = bank.value_to_monthly_payment(listing.value, household)

            listing_utility = household.utility(listing.house, monthly_payment)
            if listing_utility > best_option.utility:
                best_option = Option(listing.house, listing_utility)

        return best_option

    def get_brochure(self, max_bid):
        if BROCHURE_SIZE > len(self.listings):
            brochure = list(self.listings.values())
        else:
            brochure = random.sample(list(self.listings.values()), BROCHURE_SIZE)

        return list(filter(lambda listing: listing.value <= max_bid, brochure))


class SocialMarket(Market):
    @inject("houses", "government")
    def list_social_house(self, house, houses, government):
        if house.value <= government.liberalisation_threshold:
            self.listings[house.id] = SocialListing(house=house, value=house.value)
        else:
            rental_house = RentalHouse(house.size, house.quality)
            rental_house.id = house.id
            houses.update(rental_house)

            self.new_houses_for_listings.append(rental_house)

    def update(self):
        super().update()
        self._assign_social_housing()

    def _assign_social_housing(self):
        social_listings_with_interest = list(filter(lambda l: isinstance(l.house, SocialHouse)
                                                              and len(l.house.interested) > 0,
                                                    self.listings.values()))

        for listing in social_listings_with_interest:
            longest_waiting_household = max(listing.house.interested, key=lambda household: household.wait_list_time)
            listing.house.move_in(longest_waiting_household)

    @inject("houses", "government")
    def _process_new_listings(self, houses, government):
        new_houses = self.new_houses_for_listings
        super()._process_new_listings()

        for house in new_houses:
            value = self.listings[house.id].value
            if value <= government.liberalisation_threshold:
                social_house = SocialHouse(house, value)
                self.listings[social_house.id] = SocialListing(house=social_house, value=value)
                houses.update(social_house)

    def _update_prices(self):
        for house_id in self.listings:
            listing = self.listings[house_id]
            if isinstance(listing.house, RentalHouse):
                new_value = round(LIST_PRICE_UPDATE_FACTOR * listing.value)
                self.listings[house_id] = listing._replace(value=new_value)

    def get_brochure(self):
        private_sector_listings = list(
            filter(lambda listing: isinstance(listing.house, RentalHouse), self.listings.values()))

        if BROCHURE_SIZE >= len(private_sector_listings):
            return private_sector_listings

        return random.sample(private_sector_listings, BROCHURE_SIZE)

    @inject("rules")
    def get_social_brochure(self, year_income, household_size, rules):
        if (household_size == 1 and year_income > rules.max_income_one_person_household)\
                or (household_size > 1 and year_income > rules.max_income_multi_person_household):
            social_sector_listings = list(
                filter(lambda listing: isinstance(listing.house, SocialHouse) and listing.no_income_limit,
                       self.listings.values()))
        else:
            social_sector_listings = list(
                filter(lambda listing: isinstance(listing.house, SocialHouse), self.listings.values()))

        if BROCHURE_SIZE > len(social_sector_listings):
            return social_sector_listings
        else:
            return random.sample(social_sector_listings, BROCHURE_SIZE)

    def get_best_option_from_market(self, household):
        best_private_option = self.get_best_non_social_rent_option(household)
        best_social_option = self.get_best_social_rent_option(household)

        return max(best_private_option, best_social_option, key=lambda option: option.utility)

    def get_best_non_social_rent_option(self, household):
        brochure = self.get_brochure()
        best_option = Option(None, -math.inf)

        for listing in brochure:
            listing_utility = household.utility(listing.house, listing.value)
            if listing_utility > best_option.utility:
                best_option = Option(listing.house, listing_utility)

        return best_option

    def get_best_social_rent_option(self, household):
        brochure = self.get_social_brochure(household.income * len(MONTHS), household.size)
        best_option = Option(None, -math.inf)

        for listing in brochure:
            listing_utility = household.utility(listing.house, listing.value)
            if listing_utility > best_option.utility:
                best_option = Option(listing.house, listing_utility)

        return best_option

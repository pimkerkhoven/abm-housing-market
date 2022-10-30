import collections
import math
import random

from model.agents.house import House, RentalHouse, SocialHouse
from model.agents.market import SocialMarket, Option, SocialListing
from model.constants import LIST_PRICE_UPDATE_FACTOR, BROCHURE_SIZE
from model.util.contracts import RentalContract, NoHouse
from model.util.injector import inject

ShareListing = collections.namedtuple('ShareListing', ['house', 'value', 'share_with'])


@inject("households", "houses", "rules")
def set_new_tax_rate_sharing(self, households, houses, rules):
    total_rent_allowance_per_month = sum([self.determine_rent_allowance(h, h.contract.get_costs(), h.contract.house)
                                              for h in households.values()])
    total_income_per_month = sum([h.income for h in households.values() if h.income > 0])
    max_share_bonus_per_month = len([h for h in houses.values() if isinstance(h, ShareHouse)]) * rules.share_bonus

    self.tax_rate = (total_rent_allowance_per_month + max_share_bonus_per_month) / total_income_per_month


def count_houses_under_sharing(self):
    shared_houses = len([h for h in self.values() if isinstance(h, ShareHouse)])
    return len(self) + shared_houses


def decide_to_share(model):
    for household in model.households.values():
        # Cannot share social house!
        if isinstance(household.contract, RentalContract): # and not isinstance(household.contract.house, SocialHouse):
            current_utility = household.current_utility()

            share_cost = round(household.contract.get_costs() / 2) - model.rules.share_bonus

            sharing_utility = household.utility(household.contract.house, share_cost,
                                                share_with_household_size=household.size)

            if sharing_utility >= current_utility:
                model.rental_market.list_for_sharing(household)


def size_of_sharing_household(self):
    share_with_household_size = 0
    if isinstance(self.contract, SharedContract):
        sharing_with = [s for s in self.contract.house.shared_by if s != self.id]

        if len(sharing_with) > 1:
            raise RuntimeError("Cannot share with more than one household!!")

        for share_with_id in sharing_with:
            share_with_household_size += self.contract.house.shared_by[share_with_id].size

    return share_with_household_size


@inject("parameters", "households")
def current_share_utility(self, _parameters, _households):
    return self.utility(self._contract.house, self._contract.get_costs(),
                        share_with_household_size=self.size_of_sharing_household())


@inject("parameters")
def share_utility(household, house, cost, parameters, share_with_household_size=0):
    return parameters.utility(household, house, cost, share_with_household_size)


def calculate_sharing_utility(self, household, house, cost, share_with_household_size):
    rum = self.normal_distribution_store.next()

    movement_cost = 0
    if not house == household.contract.house and not isinstance(household.contract.house, NoHouse):
        movement_cost = self.movement_cost
        if household.contract.run_time > 0:
            movement_cost = movement_cost * (12 / household.contract.run_time)

    homeless_penalty = 5 if isinstance(household.contract.house, NoHouse) else 0

    return self.money_weight * household.left_over_money(cost, house) \
           + self.house_size_weight * (house.size / (household.size + share_with_household_size)) ** 0.5 \
           * self.house_quality_weight * house.quality \
           - movement_cost \
           - homeless_penalty \
           + rum


class SharedContract:
    def __init__(self, cost, house, from_rental_contract=None):
        self.run_time = 0
        self._cost = cost
        self.house = house
        self.want_to_move = False
        self.want_to_move_time = 0

        if from_rental_contract is not None:
            self.run_time = from_rental_contract.run_time
            self.want_to_move = from_rental_contract.want_to_move

    def update(self, months_passed=1):
        self.run_time += months_passed

        if self.want_to_move:
            self.want_to_move_time += 1

    @inject("rules")
    def get_costs(self, rules):
        cost = self._cost / len(self.house.shared_by)

        if len(self.house.shared_by) > 1:
            return cost - rules.share_bonus

        return cost

    def to_record(self):
        return "Share", self.get_costs(), self.house.size, self.house.quality, self.house.id, type(self.house).__name__

    def __repr__(self):
        return "SharedContract({}, {}, {}, {})".format(self.run_time, self.get_costs(), self.house.id,
                                                       self.want_to_move)


def share_house_to_rental_house(share_house):
    if share_house.was_social:
        return SocialHouse(share_house, value=share_house.value)

    rental_house = RentalHouse(share_house.size, share_house.quality)
    rental_house.id = share_house.id

    return rental_house


class ShareHouse(House):
    def __init__(self, rental_house, household):
        super().__init__(rental_house.size, rental_house.quality)
        self.id = rental_house.id

        self.was_social = False
        if isinstance(rental_house, SocialHouse):
            self.value = rental_house.value
            self.was_social = True

        self.shared_by = {household.id: household}

    @inject("rental_market", "houses")
    def list(self, rental_market, houses):
        rental_house = share_house_to_rental_house(self)

        if self.id != rental_house.id:
            print("ERROR ERROR ERROR")

        houses.update(rental_house)

        if isinstance(rental_house, SocialHouse):
            # FIXME: Bug introduced here?
            rental_market.list_social_house(rental_house)
        else:
            rental_market.list(rental_house)

    @inject("rental_market")
    def move_out(self, to, by, rental_market):
        self.shared_by.pop(by.id)

        if len(self.shared_by) == 0:
            self.list()
        elif len(self.shared_by) == 1:
            rental_market.list_for_sharing(list(self.shared_by.values())[0])
        else:
            raise RuntimeError("This cannot be a possibility")

        if to is not None:
            to.move_in(by)

    @inject("rental_market")
    def move_in(self, renter, rental_market, log_transaction=True):
        if len(self.shared_by) == 2:
            raise RuntimeError("More than two households cannot share house")

        wait_time = renter.contract.want_to_move_time if renter.contract.want_to_move else -1

        self.shared_by[renter.id] = renter

        listing = rental_market.listings[self.id]
        # Here rent price of listing is converted back to original value!!
        contract = SharedContract(listing.value, self)
        renter.set_contract(contract)

        # handle contract for current sharer and new sharer
        rental_market.transact(self.id, renter.id, wait_time, log_transaction=log_transaction)


class ShareMarket(SocialMarket):
    @inject("houses", "government")
    def list_social_house(self, house, houses, government):
        if house.id in self.listings and isinstance(self.listings[house.id], ShareListing):
            self.listings.pop(house.id)

        if house.value <= government.liberalisation_threshold:
            self.listings[house.id] = SocialListing(house=house, value=house.value)
        else:
            rental_house = RentalHouse(house.size, house.quality)
            rental_house.id = house.id
            houses.update(rental_house)

            self.new_houses_for_listings.append(rental_house)

    def list(self, house):
        if house.id in self.listings and not isinstance(self.listings[house.id], ShareListing):
            return

        if house.id in self.listings and isinstance(self.listings[house.id], ShareListing):
            self.listings.pop(house.id)

        self.new_houses_for_listings.append(house)

    @inject("houses", "rules")
    def list_for_sharing(self, household, houses, rules):
        house = household.contract.house
        if house.id in self.listings:
            return

        # If household was not already sharing, convert to share house!
        if not isinstance(household.contract, SharedContract):
            house = ShareHouse(house, household)
            shared_contract = SharedContract(household.contract.get_costs(), house,
                                             from_rental_contract=household.contract)
            household.set_contract(shared_contract)

        # This cost is just for the listing and calculating the utility!!
        # TODO: what happens when a household moves out of a house listed for sharing??
        #  Complex could be source of bug in code -> Need to check
        share_cost = household.contract._cost # round(household.contract.get_costs() / 2) - rules.share_bonus
        self.listings[house.id] = ShareListing(house=house, value=share_cost, share_with=household)
        houses.update(house)

    def get_brochure(self):
        private_sector_listings = list(
            filter(lambda listing: isinstance(listing.house, RentalHouse) or isinstance(listing.house, ShareHouse),
                   self.listings.values()))

        if BROCHURE_SIZE >= len(private_sector_listings):
            return private_sector_listings

        return random.sample(private_sector_listings, BROCHURE_SIZE)

    # TODO: social housing can also be shared -> this is handled right??
    @inject("rules")
    def get_best_non_social_rent_option(self, household, rules):
        brochure = self.get_brochure()
        best_option = Option(None, -math.inf)

        for listing in brochure:
            # Cannot share with self
            if isinstance(listing, ShareListing):
                if household.id != listing.share_with.id:
                    calculation_value = listing.value / 2 - rules.share_bonus

                    listing_utility = household.utility(listing.house, calculation_value,
                                                        share_with_household_size=listing.share_with.size)
                else:
                    continue
            else:
                listing_utility = household.utility(listing.house, listing.value)

            if listing_utility > best_option.utility:
                best_option = Option(listing.house, listing_utility)

        return best_option

    def _update_prices(self):
        for house_id in self.listings:
            listing = self.listings[house_id]
            if not isinstance(listing, ShareListing) and not isinstance(listing.house, SocialHouse):
                new_value = round(LIST_PRICE_UPDATE_FACTOR * listing.value)
                self.listings[house_id] = listing._replace(value=new_value)

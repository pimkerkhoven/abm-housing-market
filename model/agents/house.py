from model.agents.agent import Agent
from model.constants import WEALTH_BIDDING_PORTION
from model.util.contracts import BuyingContract, RentalContract
from model.util.injector import inject


class House(Agent):
    def __init__(self, size, quality):
        super().__init__()
        self.size = size
        self.quality = quality

    def __repr__(self):
        return "{}({}, {}, {})".format(type(self).__name__, self.id,
                                       self.size, self.quality)


class BuyHouse(House):
    def __init__(self, size, quality, owner=None):
        super().__init__(size, quality)
        self.owner = owner

    @inject("buying_market")
    def list(self, buying_market):
        buying_market.list(self)

    def move_out(self, _to, _by):
        self.list()

    @inject("buying_market", "bank")
    def move_in(self, buyer, buying_market, bank, log_transaction=True):
        wait_time = buyer.contract.want_to_move_time if buyer.contract.want_to_move else -1

        listing = buying_market.listings[self.id]
        mortgage_value, monthly_payment = bank.value_to_monthly_payment(listing.value, buyer, buying=True)

        new_contract = BuyingContract(monthly_payment, self, mortgage_value)

        if self.owner:
            self.owner.sell(listing.value)

        buyer.set_contract(new_contract)
        if buyer.wealth > 0:
            buyer.wealth = round((1 - WEALTH_BIDDING_PORTION) * buyer.wealth)
        self.owner = buyer

        buying_market.transact(self.id, buyer.id, wait_time, log_transaction=log_transaction)


class RentalHouse(House):
    def __init__(self, size, quality, renter=None):
        super().__init__(size, quality)
        self.renter = renter

    @inject("rental_market")
    def list(self, rental_market):
        rental_market.list(self)

    def move_out(self, to, by):
        self.list()
        self.renter = None

        if to is not None:
            to.move_in(by, )

    @inject("rental_market")
    def move_in(self, renter, rental_market, log_transaction=True):
        wait_time = renter.contract.want_to_move_time if renter.contract.want_to_move else -1

        listing = rental_market.listings[self.id]
        contract = RentalContract(listing.value, self)
        renter.set_contract(contract)
        self.renter = renter

        rental_market.transact(self.id, renter.id, wait_time, log_transaction=log_transaction)


class SocialHouse(House):
    def __init__(self, rental_house, value, renter=None):
        super().__init__(rental_house.size, rental_house.quality)
        self.id = rental_house.id
        self.renter = renter

        self.value = value
        self.interested = []

    @inject("rental_market")
    def list(self, rental_market):
        rental_market.list_social_house(self)

    def move_out(self, to, by):
        self.list()
        self.renter = None

        # handles dying
        if to is not None:  # and by is not None:
            to.move_in(by)

    def show_interest(self, by):
        self.interested.append(by)

    @inject("rental_market")
    def move_in(self, renter, rental_market, log_transaction=True):
        wait_time = renter.contract.want_to_move_time if renter.contract.want_to_move else -1

        renter.contract.house.move_out(None, renter)

        contract = RentalContract(self.value, self)
        renter.set_contract(contract)
        self.renter = renter

        self.interested = []

        rental_market.transact(self.id, renter.id, wait_time, log_transaction=log_transaction)


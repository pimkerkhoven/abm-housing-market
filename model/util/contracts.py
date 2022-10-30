class BuyingContract:
    def __init__(self, cost, house, mortgage_remaining):
        self.run_time = 0
        self._cost = cost
        self.house = house
        self.mortgage_remaining = mortgage_remaining
        self.want_to_move = False
        self.want_to_move_time = 0

    def update(self, months_passed=1):
        self.run_time += months_passed
        self.mortgage_remaining -= self._cost * months_passed
        self.mortgage_remaining = max(0, self.mortgage_remaining)

        if self.want_to_move:
            self.want_to_move_time += 1

        if self.mortgage_remaining <= 0:
            self._cost = 0

    def get_costs(self):
        return self._cost

    def to_record(self):
        return "Buy", self.mortgage_remaining, self.house.size, self.house.quality, self.house.id, type(self.house).__name__

    def __repr__(self):
        return "BuyingContract({}, {}, {}, {}, {})".format(self.run_time, self.get_costs(), self.house.id,
                                                           self.mortgage_remaining, self.want_to_move)


class RentalContract:
    def __init__(self, cost, house):
        self.run_time = 0
        self._cost = cost
        self.house = house
        self.want_to_move = False
        self.want_to_move_time = 0

    def update(self, months_passed=1):
        self.run_time += months_passed

        if self.want_to_move:
            self.want_to_move_time += 1

    def get_costs(self):
        return self._cost

    def to_record(self):
        return "Rent", self.get_costs(), self.house.size, self.house.quality, self.house.id, type(self.house).__name__

    def __repr__(self):
        return "RentalContract({}, {}, {}, {})".format(self.run_time, self.get_costs(), self.house.id,
                                                       self.want_to_move)


class NoHouse:
    def __init__(self):
        self.id = -1
        self.size = 0
        self.quality = 0

    def list(self):
        pass

    def move_out(self, to, by):
        if to is not None:
            to.move_in(by, )

    def move_in(self, by):
        if not by.contract.house == self:
            by.assign_homelessness()

    def to_record(self):
        return "Homeless",

    def __repr__(self):
        return "NoHouse"


THE_NO_HOUSE = NoHouse()


class Homeless:
    def __init__(self):
        self.run_time = 0
        self._cost = 0
        self.house = THE_NO_HOUSE
        self.want_to_move = True
        self.want_to_move_time = 0

    def update(self, months_passed=1):
        self.run_time += months_passed

        if self.want_to_move:
            self.want_to_move_time += 1

    def get_costs(self):
        return self._cost

    def __repr__(self):
        return "Homeless({}, {}, {}, {})".format(self.run_time, self._cost, self.house,
                                                     self.want_to_move)

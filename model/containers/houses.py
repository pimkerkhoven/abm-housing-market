import math
import random

from scipy.stats import skewnorm

from model.agents.house import RentalHouse, BuyHouse
from model.constants import MIN_HOUSE_SIZE, MAX_HOUSE_SIZE, MIN_HOUSE_QUALITY, \
    MAX_HOUSE_QUALITY
from model.containers.agent_container import AgentContainer
from model.util.injector import inject


def uniform_new_house_size_distribution():
    return min(MAX_HOUSE_SIZE, max(MIN_HOUSE_SIZE, skewnorm.rvs(4.5, loc=80, size=1, scale=80)[0]))


def uniform_new_house_quality_distribution():
    return random.randint(MIN_HOUSE_QUALITY, MAX_HOUSE_QUALITY)


class Houses(AgentContainer):
    @inject("rules")
    def __init__(self, rules):
        super().__init__()

        self.percentage_for_rent = rules.construction['percentage_for_rent']

        self.size_distribution = rules.construction['size_distribution'] \
            if "size_distribution" in rules.construction \
            else uniform_new_house_size_distribution

        self.quality_distribution = rules.construction['quality_distribution'] \
            if "quality_distribution" in rules.construction \
            else uniform_new_house_quality_distribution

        self.target_shortage = rules.construction['target_shortage']
        self.max_build_limit = rules.construction['max_build_limit']

    @inject("households", "run_settings")
    def construct(self, households, run_settings):
        # if year < 2035:
        #     x = year - START_YEAR
        #     target_shortage = ((-1 / 72) * x ** 2) + (1 / 3) * x + 2
        #     target_shortage /= 100
        # else:
        target_shortage = self.target_shortage

        current_shortage = self.calculate_housing_shortage()

        if current_shortage > target_shortage:
            to_construct = (1 - target_shortage) * len(households) - self.count_houses()
            # to_construct = min(to_construct, math.ceil(self.max_build_limit / run_settings.scale_factor))
            to_construct = math.floor(to_construct)
        else:
            to_construct = 0

        # print(year, ":", to_construct * run_settings.scale_factor, ",")

        for _ in range(to_construct):
            new_house = self.get_new_house()
            self.add(new_house)
            new_house.list()

    @inject("households")
    def calculate_housing_shortage(self, households):
        return (len(households) - self.count_houses()) / len(households)

    def count_houses(self):
        return len(self)

    def get_new_house(self):
        size = self.size_distribution()
        quality = self.quality_distribution()

        if random.random() <= self.percentage_for_rent:
            return RentalHouse(size, quality)

        return BuyHouse(size, quality)
